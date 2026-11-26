"""NVIDIA addendum report (PLAN.md: "NVIDIA addendum" and its five amendments).

    .\\.venv\\Scripts\\python.exe scripts/api_report.py --selftest   # simulated replies only: checks the pipeline
    .\\.venv\\Scripts\\python.exe scripts/api_report.py --final      # the addendum, once the owner says the run has stopped
    -> reports/nvidia_addendum.md and reports/nvidia_addendum.csv

Written on 2026-11-26, while the test run was still going and before any test reply had been read.
PLAN.md fixes what is computed. Where it leaves a detail open, the detail is fixed here, now:

- A presentation's k replies give lp = log((c + 1/2) / (k + 1)) for each answer and mass = the
  on-menu share. The existing analysis functions then run unchanged. A pair whose mean
  log-odds is exactly 0 counts as 1/2 (PLAN.md).
- P_cells for a subset is the number of on-menu replies naming the reference over all on-menu
  replies, across the subset's pairs, with the main analysis's cluster bootstrap. Off-menu
  replies are reported separately.
- A pair counts only if every one of its presentations has a reply (a complete pair).
  - Each model is analysed on all its complete pairs.
  - The two NVIDIA models are compared on the pairs complete for both.
  - Gemma 4 31B is compared with the local Gemma 4 E2B on Gemma 4 31B's complete pairs, paired
    by pair. The local model's P_cells is its mean two-letter probability for the reference
    over the same presentations.
- Refusal rule for API models: a model with more than a fifth of its preference replies
  off-menu is reported as refusing and is not scored.
- Predictions P2, P3, P4 and P6 use scripts/predictions.py's own functions and criteria, on the
  pre-registered sign statistic. That statistic is not comparable with the local models'
  (PLAN.md, first amendment), so the verdicts carry that label; strength comparisons use
  P_cells.
- P6 (the E1 balance correlation) needs every pair of an image family: 10 pairs among 5
  layouts. It uses only families with all 10 pairs complete, and is "not estimable" if there
  are none. The run takes pairs in one random order, so a part-done pass rarely completes a
  family. All other E1 measures use every complete pair.

The self-test simulates replies with known probabilities. Checked on 2026-11-26 over three
seeds of full passes: P_cells scatters around the true values on both sides, with no bias.
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
import tempfile
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import special

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aesx import analysis  # noqa: E402
from aesx import api_nvidia as api  # noqa: E402
from aesx.effects import _ci, _draws, boot_ratio, manifest_table  # noqa: E402
from aesx.manifest import ROOT  # noqa: E402
import predictions as pr  # noqa: E402
import run_api  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)

MODELS = ("gemma-4-31b", "nemotron-3.5-super-vl")
LOCAL_SIBLING = {"gemma-4-31b": "gemma-4-e2b"}  # same family, run locally in the main study
LOCAL_MODELS = ("qwen3.5-0.8b", "minicpm-v-4.7-1b", "smolvlm2-2.2b", "internvl3.5-2b",
                "north-micro-vision", "qwen3.5-4b", "gemma-4-e2b")
KEYS = ["experiment", "pair_id", "layout", "framing"]


# ------------------------------------------------------------------ subsets
def _flips(d):
    return (d.experiment == "framing") & (d.condition == "flip") & (d.p_pos_ref != 50)


def _ecc(d, which):
    f = d[_flips(d)]
    levels = sorted(f.dose.dropna().unique())
    if not levels:
        return pd.Series(False, index=d.index)
    return _flips(d) & (d.dose == (levels[0] if which == "near" else levels[-1]))


# (key, label, task, selector on per-pair rows of the "you" framing, human value, note on the human figure)
HEADLINE = [
    ("e1_p_balanced", "E1: P(more balanced chosen), all pairs", "prefer",
     lambda d: d.experiment == "apb", None, "people: ratings, r = -.74 to -.87 over images"),
    ("e2_p_balanced", "E2: P(balanced chosen), 90 px", "prefer",
     lambda d: (d.experiment == "multiobject") & (d.condition == "balance"), 0.528, "people: bars .48 to .56; P2 band .43-.57"),
    ("e3_p_inward", "E3: P(inward-facing chosen), off-centre flips", "prefer", _flips, 0.740, "people .74"),
    ("e3_p_inward_8", "E3: P(inward-facing chosen), 8% from centre", "prefer", lambda d: _ecc(d, "near"), 0.704, "people .70"),
    ("e3_p_inward_25", "E3: P(inward-facing chosen), 25% from centre", "prefer", lambda d: _ecc(d, "far"), 0.815, "people .82"),
    ("e3_p_centre", "E3: P(centre chosen over a quarter line), symmetrical objects", "prefer",
     lambda d: (d.experiment == "framing") & (d.condition == "centre") & (d.human_direction == "ref"), None,
     "people: centre preferred (direction only)"),
    ("e4_red_heavier", "E4 weight: P(red named heavier than yellow), small and medium", "weight",
     lambda d: (d.experiment == "colour") & (d.condition == "red_vs_yellow") & d.p_size_level.isin(["small", "medium"]),
     None, "people: red heavier (direction only)"),
    ("e5_p_less_altered", "E5: P(less altered grid chosen), all pairs", "prefer",
     lambda d: d.experiment == "proportion", None, "no human anchor for generated grids"),
]


# ------------------------------------------------------------------ data
def read_replies(path: Path) -> pd.DataFrame:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # a torn last line
    return pd.DataFrame(rows).drop_duplicates("trial_id", keep="last") if rows else pd.DataFrame()


def presentations(rep: pd.DataFrame) -> pd.DataFrame:
    """One row per presentation, in the format analysis.load_results produces."""
    a0, a1 = rep["answers"].str[0], rep["answers"].str[1]
    rep = rep.assign(cf=(rep["choice"] == a0).astype(int), cs=(rep["choice"] == a1).astype(int))
    g = rep.groupby("base_trial_id", sort=False)
    out = g[["pair_id", "experiment", "task", "framing", "layout", "first", "labels", "answers"]].first()
    out["k"], out["c_first"], out["c_second"] = g.size(), g["cf"].sum(), g["cs"].sum()
    out = out.reset_index().rename(columns={"base_trial_id": "trial_id"})
    out["lp_first"] = np.log((out.c_first + 0.5) / (out.k + 1))
    out["lp_second"] = np.log((out.c_second + 0.5) / (out.k + 1))
    out["mass"] = (out.c_first + out.c_second) / out.k
    out["lo_first"] = out.lp_first - out.lp_second
    out["off_menu"] = out.mass < analysis.OFF_MENU_MASS
    out["c_on"] = out.c_first + out.c_second
    out["c_ref"] = np.where(out["first"] == "ref", out.c_first, out.c_second)
    return out


def expected_trials(split: str) -> dict[str, set[str]]:
    exp: dict[str, set[str]] = {}
    for t in run_api.trials_for(split):
        exp.setdefault(t.pair_id, set()).add(t.trial_id)
    return exp


def complete_pairs(pres: pd.DataFrame, expected: dict[str, set[str]]) -> set[str]:
    have = pres.groupby("pair_id")["trial_id"].agg(set).to_dict()
    return {p for p, ids in expected.items() if ids <= have.get(p, set())}


def with_cells(pp: pd.DataFrame, pres: pd.DataFrame, task: str) -> pd.DataFrame:
    cells = pres[pres.task == task].groupby(KEYS).agg(num=("c_ref", "sum"), den=("c_on", "sum")).reset_index()
    pp = pp.merge(cells, on=KEYS, how="left")
    pp.loc[np.isclose(pp.pref, 0.0, atol=1e-12), "choice_ref"] = 0.5  # PLAN.md: a tie counts one half
    return pp


class APIModel(pr.Model):
    """predictions.Model built from sampled replies, restricted to complete pairs."""

    def __init__(self, name: str, pres: pd.DataFrame, meta: pd.DataFrame, pairs: set[str]):
        self.name = name
        df = pres[pres.pair_id.isin(pairs) & (pres.layout == pr.LAYOUT)].copy()
        self.pres = df
        self.pp = with_cells(analysis.prefer_by_pair(df).merge(meta, on="pair_id"), df, "prefer")
        self.pw = (with_cells(analysis.prefer_by_pair(df, "weight").merge(meta, on="pair_id"), df, "weight")
                   if (df.task == "weight").any() else None)
        self.sd = analysis.samediff_by_pair(df).merge(meta, on="pair_id")
        pref = df[df.task == "prefer"]
        self.offmenu = float(1 - pref.c_on.sum() / pref.k.sum()) if len(pref) else float("nan")
        self.refusal = {"refuses": self.offmenu}
        self._vis = {}
        # E1's scale values (P6) need every pair of a family: 10 pairs among 5 layouts. The run takes
        # pairs in one random order, so a part-done pass rarely completes a family.
        fam = meta[meta.pair_id.str.startswith("apb-") & (meta.kind == "manipulation")]
        self.e1_families = {f for f, ids in fam.groupby("p_family").pair_id if set(ids) <= pairs}


def p6_complete_families(mod: APIModel) -> list[dict]:
    """P6 on the E1 families whose 10 pairs are all complete; not estimable if there are none."""
    if not mod.e1_families:
        return [{"prediction": "P6", "part": "r(balance score, preference scale value)", "estimate": np.nan,
                 "lo": np.nan, "hi": np.nan, "verdict": "not estimable",
                 "note": "no E1 family has all 10 of its pairs complete"}]
    sub = copy.copy(mod)
    sub.pp = mod.pp[(mod.pp.experiment != "apb") | mod.pp.p_family.isin(mod.e1_families)]
    rows = pr.p6(sub)
    for r in rows:
        r["note"] = f"{len(mod.e1_families)} complete families; {r['note']}"
    return rows


def local_cells(model: str, meta: pd.DataFrame, task: str) -> pd.DataFrame:
    """A local model's per-pair P_cells parts: summed two-letter probability for the reference."""
    df = analysis.load_results(ROOT / "runs" / "test" / model / "results.jsonl")
    d = df[(df.task == task) & (df.layout == pr.LAYOUT)].copy()
    d["p"] = special.expit(np.where(d["first"] == "ref", d.lo_first, -d.lo_first))
    return d.groupby(KEYS).agg(num=("p", "sum"), den=("p", "size")).reset_index().merge(meta, on="pair_id")


def subset(frame: pd.DataFrame, select) -> pd.DataFrame:
    d = frame[(frame.framing.isin(["you", "plain"])) & (frame.kind == "manipulation")]
    return d[select(d)]


def paired_ratio_diff(a: pd.DataFrame, b: pd.DataFrame, seed: int = 0):
    """P_cells(a) - P_cells(b) on the pairs both have, resampling clusters jointly."""
    m = a[["pair_id", "cluster", "num", "den"]].merge(b[["pair_id", "num", "den"]], on="pair_id", suffixes=("_a", "_b"))
    if m.empty:
        return (np.nan,) * 3, 0
    codes, uniq = pd.factorize(m.cluster.values)
    k = len(uniq)
    na, da = np.bincount(codes, m.num_a, k), np.bincount(codes, m.den_a, k)
    nb, db = np.bincount(codes, m.num_b, k), np.bincount(codes, m.den_b, k)
    est = na.sum() / da.sum() - nb.sum() / db.sum()
    idx = _draws(k, seed)
    with np.errstate(invalid="ignore", divide="ignore"):
        boots = na[idx].sum(1) / da[idx].sum(1) - nb[idx].sum(1) / db[idx].sum(1)
    return _ci(float(est), boots), len(m)


# ------------------------------------------------------------------ report
def fmt(e, lo, hi, dec=3):
    if e is None or not np.isfinite(e):
        return "–"
    ci = f" [{lo:.{dec}f}, {hi:.{dec}f}]" if np.isfinite(lo) else ""
    return f"{e:.{dec}f}{ci}"


def build(runs: Path, split: str, models: tuple[str, ...], out_md: Path, out_csv: Path, status: str) -> dict:
    meta = manifest_table(split)
    expected = expected_trials(split)
    n_pairs_total = len(expected)
    for m in models:  # predictions.row looks up parameter counts in the local registry
        pr.MODELS.setdefault(m, {"params_b": api.MODELS[m]["params_b"]})
    am: dict[str, APIModel] = {}
    info: dict[str, dict] = {}
    for m in models:
        f = runs / m / "results.jsonl"
        rep = read_replies(f) if f.exists() else pd.DataFrame()
        if rep.empty:
            info[m] = {"replies": 0}
            continue
        pres = presentations(rep)
        done = complete_pairs(pres, expected)
        am[m] = APIModel(m, pres, meta, done)
        by_exp = meta[meta.pair_id.isin(done)].pair_id.map(lambda p: p.split("-")[0]).value_counts().to_dict()
        info[m] = {"replies": len(rep), "presentations": len(pres), "complete_pairs": len(done),
                   "share_of_pairs": len(done) / n_pairs_total, "by_experiment": by_exp,
                   "offmenu": am[m].offmenu, "refusing": am[m].refusing}
    rows = []

    def add(section, model, item, est=np.nan, lo=np.nan, hi=np.nan, n=0, note=""):
        rows.append({"section": section, "model": model, "item": item, "estimate": est, "lo": lo, "hi": hi,
                     "n": n, "note": note})

    lines = ["# NVIDIA addendum: Gemma 4 31B and Nemotron 3.5 Super VL", "",
             f"Generated by `scripts/api_report.py`. {status}", "",
             "The rules are fixed in `PLAN.md` (NVIDIA addendum and its five amendments) and in this script's "
             "docstring, all written before any test reply was read. The two-image layout and the \"you\" "
             "framing apply unless stated. The intervals are 95% cluster-bootstrap intervals over stimuli.", ""]

    # completeness, refusal, position bias
    lines += ["## What was collected", "", "| Model | Replies | Complete pairs | Share of the design | Off-menu (preference) | Refusal rule |",
              "|---|---|---|---|---|---|"]
    for m in models:
        i = info[m]
        if not i.get("replies"):
            lines.append(f"| {m} | 0 | – | – | – | – |")
            continue
        lines.append(f"| {m} | {i['replies']:,} | {i['complete_pairs']:,} of {n_pairs_total:,} | {i['share_of_pairs']:.1%} | "
                     f"{i['offmenu']:.1%} | {'refusing: not scored' if i['refusing'] else 'scored'} |")
        add("collected", m, "complete pairs", i["complete_pairs"], n=n_pairs_total, note=json.dumps(i["by_experiment"]))
        add("collected", m, "off-menu share of preference replies", i["offmenu"])
    lines += [""]

    lines += ["## Position bias and visibility", "",
              "Position bias is the share of on-menu replies naming the first image on identical pairs (.5 = none). "
              "Visibility is the same/different AUC on each experiment (rule: at least .75 with the lower end above .50).", "",
              "| Model | Position bias | E1 | E2 | E3 | E4 | E5 |", "|---|---|---|---|---|---|---|"]
    for m, mod in am.items():
        ident = mod.pres[(mod.pres.task == "prefer") & (mod.pres.framing == "you") & mod.pres.pair_id.isin(
            meta[meta.kind == "identical"].pair_id)].merge(meta[["pair_id", "cluster"]], on="pair_id")
        pb = boot_ratio(ident.cluster.values, ident.c_first.values, ident.c_on.values) if len(ident) else (np.nan,) * 3
        add("bias", m, "P(first image named), identical pairs", *pb, n=ident.pair_id.nunique())
        cells = [fmt(*pb)]
        for exp in ("apb", "multiobject", "framing", "colour", "proportion"):
            a = mod.visibility(exp)
            add("visibility", m, exp, *a, note="sees" if mod.sees(exp) else "cannot see")
            cells.append(f"{fmt(*a, dec=2)}{'' if mod.sees(exp) else ' (cannot see)'}")
        lines.append(f"| {m} | " + " | ".join(cells) + " |")
    lines += [""]

    # headline P_cells
    local_pc = {}
    for lm in LOCAL_MODELS:
        p = ROOT / "runs" / "test" / lm / "results.jsonl"
        if p.exists():
            local_pc[lm] = {t: local_cells(lm, meta, t) for t in ("prefer", "weight")}
    lines += ["## Choice proportions (P_cells): the scale shared with people and the local models", "",
              "P_cells counts how often a model names the reference image across all counterbalanced presentations, as "
              "people's choice proportions do. The local models' range is their own P_cells over all their test pairs, "
              "for context.", "",
              "| Effect | " + " | ".join(am) + " | People | Local models (range) |", "|---|" + "---|" * len(am) + "---|---|"]
    for key, label, task, sel, human, hnote in HEADLINE:
        cells = []
        for m, mod in am.items():
            frame = mod.pp if task == "prefer" else mod.pw
            if frame is None or (mod.refusing):
                cells.append("–")
                continue
            d = subset(frame, sel)
            pc = boot_ratio(d.cluster.values, d.num.values, d.den.values) if len(d) else (np.nan,) * 3
            add("p_cells", m, key, *pc, n=len(d), note=label)
            cells.append(f"{fmt(*pc)} (n={len(d)})")
        lv = []
        for lm, frames in local_pc.items():
            d = subset(frames[task], sel)
            if len(d):
                lv.append(d.num.sum() / d.den.sum())
        lr = f"{min(lv):.3f} to {max(lv):.3f}" if lv else "–"
        hv = f"{human:.3f} ({hnote})" if human is not None else hnote
        lines.append(f"| {label} | " + " | ".join(cells) + f" | {hv} | {lr} |")
    lines += [""]

    # comparisons
    lines += ["## Comparisons, paired by pair", ""]
    if len(am) == 2:
        (ma, a), (mb, b) = list(am.items())
        lines += [f"**{ma} minus {mb}** on pairs complete for both (P_cells difference):", "",
                  "| Effect | Difference | Shared pairs |", "|---|---|---|"]
        for key, label, task, sel, *_ in HEADLINE:
            fa, fb = (a.pp, b.pp) if task == "prefer" else (a.pw, b.pw)
            if fa is None or fb is None:
                continue
            e, n = paired_ratio_diff(subset(fa, sel), subset(fb, sel))
            add("nvidia_a_minus_b", f"{ma} - {mb}", key, *e, n=n, note=label)
            lines.append(f"| {label} | {fmt(*e)} | {n} |")
        lines += [""]
    for m, sib in LOCAL_SIBLING.items():
        if m not in am or sib not in local_pc:
            continue
        lines += [f"**{m} minus the local {sib}** (same family), on {m}'s complete pairs (P_cells difference):", "",
                  "| Effect | Difference | Pairs |", "|---|---|---|"]
        for key, label, task, sel, *_ in HEADLINE:
            fa = am[m].pp if task == "prefer" else am[m].pw
            if fa is None:
                continue
            e, n = paired_ratio_diff(subset(fa, sel), subset(local_pc[sib][task], sel))
            add("family", f"{m} - {sib}", key, *e, n=n, note=label)
            lines.append(f"| {label} | {fmt(*e)} | {n} |")
        lines += [""]

    # predictions, by predictions.py's own functions
    lines += ["## Predictions (pre-registered sign statistic)", "",
              "Scored by `scripts/predictions.py`'s functions and criteria, with ties counted as one half. With one sampled "
              "reply per presentation this statistic sits much closer to .5 than the local models' log-probability "
              "version (`reports/readout_math.md`), so these verdicts are not comparable with the main report's. "
              "P1 and P5 concern small models and do not apply.", "",
              "| Model | Prediction | Part | Estimate | Verdict | Note |", "|---|---|---|---|---|---|"]
    for m, mod in am.items():
        if mod.refusing:
            lines.append(f"| {m} | all | – | – | refusing | off-menu {mod.offmenu:.1%} |")
            continue
        for fn in (pr.p2, pr.p3, pr.p4, p6_complete_families):
            for r in fn(mod):
                add("prediction", m, f"{r['prediction']}: {r['part']}", r["estimate"], r["lo"], r["hi"],
                    note=f"{r['verdict']}; {r['note']}".strip("; "))
                lines.append(f"| {m} | {r['prediction']} | {r['part']} | {fmt(r['estimate'], r['lo'], r['hi'])} | "
                             f"{r['verdict']} | {r['note']} |")
    lines += [""]

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pd.DataFrame(rows).to_csv(out_csv, index=False, float_format="%.4f")
    return {"info": info, "rows": pd.DataFrame(rows), "models": am}


# ------------------------------------------------------------------ self-test
def simulate(runs: Path, split: str, spec: dict, seed: int = 7) -> None:
    """Simulated replies with known probabilities: logit P(reference) = d + b*o + a*g, where o and
    g say whether the reference is shown first / labelled A; 3% off-menu replies."""
    rng = np.random.default_rng(seed)
    trials = run_api.trials_for(split)
    pair_order = list(dict.fromkeys(t.pair_id for t in trials))
    kind = manifest_table(split).set_index("pair_id")["kind"].to_dict()
    for m, s in spec.items():
        keep = set(pair_order[: int(len(pair_order) * s["share"])])
        d = runs / m
        d.mkdir(parents=True, exist_ok=True)
        with (d / "results.jsonl").open("w", encoding="utf-8", newline="\n") as f:
            for t in trials:
                if t.pair_id not in keep:
                    continue
                o = 1 if t.first == "ref" else -1
                ref_letter = t.labels[0] if t.first == "ref" else t.labels[1]
                g = 1 if ref_letter == "A" else -1
                eff = s["d"](t) if t.task in ("prefer", "weight") else 0.0
                p_ref = special.expit(eff + s["b"] * o + 0.2 * g)
                if t.task == "samediff":  # a model that sees the change 80% of the time
                    says_differ = rng.random() < (0.8 if kind[t.pair_id] == "manipulation" else 0.2)
                    yes = says_differ if t.framing == "different" else not says_differ
                    choice = "Yes" if yes else "No"
                else:
                    ref_chosen = rng.random() < p_ref
                    choice = ref_letter if ref_chosen else (t.labels[1] if ref_letter == t.labels[0] else t.labels[0])
                if rng.random() < 0.03:
                    choice = None
                f.write(json.dumps({"trial_id": f"{t.trial_id}|s=1", "base_trial_id": t.trial_id, "sample": 1,
                                    "pair_id": t.pair_id, "experiment": t.experiment, "task": t.task,
                                    "framing": t.framing, "layout": t.layout, "first": t.first,
                                    "labels": list(t.labels), "answers": list(t.answers), "choice": choice,
                                    "reply": choice}) + "\n")


def selftest() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="aesx_api_report_"))
    try:
        spec = {
            "gemma-4-31b": {"share": 0.35, "b": 0.5, "d": lambda t: 0.8 if (t.experiment == "multiobject" and "-bal-" in t.pair_id) else 0.0},
            "nemotron-3.5-super-vl": {"share": 0.7, "b": -1.0, "d": lambda t: -0.3 if (t.experiment == "framing" and "-flip-" in t.pair_id) else 0.0},
        }
        simulate(tmp / "runs", "test", spec)
        res = build(tmp / "runs", "test", MODELS, tmp / "report.md", tmp / "report.csv", "SELF-TEST on simulated replies.")
        rows, info = res["rows"], res["info"]
        exp_e2 = (special.expit(0.8 + 0.5 + 0.2) + special.expit(0.8 + 0.5 - 0.2) + special.expit(0.8 - 0.5 + 0.2)
                  + special.expit(0.8 - 0.5 - 0.2)) / 4
        exp_e3 = np.mean([special.expit(-0.3 + bo + ga) for bo in (-1.0, 1.0) for ga in (0.2, -0.2)])
        got_e2 = rows[(rows.section == "p_cells") & (rows.model == "gemma-4-31b") & (rows.item == "e2_p_balanced")].estimate.item()
        got_e3 = rows[(rows.section == "p_cells") & (rows.model == "nemotron-3.5-super-vl") & (rows.item == "e3_p_inward")].estimate.item()
        shared = rows[(rows.section == "nvidia_a_minus_b") & (rows.item == "e2_p_balanced")].n.item()
        print(f"complete pairs: gemma {info['gemma-4-31b']['complete_pairs']}, nemotron {info['nemotron-3.5-super-vl']['complete_pairs']} "
              f"(simulated shares .35 and .70 of {len(expected_trials('test'))})")
        print(f"gemma E2 P_cells {got_e2:.3f} (true {exp_e2:.3f}); nemotron E3 P_cells {got_e3:.3f} (true {exp_e3:.3f}); "
              f"shared E2 pairs {shared}")
        print(f"off-menu: gemma {info['gemma-4-31b']['offmenu']:.3f}, nemotron {info['nemotron-3.5-super-vl']['offmenu']:.3f} (simulated .030)")
        ok = abs(got_e2 - exp_e2) < 0.05 and abs(got_e3 - exp_e3) < 0.05 and shared > 0
        ok &= abs(info["gemma-4-31b"]["offmenu"] - 0.03) < 0.01
        ok &= (rows.section == "prediction").any() and (rows.section == "family").any()
        print("report sections:", sorted(rows.section.unique()))
        print("SELF-TEST", "PASSED" if ok else "FAILED")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--final", action="store_true", help="read runs/nvidia-test: only once the owner says the run has stopped")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.final:
        ap.print_help()
        return 2
    runs = ROOT / "runs" / "nvidia-test"
    newest = None
    for m in MODELS:
        f = runs / m / "results.jsonl"
        if f.exists() and f.stat().st_size:
            with f.open("rb") as fh:
                fh.seek(-min(4096, f.stat().st_size), 2)
                last = fh.read().decode("utf-8", "replace").strip().splitlines()[-1]
            t = datetime.fromisoformat(json.loads(last)["utc"])
            newest = t if newest is None or t > newest else newest
    now = datetime.now(timezone.utc)
    if newest and now < run_api.STOP_AT and now - newest < timedelta(minutes=30):
        print(f"Refusing: the run looks active (last reply {newest:%Y-%m-%d %H:%M} UTC) and its stop time "
              f"({run_api.STOP_AT:%Y-%m-%d %H:%M} UTC) has not come. PLAN.md: no reply is read before the run stops.",
              file=sys.stderr)
        return 2
    frozen = json.loads((ROOT / "FROZEN_API.json").read_text(encoding="utf-8"))
    status = (f"Final run data as of {now:%Y-%m-%d %H:%M} UTC. Gemma 4 31B was withdrawn by NVIDIA "
              f"({frozen.get('withdrawn', {}).get('gemma-4-31b', {}).get('end_of_life', 'see PLAN.md')}) and is "
              "reported as incomplete; Nemotron ran until the fixed stop time or the end of pass 1.")
    build(runs, "test", MODELS, ROOT / "reports" / "nvidia_addendum.md", ROOT / "reports" / "nvidia_addendum.csv", status)
    print("-> reports/nvidia_addendum.md, reports/nvidia_addendum.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
