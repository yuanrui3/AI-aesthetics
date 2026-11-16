"""The freeze: what the test split may be generated and scored with.

FROZEN.json at the project root records the commit whose code generates and scores
the test stimuli, the prompt version, the models and the layouts. Every test-split
command calls ``require()``, which refuses to run if any file that determines a
stimulus, a trial or a score differs from that commit (committed or not).
"""
from __future__ import annotations

import json
import subprocess

from .manifest import ROOT

FROZEN_FILE = ROOT / "FROZEN.json"
# Everything that determines a test stimulus, a trial, or a model's score.
FROZEN_PATHS = (
    "src/aesx/balance.py", "src/aesx/grid.py", "src/aesx/icons.py", "src/aesx/manifest.py",
    "src/aesx/render.py", "src/aesx/runner.py", "src/aesx/subsets.py", "src/aesx/trials.py",
    "src/aesx/freeze.py", "src/aesx/experiments", "src/aesx/models",
    "scripts/make_stimuli.py", "scripts/run_model.py", "scripts/refusal_probe.py",
    "pyproject.toml", "uv.lock",
)


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def head() -> str:
    return _git("rev-parse", "HEAD").strip()


def uncommitted() -> list[str]:
    """Frozen paths with uncommitted changes (including untracked files)."""
    return [line[3:] for line in _git("status", "--porcelain", "--", *FROZEN_PATHS).splitlines() if line.strip()]


def changed_since(commit: str) -> list[str]:
    """Frozen paths that differ between ``commit`` and the working tree."""
    return [line for line in _git("diff", "--name-only", commit, "--", *FROZEN_PATHS).splitlines() if line.strip()]


def load() -> dict:
    if not FROZEN_FILE.exists():
        raise SystemExit("Refusing: no FROZEN.json. The test split is generated and run only after the freeze.")
    return json.loads(FROZEN_FILE.read_text(encoding="utf-8"))


def require() -> dict:
    """The frozen plan, or exit if the code has moved since the freeze."""
    frozen = load()
    changed = changed_since(frozen["commit"]) + uncommitted()
    if changed:
        raise SystemExit(f"Refusing: these files differ from the frozen commit {frozen['commit'][:10]}: "
                         + ", ".join(sorted(set(changed))))
    from .trials import PROMPT_VERSION

    if PROMPT_VERSION != frozen["prompt_version"]:
        raise SystemExit(f"Refusing: prompt version {PROMPT_VERSION} is not the frozen {frozen['prompt_version']}.")
    return frozen
