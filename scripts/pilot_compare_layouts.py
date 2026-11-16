"""Headline pilot statistics in both layouts, side by side (dev stimuli).

    uv run python scripts/pilot_compare_layouts.py [--framing you|most]
"""
from __future__ import annotations

import sys

import pandas as pd

from aesx.manifest import ROOT

KEYS = [("apb", "r_apb_all"), ("apb", "p_balanced"), ("multiobject", "p_balanced"), ("framing", "p_inward"),
        ("framing", "p_centre"), ("colour", "weight_red_vs_yellow_anchor"), ("colour", "prefer_red_vs_yellow_anchor"),
        ("proportion", "p_less_altered")]


def main() -> int:
    framing = sys.argv[sys.argv.index("--framing") + 1] if "--framing" in sys.argv else "you"
    e = pd.read_csv(ROOT / "reports" / "effects_pilot.csv")
    lay = pd.read_csv(ROOT / "reports" / "gate2_layout.csv")
    order = ["smolvlm2-500m", "qwen3.5-0.8b", "minicpm-v-4.7-1b", "smolvlm2-2.2b", "internvl3.5-2b",
             "north-micro-vision", "qwen3.5-4b", "gemma-4-e2b"]
    for exp, key in KEYS:
        print(f"\n{exp}.{key}   (framing {framing if not key.startswith('weight') else 'plain'})")
        for m in order:
            cells = []
            for layout in ("two", "sbs"):
                fr = "plain" if key.startswith("weight") else framing
                r = e[(e.model == m) & (e.layout == layout) & (e.framing == fr) & (e.experiment == exp) & (e.key == key)]
                vis = lay[(lay.model == m) & (lay.layout == layout)].iloc[0][f"auc_{exp}"]
                cells.append("n/a" if r.empty else f"{r.iloc[0].estimate:+.2f} [{r.iloc[0].lo:+.2f},{r.iloc[0].hi:+.2f}] vis {vis:.2f}")
            print(f"  {m:20s} two: {cells[0]:34s} sbs: {cells[1]}")
    print("\nsigned position bias (mean log-odds toward first/left on identical pairs):")
    for m in order:
        a, b = (lay[(lay.model == m) & (lay.layout == l)].iloc[0] for l in ("two", "sbs"))
        print(f"  {m:20s} two {a.pos_bias_mean_signed:+.2f}   sbs {b.pos_bias_mean_signed:+.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
