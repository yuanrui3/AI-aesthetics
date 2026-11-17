"""Wording check (exploratory): does each model's effect survive a rewording of the question?

    uv run python scripts/wording_check.py run qwen3.5-0.8b        # one model -> runs/wording/<model>
    uv run python scripts/wording_check.py run --all               # the seven frozen models, one at a time
    uv run python scripts/wording_check.py report                  # -> reports/wording_check.csv and .md

Design, statistics and decision rules are fixed in PLAN.md ("Wording check"). Dev pairs of
E1 to E3, two-image layout, both framings, four wordings of the preference question. Only
the question sentence changes; everything else is the frozen v1 trial. The frozen code is
imported, never edited: the trials are built by `aesx.trials.build_trials` and then only the
question at the start of the last text segment is swapped. Resumable like the main run.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import warnings
from dataclasses import replace

import numpy as np
import pandas as pd

from aesx import analysis, runner
from aesx.effects import _ci, _draws, framing_effects, manifest_table, multiobject_effects, apb_effects
from aesx.manifest import ROOT, read_manifest
from aesx.trials import PREFER_Q, PROMPT_VERSION, build_trials

warnings.simplefilter("ignore", RuntimeWarning)

EXPERIMENTS = ("apb", "multiobject", "framing")
TAG = "wording"
WORDINGS = {  # key -> question per framing; None = the frozen v1 question, unchanged
    "pleasing": None,
    "like": {"you": "Which of these two images do you like more?",
             "most": "Which of these two images would most people like more?"},
    "beautiful": {"you": "Which of these two images do you find more beautiful?",
                  "most": "Which of these two images would most people find more beautiful?"},
    "prefer": {"you": "Which of these two images do you prefer?",
               "most": "Which of these two images would most people prefer?"},
}
# The headline statistic per experiment and its null value (PLAN.md).
HEADLINE = {"apb": ("r_apb_all", 0.0), "multiobject": ("p_balanced", 0.5), "framing": ("p_inward", 0.5)}
FUNCS = {"apb": apb_effects, "multiobject": multiobject_effects, "framing": framing_effects}


def version(w: str) -> str:
    return PROMPT_VERSION if WORDINGS[w] is None else f"{PROMPT_VERSION}-{w}"


def wording_trials(experiments=EXPERIMENTS) -> list:
    base = []
    for exp in experiments:
        base += build_trials(read_manifest(ROOT / "stimuli" / exp / "dev" / "pairs.jsonl"),
                             tasks=("prefer",), layouts=("two",))
    out = []
    for w, qs in WORDINGS.items():
        for t in base:
            segs = [list(s) for s in t.segments]
            if qs is not None:
                old, last = PREFER_Q[t.framing], segs[-1]
                if last[0] != "text" or not last[1].startswith(old):
                    raise RuntimeError(f"unexpected trial text in {t.trial_id}: {last}")
                last[1] = qs[t.framing] + last[1][len(old):]
            out.append(replace(t, trial_id=f"{t.trial_id}|w={w}", segments=segs, prompt_version=version(w)))
    return out


# ------------------------------------------------------------------ running
def run_one(model: str, tag: str, limit: int | None) -> int:
    from aesx.models import registry

    trials = wording_trials()
    if limit:
        step = max(1, len(trials) // limit)
        trials = trials[::step][:limit]
    print(f"{len(trials)} trials, {len(WORDINGS)} wordings", flush=True)
    scorer = registry.load(model)
    print("loaded", scorer.spec, flush=True)
    run_dir = ROOT / "runs" / tag / model
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    runner.run(trials, scorer, run_dir, meta={"split": "dev", "tag": tag, "check": "wording",
                                              "wordings": {w: version(w) for w in WORDINGS}, "head_at_run": head})
    return 0


def run_all(tag: str) -> int:
    frozen = json.loads((ROOT / "FROZEN.json").read_text(encoding="utf-8"))
    failed, t0 = [], time.time()
    for m in frozen["models"]:
        d = ROOT / "runs" / tag / m
        d.mkdir(parents=True, exist_ok=True)
        with (d / "log.txt").open("a", encoding="utf-8") as log:
            print(f"[{(time.time() - t0) / 60:6.1f} min] start {m}", flush=True)
            rc = subprocess.run([sys.executable, __file__, "run", m, "--tag", tag], stdout=log,
                                stderr=subprocess.STDOUT, cwd=ROOT).returncode
        print(f"[{(time.time() - t0) / 60:6.1f} min] done  {m}  exit {rc}", flush=True)
        if rc:
            failed.append(m)
    print(f"all done in {(time.time() - t0) / 60:.1f} min; failed: {failed or 'none'}", flush=True)
    return 1 if failed else 0


# ------------------------------------------------------------------ report
def classify(rows: pd.DataFrame, null: float) -> str:
    above, below = (rows.lo > null).sum(), (rows.hi < null).sum()
    if len(rows) < len(WORDINGS) or rows[["lo", "hi"]].isna().any().any():
        return "incomplete"
    if above == len(rows) or below == len(rows):
        return "consistent"
    if above and below:
        return "reversed"
    if above + below == 0:
        return "null throughout"
    return "mixed"


def pos_bias(pp: pd.DataFrame) -> tuple[float, float, float]:
    v = pp[pp.kind == "identical"].pos_bias.values
    if len(v) < 2:
        return (float(np.mean(v)) if len(v) else np.nan, np.nan, np.nan)
    return _ci(float(v.mean()), v[_draws(len(v), 0)].mean(axis=1))


def report(tag: str) -> int:
    meta = manifest_table("dev")
    human = {}
    try:
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "human_effects.py"), "--json"],
                             capture_output=True, text=True, check=True).stdout
        human = {(e["experiment"], e["key"]): e.get("estimate") for e in json.loads(out)}
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        pass
    alias = {("apb", "r_apb_all"): "hf_e2_all"}
    rows, agree, repeat = [], [], []
    for run in sorted((ROOT / "runs" / tag).glob("*/results.jsonl")):
        model = run.parent.name
        df = analysis.load_results(run)
        pps = {}
        for w in WORDINGS:
            dw = df[df.prompt_version == version(w)]
            if dw.empty:
                continue
            pp = analysis.prefer_by_pair(dw).merge(meta, on="pair_id")
            pps[w] = pp
            for fr, d in pp.groupby("framing"):
                for exp, (key, null) in HEADLINE.items():
                    if not (d.experiment == exp).any():
                        continue
                    try:
                        hit = [r for r in FUNCS[exp](d) if r["key"] == key]
                    except ValueError:  # incomplete design (a partial or smoke-test run)
                        hit = []
                    if hit:
                        r = hit[0]
                        rows.append({"model": model, "experiment": exp, "framing": fr, "wording": w, "key": key,
                                     "estimate": r["estimate"], "lo": r["lo"], "hi": r["hi"], "n": r["n"], "null": null,
                                     "human": human.get((exp, alias.get((exp, key), key)))})
                    b = pos_bias(d[d.experiment == exp])
                    rows.append({"model": model, "experiment": exp, "framing": fr, "wording": w, "key": "pos_bias",
                                 "estimate": b[0], "lo": b[1], "hi": b[2], "n": int((d[d.experiment == exp].kind == "identical").sum()),
                                 "null": 0.0, "human": None})
        # pair-level agreement with the frozen wording
        if "pleasing" in pps:
            base = pps["pleasing"][["pair_id", "framing", "experiment", "kind", "pref"]]
            for w, pp in pps.items():
                if w == "pleasing":
                    continue
                m = base.merge(pp[["pair_id", "framing", "pref"]], on=["pair_id", "framing"], suffixes=("_v1", "_w"))
                m = m[m.kind == "manipulation"]
                for (exp, fr), g in m.groupby(["experiment", "framing"]):
                    agree.append({"model": model, "experiment": exp, "framing": fr, "wording": w, "n_pairs": len(g),
                                  "r_pair_pref": float(np.corrcoef(g.pref_v1, g.pref_w)[0, 1]) if len(g) > 2 else np.nan})
        # repeatability: frozen-wording trials that repeat pilot trials exactly
        pilot = ROOT / "runs" / "pilot" / model / "results.jsonl"
        if pilot.exists():
            p = analysis.load_results(pilot)
            p = p[p.task == "prefer"][["trial_id", "lo_first"]]
            w = df[df.prompt_version == version("pleasing")][["trial_id", "lo_first"]].copy()
            w["trial_id"] = w.trial_id.str.replace("|w=pleasing", "", regex=False)
            m = p.merge(w, on="trial_id", suffixes=("_pilot", "_now"))
            if len(m):
                dlo = (m.lo_first_now - m.lo_first_pilot).abs()
                repeat.append({"model": model, "n_trials": len(m), "max_abs_diff_logodds": float(dlo.max()),
                               "median_abs_diff_logodds": float(dlo.median()),
                               "choice_flips": int(((m.lo_first_now > 0) != (m.lo_first_pilot > 0)).sum())})
    if not rows:
        print("no wording runs found")
        return 1
    t = pd.DataFrame(rows)
    (ROOT / "reports").mkdir(exist_ok=True)
    t.to_csv(ROOT / "reports" / "wording_check.csv", index=False, float_format="%.4f")
    a = pd.DataFrame(agree)
    r = pd.DataFrame(repeat)
    write_md(t, a, r)
    print(f"{len(t)} rows -> reports/wording_check.csv, reports/wording_check.md")
    return 0


def write_md(t: pd.DataFrame, a: pd.DataFrame, r: pd.DataFrame) -> None:
    order = list(WORDINGS)
    lines = ["# Wording check (exploratory, dev pairs)", "",
             "Generated by `scripts/wording_check.py report`. Design and rules: `PLAN.md`, \"Wording check\". "
             "Each cell is the estimate with its 95% bootstrap interval over stimuli. Wordings: "
             + "; ".join(f"`{w}`" for w in order) + ".", ""]
    head = t[t.key != "pos_bias"]
    for fr in ("you", "most"):
        lines += [f"## Headline statistics, \"{fr}\" framing", "",
                  "| Model | Experiment | " + " | ".join(order) + " | Spread | Human | Gap, pleasing to human | Direction |",
                  "|---|---|" + "---|" * len(order) + "---|---|---|---|"]
        for (model, exp), g in head[head.framing == fr].groupby(["model", "experiment"], sort=False):
            g = g.set_index("wording").reindex(order)
            cells = [("" if pd.isna(x.estimate) else f"{x.estimate:.2f} [{x.lo:.2f}, {x.hi:.2f}]") for _, x in g.iterrows()]
            spread = g.estimate.max() - g.estimate.min()
            hum = pd.to_numeric(g.human, errors="coerce").dropna()
            hum_s = f"{hum.iloc[0]:.2f}" if len(hum) else "none"
            gap = abs(g.estimate.get("pleasing") - hum.iloc[0]) if len(hum) and pd.notna(g.estimate.get("pleasing")) else None
            gap_s = "" if gap is None else f"{gap:.2f}"
            lines.append(f"| {model} | {exp} ({g.key.dropna().iloc[0]}) | " + " | ".join(cells)
                         + f" | {spread:.2f} | {hum_s} | {gap_s} | {classify(g.dropna(subset=['estimate']).reset_index(), g['null'].dropna().iloc[0])} |")
        lines.append("")
    pb = t[(t.key == "pos_bias") & (t.framing == "you")]
    lines += ["## Position bias on identical pairs, \"you\" framing (log-odds of naming the first image)", "",
              "| Model | Experiment | " + " | ".join(order) + " |", "|---|---|" + "---|" * len(order)]
    for (model, exp), g in pb.groupby(["model", "experiment"], sort=False):
        g = g.set_index("wording").reindex(order)
        lines.append(f"| {model} | {exp} | " + " | ".join("" if pd.isna(x) else f"{x:+.2f}" for x in g.estimate) + " |")
    lines.append("")
    if len(a):
        lines += ["## Pair-level agreement with the frozen wording (r of pair log-odds, changed pairs)", "",
                  "| Model | Experiment | Framing | " + " | ".join(order[1:]) + " |", "|---|---|---|" + "---|" * (len(order) - 1)]
        for (model, exp, fr), g in a.groupby(["model", "experiment", "framing"], sort=False):
            g = g.set_index("wording").reindex(order[1:])
            lines.append(f"| {model} | {exp} | {fr} | " + " | ".join("" if pd.isna(x) else f"{x:.2f}" for x in g.r_pair_pref) + " |")
        lines.append("")
    if len(r):
        lines += ["## Repeatability against the pilot (identical trials, scored again)", "",
                  "| Model | Trials | Largest difference (log-odds) | Median difference | Choices flipped |", "|---|---|---|---|---|"]
        for _, x in r.iterrows():
            lines.append(f"| {x.model} | {x.n_trials} | {x.max_abs_diff_logodds:.4f} | {x.median_abs_diff_logodds:.4f} | {x.choice_flips} |")
        lines.append("")
    (ROOT / "reports" / "wording_check.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("model", nargs="?")
    r.add_argument("--all", action="store_true", help="the seven frozen models, one at a time")
    r.add_argument("--tag", default=TAG)
    r.add_argument("--limit", type=int, default=None, help="smoke test: an even sample of N trials")
    p = sub.add_parser("report")
    p.add_argument("--tag", default=TAG)
    a = ap.parse_args()
    if a.cmd == "report":
        return report(a.tag)
    if a.all:
        return run_all(a.tag)
    if not a.model:
        ap.error("give a model or --all")
    return run_one(a.model, a.tag, a.limit)


if __name__ == "__main__":
    sys.exit(main())
