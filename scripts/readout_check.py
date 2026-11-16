"""Does the "Answer:" prefix readout (dev-3) give the same preferences as reading the
first reply token (dev-1)?

Two models were run both ways on the same dev pairs: all dev pairs with dev-1
(runs/dev, Gate 1) and the pilot subset with dev-3 (runs/pilot). Single trials are
dominated by position and label bias, which the readout can change, so the fair
comparison is at the pair level, after the four counterbalanced presentations
have been averaged.

    uv run python scripts/readout_check.py
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from aesx import analysis
from aesx.effects import manifest_table
from aesx.manifest import ROOT


def main() -> int:
    meta = manifest_table("dev")[["pair_id", "kind"]]
    print(f"{'model':16s} {'layout':6s} {'framing':7s} {'pairs':>5s} {'r(pref)':>8s} {'same choice':>12s} "
          f"{'bias dev-1':>10s} {'bias dev-3':>10s}")
    for model in ("smolvlm2-500m", "qwen3.5-0.8b"):
        a = analysis.prefer_by_pair(analysis.load_results(ROOT / "runs" / "dev" / model / "results.jsonl")).merge(meta, on="pair_id")
        b = analysis.prefer_by_pair(analysis.load_results(ROOT / "runs" / "pilot" / model / "results.jsonl")).merge(meta, on="pair_id")
        m = a.merge(b, on=["pair_id", "layout", "framing", "experiment", "kind"], suffixes=("_1", "_3"))
        for (layout, framing), g in m.groupby(["layout", "framing"], sort=False):
            x = g[g.kind == "manipulation"]
            ident = g[g.kind == "identical"]
            r = np.corrcoef(x.pref_1, x.pref_3)[0, 1]
            same = float((x.choice_ref_1 == x.choice_ref_3).mean())
            print(f"{model:16s} {layout:6s} {framing:7s} {len(x):5d} {r:8.2f} {same:12.2f} "
                  f"{ident.pos_bias_1.mean():10.2f} {ident.pos_bias_3.mean():10.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
