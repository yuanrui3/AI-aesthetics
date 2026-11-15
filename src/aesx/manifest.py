"""Pair manifests: the committed record from which every stimulus can be rebuilt.

A *pair* is a reference composition and its manipulated twin. PNGs are
git-ignored; the manifest (seed, parameters, SHA-256 of both files) is committed,
so a rebuild can be verified bit for bit.
"""
from __future__ import annotations

import hashlib
import json
import zlib
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPLITS = {"dev": 0, "test": 1}


def rng_for(experiment: str, split: str, index: int) -> np.random.Generator:
    """Independent, reproducible stream per (experiment, split, pair index).

    Dev and test streams never overlap, so nothing tuned on dev stimuli can
    have seen a test stimulus.
    """
    return np.random.default_rng(np.random.SeedSequence([zlib.crc32(experiment.encode()), SPLITS[split], index]))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@dataclass
class Pair:
    experiment: str
    pair_id: str
    split: str  # "dev" | "test"
    index: int  # seed index within (experiment, split)
    kind: str  # "manipulation" | "identical"
    condition: str  # experiment-specific cell label, e.g. "inward_vs_outward"
    ref: str  # path relative to project root
    alt: str
    ref_sha256: str = ""
    alt_sha256: str = ""
    # Signed size of the manipulation where it has one (balance-score difference,
    # shift distance...). Sign convention is documented per experiment.
    dose: float | None = None
    # Which member people chose more often in the source paper:
    # "ref", "alt", or "none" for a published null / an identical-pair control.
    human_direction: str = "none"
    # Bootstrap unit. Pairs that share images (e.g. all pairs built from one set of
    # elements) share a cluster and are resampled together. Defaults to the pair itself.
    cluster: str = ""
    params: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.cluster:
            self.cluster = self.pair_id


def save_pair(pair: Pair, ref_im: Image.Image, alt_im: Image.Image) -> Pair:
    for rel, im in ((pair.ref, ref_im), (pair.alt, alt_im)):
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        im.save(p, format="PNG", optimize=False)
    pair.ref_sha256 = sha256_file(ROOT / pair.ref)
    pair.alt_sha256 = sha256_file(ROOT / pair.alt)
    return pair


def write_manifest(path: Path, pairs: list[Pair]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for p in pairs:
            f.write(json.dumps(asdict(p), sort_keys=True) + "\n")


def read_manifest(path: Path) -> list[Pair]:
    with Path(path).open(encoding="utf-8") as f:
        return [Pair(**json.loads(line)) for line in f if line.strip()]


def verify_manifest(path: Path) -> list[str]:
    """Return the pair_ids whose files are missing or differ from the recorded hash."""
    bad = []
    for p in read_manifest(path):
        for rel, want in ((p.ref, p.ref_sha256), (p.alt, p.alt_sha256)):
            f = ROOT / rel
            if not f.exists() or sha256_file(f) != want:
                bad.append(p.pair_id)
                break
    return bad
