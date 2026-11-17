"""Score predictions P1 to P6 (PLAN.md) against a run.

    uv run python scripts/predictions.py --split test --tag test     -> reports/predictions_test.md and .csv
    uv run python scripts/predictions.py --split dev --tag pilot     -> reports/predictions_pilot.*  (code check)

Written and committed on 2026-11-17, while the main run was still going and before any
test result had been opened. PLAN.md states each prediction and the test that decides it;
where it gives no numeric criterion, the criterion is fixed here, at the same time, and
listed in CRITERIA (printed at the top of the report).

The primary cell throughout is the two-image layout and the "you" framing; P3 compares
the two framings. Intervals are 95% bootstrap intervals over stimuli, resampling the same
clusters as the main analysis (a family in E1, a unit in E2, an icon in E3, a layout in E4).
A model that fails the visibility rule in an experiment is listed as "cannot see" for every
part that rests on that experiment. A model classed as refusing on more than a fifth of its
refusal probe is listed as "refusing" and not scored.
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings

import numpy as np
import pandas as pd

from aesx import analysis
from aesx.effects import _ci, _draws, apb_effects, manifest_table, multiobject_effects
from aesx.manifest import ROOT
from aesx.models.registry import MODELS

warnings.simplefilter("ignore", RuntimeWarning)

LAYOUT, FRAMING = "two", "you"
SMALL_B = 3.0          # P1: "small" = under 3B parameters (PLAN.md)
P2_HUMAN_TOP = 0.561   # P2: highest of the eight human bars
P2_MATCH = (0.43, 0.57)
P6_INDIVIDUAL = (-0.46, -0.28)  # P6: range of individual raters' mean r
VIS_AUC, VIS_LO = 0.75, 0.50    # visibility rule (PLAN.md)
REFUSAL_MAX = 0.20

CRITERIA = [
    "P1 (models under 3B): |position bias| on identical pairs of E1-E4 (log-odds) against the largest "
    "|mean preference| (log-odds) over the anchored conditions of the experiments the model can see: "
    "E1 all changed pairs, E2 90 px pairs, E3 off-centre flips and centre-vs-quarter pairs, E4 weight "
    "question red vs yellow at 8-24% area. Supported if the bias is larger (point estimates, as PLAN.md says).",
    "P2: E2 P(balanced chosen) at 90 px. Supported if the interval's lower end is above .561; "
    "'matches people' if the whole interval lies within .43-.57; otherwise inconclusive (or 'reversed' if "
    "the upper end is below .50).",
    "P3: E3 off-centre flips. Difference |P(inward | most people) - .5| - |P(inward | you) - .5|, paired over "
    "icons. Supported if the interval is above zero.",
    "P4: three parts, each a paired difference with its interval. E1: P(more balanced chosen) at score "
    "difference 40-100 minus at 0-12 (families). E3: P(inward) at 25% minus at 8% from centre (icons). "
    "E4 weight: P(red named heavier than yellow) at the small and medium sizes pooled minus at the large "
    "size (layouts). Supported if the interval is above zero; 'reversed' if below. The four E1 bins are "
    "also shown, with whether they rise monotonically.",
    "P5 (the two smallest frozen models): visibility on the subtlest manipulations, E2 45 px shifts and E1 "
    "pairs under 12 points apart, each against that experiment's identical pairs. Supported for a model if "
    "it fails the visibility rule (AUC at least .75 with the lower end above .50) on that subset. Shown "
    "for every model.",
    "P6: E1 r(balance score, preference scale value). Supported if the interval's upper end is below "
    "-.46 (stronger than the strongest individual-rater mean); 'weaker than individuals' if its lower end "
    "is above -.28; otherwise inconclusive.",
]


# ------------------------------------------------------------------ helpers
def paired_diff(cl_a, va, cl_b, vb, f=lambda a, b: a - b, seed: int = 0):
    """f(mean of a, mean of b), both resampled with the same draw of clusters."""
    cl_a, cl_b = np.asarray(cl_a), np.asarray(cl_b)
    va, vb = np.asarray(va, float), np.asarray(vb, float)
    if len(va) == 0 or len(vb) == 0:
        return (np.nan,) * 3
    codes, uniq = pd.factorize(np.concatenate([cl_a, cl_b]))
    ca, cb, k = codes[: len(cl_a)], codes[len(cl_a):], len(uniq)
    sa, na = np.bincount(ca, va, k), np.bincount(ca, minlength=k).astype(float)
    sb, nb = np.bincount(cb, vb, k), np.bincount(cb, minlength=k).astype(float)
    est = f(sa.sum() / na.sum(), sb.sum() / nb.sum())
    idx = _draws(k, seed)
    with np.errstate(invalid="ignore", divide="ignore"):
        return _ci(est, f(sa[idx].sum(1) / na[idx].sum(1), sb[idx].sum(1) / nb[idx].sum(1)))


def mean_boot(values, seed: int = 0):
    v = np.asarray(values, float)
    if len(v) < 2:
        return (float(v.mean()) if len(v) else np.nan, np.nan, np.nan)
    return _ci(float(v.mean()), v[_draws(len(v), seed)].mean(1))


def verdict_interval(lo, hi, zero=0.0) -> str:
    if np.isnan(lo) or np.isnan(hi):
        return "not estimable"
    return "supported" if lo > zero else "reversed" if hi < zero else "not supported"


class Model:
    def __init__(self, run, meta: pd.DataFrame):
        self.name = run.parent.name
        df = analysis.load_results(run)
        self.pp = analysis.prefer_by_pair(df).merge(meta, on="pair_id")
        self.pp = self.pp[self.pp.layout == LAYOUT]
        self.pw = analysis.prefer_by_pair(df, "weight").merge(meta, on="pair_id") if (df.task == "weight").any() else None
        if self.pw is not None:
            self.pw = self.pw[(self.pw.layout == LAYOUT)]
        self.sd = analysis.samediff_by_pair(df).merge(meta, on="pair_id")
        self.sd = self.sd[self.sd.layout == LAYOUT]
        probe = run.parent / "refusal_probe.json"
        self.refusal = json.loads(probe.read_text(encoding="utf-8")) if probe.exists() else None
        self._vis = {}

    @property
    def refusing(self) -> bool:
        return bool(self.refusal and self.refusal.get("refuses", 0) > REFUSAL_MAX)

    def you(self, exp: str) -> pd.DataFrame:
        """Changed pairs of one experiment, primary framing. (Fixed 2026-11-17 after the first
        test scoring: identical pairs share a condition label with E2's 90 px pairs and E3's
        flips and were being counted in P1, P3 and P4-E3; see LOG.md.)"""
        d = self.pp[(self.pp.experiment == exp) & (self.pp.framing == FRAMING) & (self.pp.kind == "manipulation")]
        return d

    def visibility(self, exp: str, mask=None):
        s = self.sd[self.sd.experiment == exp]
        pos = s[s.kind == "manipulation"]
        if mask is not None:
            pos = pos[mask(pos)]
        neg = s[s.kind == "identical"]
        if len(pos) == 0 or len(neg) == 0:
            return (np.nan,) * 3
        return analysis.auc_ci(pos["diff"].values, neg["diff"].values)

    def sees(self, exp: str) -> bool:
        if exp not in self._vis:
            a, lo, _ = self.visibility(exp)
            self._vis[exp] = bool(a >= VIS_AUC and lo > VIS_LO)
        return self._vis[exp]


# --------------------------------------------------------------- predictions
def p1(m: Model) -> list[dict]:
    if MODELS[m.name]["params_b"] >= SMALL_B:
        return [row("P1", m, "", note=f"not tested: {MODELS[m.name]['params_b']:.1f}B, not under {SMALL_B:.0f}B")]
    ident = m.pp[(m.pp.kind == "identical") & (m.pp.framing == FRAMING) & m.pp.experiment.isin(["apb", "multiobject", "framing", "colour"])]
    bias = mean_boot(ident.pos_bias.values)
    conds = {
        "E1 changed pairs": ("apb", lambda d: d[d.kind == "manipulation"]),
        "E2 90 px": ("multiobject", lambda d: d[d.condition == "balance"]),
        "E3 off-centre flips": ("framing", lambda d: d[(d.condition == "flip") & (d.p_pos_ref != 50)]),
        "E3 centre vs quarter": ("framing", lambda d: d[(d.condition == "centre") & (d.human_direction == "ref")]),
    }
    effects = {}
    for lab, (exp, sel) in conds.items():
        if m.sees(exp):
            g = sel(m.you(exp))
            effects[lab] = (abs(g.pref.mean()), g)
    if m.pw is not None and m.sees("colour"):
        g = m.pw[(m.pw.experiment == "colour") & (m.pw.human_direction == "ref")]
        effects["E4 weight, red vs yellow"] = (abs(g.pref.mean()), g)
    out = [row("P1", m, "position bias, log-odds (signed; + = first image)", *bias,
               note=f"{len(ident)} identical pairs; compared by its absolute value {abs(bias[0]):.3f}")]
    if not effects:
        out.append(row("P1", m, "verdict", verdict="cannot see", note="fails the visibility rule in E1 to E4"))
        return out
    for lab, (v, g) in effects.items():
        out.append(row("P1", m, f"|mean preference|, {lab}", v, note=f"{len(g)} pairs"))
    top_lab, (top, _) = max(effects.items(), key=lambda kv: kv[1][0])
    out.append(row("P1", m, "verdict", abs(bias[0]) - top, verdict="supported" if abs(bias[0]) > top else "not supported",
                   note=f"bias minus largest effect ({top_lab})"))
    return out


def p1_by_experiment(m: Model) -> list[dict]:
    """POST HOC, added 2026-11-17 after the test results were opened. The committed P1 pools
    the signed position bias over E1-E4, so biases of opposite sign in different experiments
    cancel. This compares, within each experiment the model can see, the absolute bias on that
    experiment's identical pairs with the largest absolute mean preference among its anchored
    conditions. Reported beside the committed verdict, never instead of it."""
    if MODELS[m.name]["params_b"] >= SMALL_B:
        return []
    conds = {
        "apb": [lambda d: d],
        "multiobject": [lambda d: d[d.condition == "balance"]],
        "framing": [lambda d: d[(d.condition == "flip") & (d.p_pos_ref != 50)],
                    lambda d: d[(d.condition == "centre") & (d.human_direction == "ref")]],
    }
    out, n_bias = [], 0
    for exp in ("apb", "multiobject", "framing", "colour"):
        if not m.sees(exp):
            continue
        if exp == "colour":
            if m.pw is None:
                continue
            src = m.pw[m.pw.experiment == "colour"]
            ident = src[(src.kind == "identical")]
            eff = abs(src[(src.kind == "manipulation") & (src.human_direction == "ref")].pref.mean())
        else:
            src = m.pp[(m.pp.experiment == exp) & (m.pp.framing == FRAMING)]
            ident = src[src.kind == "identical"]
            eff = max(abs(sel(m.you(exp)).pref.mean()) for sel in conds[exp])
        bias = abs(ident.pos_bias.mean())
        n_bias += bias > eff
        out.append(row("P1b", m, f"{exp}: |bias| {bias:.3f} vs largest |effect| {eff:.3f}", bias - eff,
                       verdict="bias larger" if bias > eff else "effect larger", note="post hoc"))
    if out:
        out.append(row("P1b", m, "verdict", verdict=f"bias larger in {n_bias} of {len(out)}", note="post hoc"))
    return out


def p2(m: Model) -> list[dict]:
    if not m.sees("multiobject"):
        return [row("P2", m, "verdict", verdict="cannot see", note="fails the visibility rule in E2")]
    r = next(x for x in multiobject_effects(m.you("multiobject")) if x["key"] == "p_balanced")
    lo, hi = r["lo"], r["hi"]
    if lo > P2_HUMAN_TOP:
        v = "supported"
    elif lo >= P2_MATCH[0] and hi <= P2_MATCH[1]:
        v = "matches people"
    elif hi < 0.5:
        v = "reversed"
    else:
        v = "inconclusive"
    return [row("P2", m, "P(balanced chosen), 90 px", r["estimate"], lo, hi, verdict=v, note=f"{r['n']} pairs")]


def p3(m: Model) -> list[dict]:
    if not m.sees("framing"):
        return [row("P3", m, "verdict", verdict="cannot see", note="fails the visibility rule in E3")]
    d = m.pp[(m.pp.experiment == "framing") & (m.pp.kind == "manipulation") & (m.pp.condition == "flip") & (m.pp.p_pos_ref != 50)]
    you, most = d[d.framing == "you"], d[d.framing == "most"]
    out = []
    for lab, g in (("you", you), ("most people", most)):
        e = paired_diff(g.cluster, g.choice_ref, g.cluster, g.choice_ref, f=lambda a, b: a)
        out.append(row("P3", m, f"P(inward chosen), {lab}", *e, note=f"{len(g)} pairs"))
    diff = paired_diff(you.cluster, you.choice_ref, most.cluster, most.choice_ref, f=lambda a, b: np.abs(b - 0.5) - np.abs(a - 0.5))
    out.append(row("P3", m, "|most - .5| minus |you - .5|", *diff, verdict=verdict_interval(diff[1], diff[2])))
    return out


def p4(m: Model) -> list[dict]:
    out = []
    # E1
    if m.sees("apb"):
        d = m.you("apb")
        d = d[d.kind == "manipulation"]
        bins = [(0, 12), (12, 25), (25, 40), (40, 100)]
        ps = []
        for lo_, hi_ in bins:
            g = d[(d.dose >= lo_) & (d.dose < hi_)]
            e = paired_diff(g.cluster, g.choice_ref, g.cluster, g.choice_ref, f=lambda a, b: a)
            ps.append(e[0])
            out.append(row("P4", m, f"E1 P(more balanced chosen), difference {lo_}-{hi_}", *e, note=f"{len(g)} pairs"))
        a, b = d[d.dose >= 40], d[d.dose < 12]
        e = paired_diff(a.cluster, a.choice_ref, b.cluster, b.choice_ref)
        mono = all(x <= y for x, y in zip(ps, ps[1:]))
        out.append(row("P4", m, "E1 verdict: 40-100 minus 0-12", *e, verdict=verdict_interval(e[1], e[2]),
                       note="bins rise monotonically" if mono else "bins not monotonic"))
    else:
        out.append(row("P4", m, "E1 verdict", verdict="cannot see", note="fails the visibility rule in E1"))
    # E3
    if m.sees("framing"):
        d = m.you("framing")
        d = d[(d.condition == "flip") & (d.p_pos_ref != 50)]
        eccs = sorted(d.dose.unique())
        near, far = d[d.dose == eccs[0]], d[d.dose == eccs[-1]]
        for lab, g in (("8%", near), ("25%", far)):
            out.append(row("P4", m, f"E3 P(inward chosen), {lab} from centre",
                           *paired_diff(g.cluster, g.choice_ref, g.cluster, g.choice_ref, f=lambda a, b: a), note=f"{len(g)} pairs"))
        e = paired_diff(far.cluster, far.choice_ref, near.cluster, near.choice_ref)
        out.append(row("P4", m, "E3 verdict: 25% minus 8%", *e, verdict=verdict_interval(e[1], e[2]), note="people: .82 against .70"))
    else:
        out.append(row("P4", m, "E3 verdict", verdict="cannot see", note="fails the visibility rule in E3"))
    # E4 weight
    if m.pw is not None and m.sees("colour"):
        d = m.pw[(m.pw.experiment == "colour") & (m.pw.condition == "red_vs_yellow")]
        small, large = d[d.p_size_level.isin(["small", "medium"])], d[d.p_size_level == "large"]
        for lab, g in (("small and medium", small), ("large", large)):
            out.append(row("P4", m, f"E4 P(red named heavier than yellow), {lab}",
                           *paired_diff(g.cluster, g.choice_ref, g.cluster, g.choice_ref, f=lambda a, b: a), note=f"{len(g)} pairs"))
        e = paired_diff(small.cluster, small.choice_ref, large.cluster, large.choice_ref)
        out.append(row("P4", m, "E4 verdict: small and medium minus large", *e, verdict=verdict_interval(e[1], e[2]),
                       note="people: present at the smaller areas, absent at the largest"))
    else:
        out.append(row("P4", m, "E4 verdict", verdict="cannot see", note="fails the visibility rule in E4 or no weight trials"))
    return out


def p5(m: Model, smallest: set[str]) -> list[dict]:
    out = []
    for lab, exp, mask in (("E2 45 px", "multiobject", lambda s: s.dose == 45),
                           ("E1 under 12 points", "apb", lambda s: s.dose < 12)):
        a, lo, hi = m.visibility(exp, mask)
        fails = not (a >= VIS_AUC and lo > VIS_LO)
        v = ("supported" if fails else "not supported") if m.name in smallest else ("fails" if fails else "passes")
        out.append(row("P5", m, f"{lab}: visibility AUC", a, lo, hi, verdict=v,
                       note="prediction applies" if m.name in smallest else "context only"))
    return out


def p6(m: Model) -> list[dict]:
    if not m.sees("apb"):
        return [row("P6", m, "verdict", verdict="cannot see", note="fails the visibility rule in E1")]
    r = next(x for x in apb_effects(m.you("apb")) if x["key"] == "r_apb_all")
    lo, hi = r["lo"], r["hi"]
    if np.isnan(lo):
        v = "not estimable"
    elif hi < P6_INDIVIDUAL[0]:
        v = "supported"
    elif lo > P6_INDIVIDUAL[1]:
        v = "weaker than individuals"
    else:
        v = "inconclusive"
    return [row("P6", m, "r(balance score, preference scale value)", r["estimate"], lo, hi, verdict=v,
                note="people: images -.85 to -.88; individual raters -.28 to -.46")]


def row(pred, m: Model, part, est=np.nan, lo=np.nan, hi=np.nan, verdict="", note="") -> dict:
    return {"prediction": pred, "model": m.name, "params_b": MODELS[m.name]["params_b"], "part": part,
            "estimate": est, "lo": lo, "hi": hi, "verdict": verdict, "note": note}


# ------------------------------------------------------------------ report
def write_md(t: pd.DataFrame, tag: str, models: list[str], refusing: dict) -> None:
    lines = [f"# Predictions P1 to P6, run `{tag}`", "",
             f"Generated by `scripts/predictions.py --tag {tag}`. Two-image layout, \"you\" framing unless stated. "
             "Predictions are stated in `PLAN.md`; the criteria below were fixed in this script before the test "
             "results were opened.", "", "## Criteria", ""] + [f"- {c}" for c in CRITERIA] + [""]
    if refusing:
        lines += ["## Refusing models (not scored)", ""] + [f"- {k}: refuses on {v:.0%} of the probe" for k, v in refusing.items()] + [""]
    verdicts = t[t.verdict != ""]
    lines += ["## Summary", "", "| Prediction | " + " | ".join(models) + " |", "|---|" + "---|" * len(models)]
    for pred, g in verdicts.groupby("prediction", sort=True):
        cells = []
        for mname in models:
            v = g[g.model == mname]
            if (v.part == "verdict").any() and len(v) > 1:
                v = v[v.part == "verdict"]
            cells.append("; ".join(f"{p.split(':')[0].replace(' verdict', '')}: {x}" if len(v) > 1 else x
                                   for p, x in zip(v.part, v.verdict)) or "")
        lines.append(f"| {pred} | " + " | ".join(cells) + " |")
    lines.append("")
    for pred, g in t.groupby("prediction", sort=True):
        lines += [f"## {pred}", "", "| Model | Part | Estimate [95% interval] | Verdict | Note |", "|---|---|---|---|---|"]
        for _, r in g.iterrows():
            est = "" if pd.isna(r.estimate) else (f"{r.estimate:.3f}" if pd.isna(r.lo) else f"{r.estimate:.3f} [{r.lo:.3f}, {r.hi:.3f}]")
            lines.append(f"| {r.model} | {r.part} | {est} | {r.verdict} | {r.note} |")
        lines.append("")
    (ROOT / "reports" / f"predictions_{tag}.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    ap.add_argument("--tag", default="test")
    a = ap.parse_args()
    meta = manifest_table(a.split)
    runs = sorted((ROOT / "runs" / a.tag).glob("*/results.jsonl"), key=lambda p: MODELS[p.parent.name]["params_b"])
    if not runs:
        print("no runs found")
        return 1
    models = [Model(r, meta) for r in runs]
    names = [m.name for m in models]
    smallest = set(sorted(names, key=lambda n: MODELS[n]["params_b"])[:2])
    rows, refusing = [], {}
    for m in models:
        if m.refusing:
            refusing[m.name] = m.refusal["refuses"]
            rows.append(row("P0", m, "refusal", verdict="refusing, not scored"))
            continue
        rows += p1(m) + p1_by_experiment(m) + p2(m) + p3(m) + p4(m) + p5(m, smallest) + p6(m)
    t = pd.DataFrame(rows)
    (ROOT / "reports").mkdir(exist_ok=True)
    t.to_csv(ROOT / "reports" / f"predictions_{a.tag}.csv", index=False, float_format="%.4f")
    write_md(t, a.tag, names, refusing)
    print(f"{len(t)} rows -> reports/predictions_{a.tag}.csv, reports/predictions_{a.tag}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
