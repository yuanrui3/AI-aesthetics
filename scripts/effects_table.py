"""Model effects for every experiment, layout and framing, beside the human figure.

    uv run python scripts/effects_table.py --split dev                 # all models with a run
    uv run python scripts/effects_table.py --split dev --model qwen3.5-0.8b --layout two
    -> reports/effects_<split>.csv  (and a printed summary)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import warnings

import pandas as pd

warnings.simplefilter("ignore", RuntimeWarning)  # empty bootstrap cells return nan by design

from aesx import analysis
from aesx.effects import EFFECT_FUNCS, manifest_table
from aesx.manifest import ROOT


def human_effects() -> dict[tuple[str, str], dict]:
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "human_effects.py"), "--json"],
                         capture_output=True, text=True, check=True).stdout
    return {(e["experiment"], e["key"]): e for e in json.loads(out)}


def model_effects(run_path, meta: pd.DataFrame) -> pd.DataFrame:
    df = analysis.load_results(run_path)
    rows = []
    for task in ("prefer", "weight"):
        if not (df.task == task).any():
            continue
        pp = analysis.prefer_by_pair(df, task).merge(meta, on="pair_id")
        for (layout, framing), d in pp.groupby(["layout", "framing"], sort=False):
            for exp, fn in EFFECT_FUNCS.items():
                if not (d.experiment == exp).any():
                    continue
                if exp == "colour":
                    res = fn(d, task)
                elif task == "prefer":
                    res = fn(d)
                else:
                    continue
                for r in res:
                    rows.append({"layout": layout, "framing": framing, "task": task, **r})
    return pd.DataFrame(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev")
    ap.add_argument("--model", default=None)
    ap.add_argument("--layout", default=None)
    a = ap.parse_args()

    meta = manifest_table(a.split)
    human = human_effects()
    frames = []
    for run in sorted((ROOT / "runs" / a.split).glob("*/results.jsonl")):
        if a.model and run.parent.name != a.model:
            continue
        t = model_effects(run, meta)
        t.insert(0, "model", run.parent.name)
        frames.append(t)
    if not frames:
        print("no runs found")
        return 1
    t = pd.concat(frames, ignore_index=True)
    # Model keys whose human counterpart is stored under a different key in human_effects.py.
    alias = {("apb", "r_apb_circles"): "e2_circles", ("apb", "r_apb_hexagons"): "e2_hexagons",
             ("apb", "r_apb_all"): "hf_e2_all"}
    t["human"] = [human.get((e, alias.get((e, k), k)), {}).get("estimate") for e, k in zip(t.experiment, t.key)]
    (ROOT / "reports").mkdir(exist_ok=True)
    t.to_csv(ROOT / "reports" / f"effects_{a.split}.csv", index=False, float_format="%.4f")

    show = t if not a.layout else t[t.layout == a.layout]
    for (model, layout, framing, task), g in show.groupby(["model", "layout", "framing", "task"], sort=False):
        print(f"\n=== {model} | layout {layout} | framing {framing} | question {task}")
        for _, r in g.iterrows():
            h = "" if pd.isna(r.human) else f"   human {r.human:+.3f}"
            print(f"  {r.experiment:11s} {r.estimate:+.3f} [{r.lo:+.3f}, {r.hi:+.3f}]  n={r.n:<4d} {r.label}{h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
