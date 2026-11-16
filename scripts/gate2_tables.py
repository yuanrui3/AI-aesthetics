"""Gate 2 tables from the pilot runs (runs/pilot/<model>/).

    uv run python scripts/gate2_tables.py     ->  reports/gate2_tables.md, reports/gate2_layout.csv

1. Models: pinned commit, licence, size, speed, memory.
2. Layout choice: position bias, visibility and off-menu rate per model and layout,
   and the layout chosen by the rule in PLAN.md.
3. Model against human on the headline statistic of each experiment (chosen layout).
4. The same under the "most people" framing.
5. GPU time the main run needs, from measured seconds per trial.
"""
from __future__ import annotations

import importlib
import json
import subprocess
import sys
import warnings

import numpy as np
import pandas as pd

from aesx import analysis
from aesx.effects import EFFECT_FUNCS, manifest_table
from aesx.manifest import ROOT

warnings.simplefilter("ignore", RuntimeWarning)

TAG = "pilot"
EXPS = ("apb", "multiobject", "framing", "colour", "proportion")
ENAME = {"apb": "E1", "multiobject": "E2", "framing": "E3", "colour": "E4", "proportion": "E5"}
LAYOUT_NAMES = {"two": "two images", "sbs": "side by side"}
VIS_AUC, OFF_MENU_MAX = 0.75, 0.20
# (experiment, effect key, row label, human key or None, note on the human figure)
HEAD = [
    ("apb", "r_apb_all", "E1 r(balance score, preference)", "hf_e2_all", "aggregate; individual raters average -.44"),
    ("apb", "p_balanced", "E1 P(more balanced chosen)", None, "not reported"),
    ("multiobject", "p_balanced", "E2 P(balanced chosen), 90 px shift", "p_balanced", "bars range .48 to .56; not above chance"),
    ("framing", "p_inward", "E3 P(inward-facing chosen)", "p_inward", "positions range .69 to .87"),
    ("framing", "p_centre", "E3 P(centre chosen), symmetrical", None, "direction only: above .50"),
    ("colour", "weight_red_vs_yellow_anchor", "E4 P(red named heavier than yellow)", None, "direction only: above .50"),
    ("proportion", "p_less_altered", "E5 P(less altered chosen)", None, "no anchor"),
]


def human_effects() -> dict:
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "human_effects.py"), "--json"],
                         capture_output=True, text=True, check=True).stdout
    return {(e["experiment"], e["key"]): e for e in json.loads(out)}


def test_trials_one_layout() -> tuple[int, dict]:
    """Trials per model for the full test split in one layout, from each generator's design."""
    per = {}
    for exp in EXPS:
        mod = importlib.import_module(f"aesx.experiments.{exp}")
        if exp == "apb":
            manip, ident = mod.UNITS["test"] * 10, mod.UNITS["test"] * 2
        elif exp == "multiobject":
            manip, ident = mod.UNITS["test"] * 10, mod.UNITS["test"]
        elif exp == "framing":
            manip = (len(mod.DIRECTED["test"]) * mod.FLIP_VARIANTS["test"] * 7 + mod.N_POSITION_ICONS["test"] * 21
                     + len(mod.SYMMETRIC["test"]) * 3)
            ident = max(8, manip // 10)
        elif exp == "colour":
            manip, ident = mod.UNITS["test"] * 6, (mod.UNITS["test"] + 1) // 2
        else:
            manip, ident = mod.UNITS["test"] * 3, (mod.UNITS["test"] + 2) // 3
        questions = 5 if exp == "colour" else 4  # 2 framings + 2 same/different polarities (+ weight)
        per[exp] = {"pairs": manip, "identical": ident, "trials": manip * 4 * questions + ident * 2 * questions}
    return sum(v["trials"] for v in per.values()), per


def main() -> int:
    meta = manifest_table("dev")
    human = human_effects()
    runs = sorted((ROOT / "runs" / TAG).glob("*/results.jsonl"))
    if not runs:
        print("no pilot runs")
        return 1

    models, layout_rows, effect_rows = [], [], []
    for run in runs:
        name = run.parent.name
        spec = json.loads((run.parent / "run.json").read_text(encoding="utf-8"))["model"]
        df = analysis.load_results(run)
        sec = df.groupby("layout").seconds.mean() if "seconds" in df else pd.Series(dtype=float)
        timing = json.loads((run.parent / "timing.json").read_text(encoding="utf-8")) if (run.parent / "timing.json").exists() else {}
        models.append({"model": name, "family": spec.get("family"), "params_b": spec.get("params_b"), "licence": spec.get("licence"),
                       "commit": (spec.get("commit") or "")[:10], "n_trials": len(df),
                       "sec_two": float(sec.get("two", np.nan)), "sec_sbs": float(sec.get("sbs", np.nan)),
                       "peak_vram_mib": timing.get("peak_vram_mib")})
        pp = analysis.prefer_by_pair(df).merge(meta, on="pair_id")
        sd = analysis.samediff_by_pair(df).merge(meta, on="pair_id")
        raw = df[df.task == "prefer"]
        for layout in ("two", "sbs"):
            vis, bias = {}, []
            for exp in EXPS:
                s = sd[(sd.experiment == exp) & (sd.layout == layout)]
                a = analysis.auc_ci(s[s.kind == "manipulation"]["diff"].values, s[s.kind == "identical"]["diff"].values, n_boot=2000)
                vis[exp] = a
                g = pp[(pp.experiment == exp) & (pp.layout == layout) & (pp.kind == "identical")]
                bias.append(float(g.pos_bias.mean()))
            off = float(raw[raw.layout == layout].off_menu.mean())
            passed = [e for e in EXPS if vis[e][0] >= VIS_AUC and vis[e][1] > 0.5]
            layout_rows.append({"model": name, "layout": layout, "pos_bias_median_abs": float(np.median(np.abs(bias))),
                                "pos_bias_mean_signed": float(np.mean(bias)), "off_menu": off,
                                "visible_n": len(passed), "visible": ",".join(ENAME[e] for e in passed),
                                **{f"auc_{e}": vis[e][0] for e in EXPS}})
        for task in ("prefer", "weight"):
            if not (df.task == task).any():
                continue
            p2 = analysis.prefer_by_pair(df, task).merge(meta, on="pair_id")
            for (layout, framing), d in p2.groupby(["layout", "framing"], sort=False):
                for exp, fn in EFFECT_FUNCS.items():
                    if not (d.experiment == exp).any() or (task == "weight" and exp != "colour"):
                        continue
                    for r in (fn(d, task) if exp == "colour" else fn(d)):
                        effect_rows.append({"model": name, "layout": layout, "framing": framing, "task": task, **r})

    M = pd.DataFrame(models).sort_values("params_b")
    L = pd.DataFrame(layout_rows)
    E = pd.DataFrame(effect_rows)
    order = list(M.model)
    (ROOT / "reports").mkdir(exist_ok=True)
    L.to_csv(ROOT / "reports" / "gate2_layout.csv", index=False, float_format="%.4f")
    E.to_csv(ROOT / "reports" / "effects_pilot.csv", index=False, float_format="%.4f")

    # ---- layout rule (PLAN.md): among layouts where at least half the models are usable,
    # the one with the smaller median absolute position bias. "Usable" = stays on the two
    # permitted answers (off-menu <= 0.20) and passes visibility in at least 3 of 5 experiments.
    L["usable"] = (L.off_menu <= OFF_MENU_MAX) & (L.visible_n >= 3)
    summary = L.groupby("layout").agg(usable=("usable", "sum"), bias=("pos_bias_median_abs", "median"),
                                      off_menu=("off_menu", "median")).reindex(["two", "sbs"])
    eligible = summary[summary.usable >= len(order) / 2]
    primary = (eligible if len(eligible) else summary).bias.idxmin()

    versions = sorted({json.loads((r.parent / "run.json").read_text(encoding="utf-8")).get("prompt_version", "?") for r in runs})
    out = [f"# Gate 2 tables (pilot: about 40 dev pairs per experiment, prompt {', '.join(versions)})", "",
           "Generated by `uv run python scripts/gate2_tables.py`. Dev stimuli only.", ""]

    out += ["## 1. Models", "", "| Model | Family | Parameters (B) | Licence | Commit | Seconds per trial: two images / side by side | Peak VRAM (GB) |",
            "|---|---|---|---|---|---|---|"]
    for _, r in M.iterrows():
        vram = "" if pd.isna(r.peak_vram_mib) else f"{r.peak_vram_mib / 1024:.1f}"
        out.append(f"| {r.model} | {r.family} | {r.params_b} | {r.licence} | `{r.commit}` | {r.sec_two:.2f} / {r.sec_sbs:.2f} | {vram} |")

    out += ["", "## 2. Layout choice", "",
            "Position bias: median over the five experiments of the absolute log-odds toward the first/left image on identical pairs. "
            f"Visible: experiments where the same/different AUC is at least {VIS_AUC} with the interval above 0.5. "
            f"Off-menu: share of preference trials with under half the probability on the two letters (limit {OFF_MENU_MAX}).", "",
            "| Model | Position bias: two / side by side | Off-menu: two / side by side | Visible: two | Visible: side by side |", "|---|---|---|---|---|"]
    for m in order:
        a, b = L[(L.model == m) & (L.layout == "two")].iloc[0], L[(L.model == m) & (L.layout == "sbs")].iloc[0]
        out.append(f"| {m} | {a.pos_bias_median_abs:.2f} / {b.pos_bias_median_abs:.2f} | {a.off_menu:.2f} / {b.off_menu:.2f} | "
                   f"{a.visible_n}/5 ({a.visible or 'none'}) | {b.visible_n}/5 ({b.visible or 'none'}) |")
    out += ["", f"Usable models (on-menu and visible in at least 3 of 5 experiments): two images {int(summary.usable['two'])} of {len(order)}, "
                f"side by side {int(summary.usable['sbs'])} of {len(order)}. Median position bias across models: "
                f"two images {summary.bias['two']:.2f}, side by side {summary.bias['sbs']:.2f}.", "",
            f"**Layout the rule in PLAN.md picks: {LAYOUT_NAMES[primary]}.** Tables 3 to 5 are given for both layouts.", "",
            "Visibility by experiment (number of the eight models passing): "
            + "; ".join(f"{ENAME[e]} two images {int(((L.layout == 'two') & L.visible.str.split(',').apply(lambda v: ENAME[e] in v)).sum())}, "
                        f"side by side {int(((L.layout == 'sbs') & L.visible.str.split(',').apply(lambda v: ENAME[e] in v)).sum())}" for e in EXPS) + ".", ""]

    out += ["## 2b. Refusals, and the forced readout against unaided answers", "",
            "60 preference trials per model answered freely (no reply prefix, up to 160 tokens). "
            "*Direct*: the reply opens with a letter. *Commits*: it names a letter as its choice later. "
            "*Refuses*: no choice, and wording that declines. *Unclear*: anything else. "
            "*Agreement*: share of replies with a parsed choice whose letter matches the forced readout on the same trial.", "",
            "| Model | Direct | Commits | Refuses | Unclear | Agreement with forced readout (n parsed) |", "|---|---|---|---|---|---|"]
    for m in order:
        f = ROOT / "runs" / TAG / m / "refusal_probe.json"
        if not f.exists():
            out.append(f"| {m} | not run | | | | |")
            continue
        p = json.loads(f.read_text(encoding="utf-8"))
        out.append(f"| {m} | {p['direct']:.2f} | {p['commits']:.2f} | {p['refuses']:.2f} | {p['unclear']:.2f} | "
                   f"{p['agreement_with_forced_readout']:.2f} ({p['n_parsed']}) |")
    out.append("")

    def cell(m: str, exp: str, key: str, framing: str, task: str, layout: str) -> str:
        r = E[(E.model == m) & (E.layout == layout) & (E.framing == framing) & (E.task == task) & (E.experiment == exp) & (E.key == key)]
        if r.empty or pd.isna(r.iloc[0].estimate):
            return "n/a"
        r = r.iloc[0]
        lrow = L[(L.model == m) & (L.layout == layout)].iloc[0]
        flag = "" if ENAME[exp] in lrow.visible.split(",") else " †"
        flag += " ‡" if lrow.off_menu > OFF_MENU_MAX else ""
        return f"{r.estimate:.2f} [{r.lo:.2f}, {r.hi:.2f}]{flag}"

    for layout, framing, title in [(l, fr, f"{n}{s}. Model against human, {LAYOUT_NAMES[l]}, {q} framing")
                                   for n, fr, q in ((3, "you", '"you"'), (4, "most", '"most people"'))
                                   for s, l in (("a", "two"), ("b", "sbs"))]:
        out += [f"## {title}", "", f"Bias-cancelled choices; 95% bootstrap intervals over stimuli. "
                "† the model fails the visibility rule for that experiment; ‡ the model is off-menu on more than a fifth of preference trials.", "",
                "| Statistic | Human | " + " | ".join(order) + " |", "|---|---|" + "---|" * len(order)]
        for exp, key, label, hkey, note in HEAD:
            h = human.get((exp, hkey)) if hkey else None
            htxt = (f"{h['estimate']:.2f} ({note})" if h else note)
            task, fr = ("weight", "plain") if key.startswith("weight") else ("prefer", framing)
            out.append(f"| {label} | {htxt} | " + " | ".join(cell(m, exp, key, fr, task, layout) for m in order) + " |")
        out.append("")

    total, per = test_trials_one_layout()
    out += ["## 5. GPU time for the main run", "",
            f"Test split in one layout: {sum(v['pairs'] for v in per.values())} manipulation pairs and "
            f"{sum(v['identical'] for v in per.values())} identical pairs, **{total:,} trials per model** "
            "(both orders, both letter assignments, both framings, both same/different polarities, plus the weight question in E4).", "",
            "Seconds per trial were measured with two models sharing the GPU and CPU, so run two at a time the "
            "wall-clock time is about half the summed hours.", "",
            "| Model | Hours, two images | Hours, side by side | Hours, both layouts |", "|---|---|---|---|"]
    h2 = hs = 0.0
    for _, r in M.iterrows():
        a, b = total * r.sec_two / 3600, total * r.sec_sbs / 3600
        h2, hs = h2 + a, hs + b
        out.append(f"| {r.model} | {a:.1f} | {b:.1f} | {a + b:.1f} |")
    out += [f"| **All {len(order)} models (summed)** | **{h2:.1f}** | **{hs:.1f}** | **{h2 + hs:.1f}** |", ""]
    (ROOT / "reports" / "gate2_tables.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
