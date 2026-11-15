"""End-to-end check of trials -> runner -> analysis with a fake model.

The fake model has a known position bias, a known label bias and a known
preference for the reference image. The analysis must recover all three, and
the bias-cancelled preference must be unaffected by the biases.

Run:  uv run python tests/test_plumbing.py
"""
from __future__ import annotations

import math
import shutil
import sys
from pathlib import Path

import numpy as np

from aesx import analysis, runner
from aesx.manifest import ROOT, Pair, read_manifest, rng_for, save_pair, verify_manifest, write_manifest
from aesx.render import Canvas
from aesx.trials import build_trials

TMP = ROOT / ".cache" / "test_plumbing"
POS, LABEL, PREF = 1.5, 0.4, 0.3  # log-odds: toward first image, toward letter A, toward the reference


class FakeScorer:
    spec = {"name": "fake"}

    def score(self, trial, images):
        assert len(images) == (1 if trial.layout == "sbs" else 2)
        if trial.task == "samediff":
            differs = trial.image_paths[0] != trial.image_paths[1]
            says_diff = 2.0 if differs else -2.0
            lo_yes = (says_diff if trial.framing == "different" else -says_diff) + 0.7  # +0.7 = yes-bias
            return _pack(lo_yes)
        lo_first = POS + (LABEL if trial.labels[0] == "A" else -LABEL)
        if trial.image_paths[0] != trial.image_paths[1]:
            lo_first += PREF if trial.first == "ref" else -PREF
        return _pack(lo_first)


def _pack(lo_first: float) -> dict:
    p = 1 / (1 + math.exp(-lo_first))
    return {"lp_first": math.log(p), "lp_second": math.log(1 - p), "mass": 1.0}


def make_pairs(n: int = 12) -> list[Pair]:
    pairs = []
    for i in range(n):
        rng = rng_for("plumbing", "dev", i)
        x, y, r = rng.uniform(60, 140), rng.uniform(60, 140), rng.uniform(15, 40)
        ref, alt = Canvas(200, 200), Canvas(200, 200)
        ref.circle(x, y, r, (0, 0, 0))
        alt.circle(200 - x, y, r, (0, 0, 0))
        ident = i % 3 == 0
        p = Pair("plumbing", f"plumbing-dev-{i:04d}", "dev", i, "identical" if ident else "manipulation", "c",
                 f".cache/test_plumbing/stim/{i:04d}_ref.png",
                 f".cache/test_plumbing/stim/{i:04d}_ref.png" if ident else f".cache/test_plumbing/stim/{i:04d}_alt.png")
        pairs.append(save_pair(p, ref.image(), ref.image() if ident else alt.image()))
    return pairs


def main() -> int:
    shutil.rmtree(TMP, ignore_errors=True)
    pairs = make_pairs()
    write_manifest(TMP / "pairs.jsonl", pairs)
    assert verify_manifest(TMP / "pairs.jsonl") == []
    assert make_pairs()[3].ref_sha256 == pairs[3].ref_sha256, "stimuli are not reproducible"

    trials = build_trials(read_manifest(TMP / "pairs.jsonl"))
    n_manip = sum(p.kind == "manipulation" for p in pairs)
    n_ident = len(pairs) - n_manip
    # per layout: manipulation 2 orders x 2 labelings, identical 1 x 2; prefer x2 framings, samediff x2 polarities
    assert len(trials) == 2 * (n_manip * 4 + n_ident * 2) * (2 + 2), len(trials)
    assert len({t.trial_id for t in trials}) == len(trials)

    half = trials[: len(trials) // 2]
    runner.run(half, FakeScorer(), TMP / "run")  # interrupted run...
    runner.run(trials, FakeScorer(), TMP / "run")  # ...resumes without redoing
    df = analysis.load_results(TMP / "run" / "results.jsonl")
    assert len(df) == len(trials)

    pp = analysis.prefer_by_pair(df)
    manip = pp[~pp.pair_id.isin([p.pair_id for p in pairs if p.kind == "identical"])]
    ident = pp[pp.pair_id.isin([p.pair_id for p in pairs if p.kind == "identical"])]
    assert np.allclose(manip.pref, PREF), manip.pref.unique()
    assert np.allclose(pp.pos_bias, POS) and np.allclose(pp.label_bias, LABEL)
    assert np.allclose(ident.pref, POS)  # identical pairs: "ref first" always, so pref == position bias
    assert (manip.choice_ref == 1).all()
    # Raw trials look like chance (position bias swamps preference); the cancelled choice does not.
    assert np.allclose(manip.p_ref_hard, 0.5)

    sd = analysis.samediff_by_pair(df)
    is_ident = sd.pair_id.isin([p.pair_id for p in pairs if p.kind == "identical"])
    assert np.allclose(sd[~is_ident]["diff"], 2.0) and np.allclose(sd[is_ident]["diff"], -2.0)
    assert np.allclose(sd.yes_bias, 0.7)
    assert analysis.auc(sd[~is_ident]["diff"].values, sd[is_ident]["diff"].values) == 1.0
    print("plumbing OK:", len(trials), "trials;", "pref", PREF, "pos", POS, "label", LABEL, "all recovered")
    shutil.rmtree(TMP, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
