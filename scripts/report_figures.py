"""One figure per experiment: each model's effect with its 95% interval, beside the human figure.
Plus one dose-response figure.

    uv run python scripts/report_figures.py --tag test      # main run  -> reports/figures/test/
    uv run python scripts/report_figures.py --tag pilot     # pilot     -> reports/figures/pilot/

Needs reports/effects_<tag>.csv (scripts/effects_table.py) and the checks table
(scripts/gate1_checks.py --tag <tag>) for visibility.

Encoding: filled marker = the model can see the manipulation in that experiment
and layout (same/different AUC >= .75, interval above .5); hollow = it cannot, so
its preference is not interpretable. Colour and marker shape both identify the
series (two images / side by side / "most people" framing). Colours are slots 1-3
of the dataviz reference palette (pre-validated; Node was not available to re-run
the validator on this machine).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from aesx.manifest import ROOT  # noqa: E402
from aesx.models.registry import MODELS  # noqa: E402

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#a3a29c", "#ecebe7"
HUMAN_BAND, HUMAN_BAND2, HUMAN_LINE = "#dcdbd6", "#eeede9", "#52514e"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
SERIES = {  # (layout, framing): (label, colour, marker)
    ("two", "you"): ("two images", BLUE, "o"),
    ("sbs", "you"): ("side by side", ORANGE, "s"),
    ("two", "most"): ('"most people" framing', AQUA, "D"),
}
NICE = {"smolvlm2-500m": "SmolVLM2 0.5B", "qwen3.5-0.8b": "Qwen3.5 0.8B", "minicpm-v-4.7-1b": "MiniCPM-V 4.7 1.6B",
        "smolvlm2-2.2b": "SmolVLM2 2.2B", "internvl3.5-2b": "InternVL3.5 2.3B", "north-micro-vision": "North Micro 2.5B",
        "qwen3.5-4b": "Qwen3.5 4.7B", "gemma-4-e2b": "Gemma 4 E2B (5.1B)"}
VIS_AUC = 0.75

plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10, "font.family": "DejaVu Sans",
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                     "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})


def human_effects() -> dict:
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "human_effects.py"), "--json"],
                         capture_output=True, text=True, check=True).stdout
    return {(e["experiment"], e["key"]): e for e in json.loads(out)}


class Data:
    def __init__(self, tag: str):
        self.e = pd.read_csv(ROOT / "reports" / f"effects_{tag}.csv")
        stem = "gate1_checks" if tag == "dev" else f"checks_{tag}"
        self.c = pd.read_csv(ROOT / "reports" / f"{stem}.csv")
        self.models = sorted(self.e.model.unique(), key=lambda m: MODELS[m]["params_b"])

    def get(self, model, exp, key, layout, framing, task="prefer"):
        r = self.e[(self.e.model == model) & (self.e.experiment == exp) & (self.e.key == key) & (self.e.layout == layout)
                   & (self.e.framing == framing) & (self.e.task == task)]
        return None if r.empty else r.iloc[0]

    def visible(self, model, exp, layout) -> bool:
        r = self.c[(self.c.model == model) & (self.c.experiment == exp) & (self.c.layout == layout)]
        return bool(len(r)) and r.iloc[0].visibility_auc >= VIS_AUC and r.iloc[0].visibility_lo > 0.5


def style(ax, xlim, xlabel, chance=None):
    ax.set_xlim(*xlim)
    ax.set_xlabel(xlabel)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    if chance is not None:
        ax.axvline(chance, color=MUTED, linewidth=1.0, zorder=1)


def human_band(ax, lo, hi, est, label, y_text, light=False):
    ax.axvspan(lo, hi, color=HUMAN_BAND2 if light else HUMAN_BAND, zorder=0, linewidth=0)
    if est is not None:
        ax.axvline(est, color=HUMAN_LINE, linewidth=1.2, linestyle=(0, (4, 2)), zorder=1)
    ax.text((lo + hi) / 2 if est is None else est, y_text, label, ha="center", va="bottom", fontsize=8.5, color=INK2,
            zorder=5, bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.5, alpha=1.0))


FRAMING_LABELS = {("two", "you"): '"you" framing', ("two", "most"): '"most people" framing'}


def forest(ax, data, exp, key, series, task="prefer", labels=None):
    """series: list of (layout, framing). Returns the handles for a legend."""
    n = len(data.models)
    offsets = np.linspace(-0.18, 0.18, len(series)) if len(series) > 1 else [0.0]
    handles = []
    for (layout, framing), off in zip(series, offsets):
        label, colour, marker = SERIES[(layout, framing if task == "prefer" else "you")]
        label = (labels or {}).get((layout, framing), label)
        for i, m in enumerate(data.models):
            r = data.get(m, exp, key, layout, framing, task)
            if r is None or pd.isna(r.estimate):
                continue
            y = n - 1 - i + off
            ax.plot([r.lo, r.hi], [y, y], color=colour, linewidth=1.8, solid_capstyle="round", zorder=3, clip_on=False)
            vis = data.visible(m, exp, layout)
            ax.plot(r.estimate, y, marker=marker, markersize=7.5, color=colour, zorder=4, clip_on=False,
                    markerfacecolor=colour if vis else SURFACE, markeredgewidth=1.6, linestyle="none")
        handles.append(plt.Line2D([], [], color=colour, marker=marker, markersize=7.5, linewidth=1.8, label=label))
    ax.set_yticks(range(n))
    ax.set_yticklabels([NICE.get(m, m) for m in reversed(data.models)])
    ax.set_ylim(-0.7, n + 1.6)
    return handles


def legend(fig, handles):
    hollow = plt.Line2D([], [], color=INK2, marker="o", markersize=7.5, markerfacecolor=SURFACE, markeredgewidth=1.6,
                        linestyle="none", label="hollow: model cannot see the manipulation")
    band = plt.Rectangle((0, 0), 1, 1, color=HUMAN_BAND, label="people (dashed line: estimate)")
    fig.legend(handles=handles + [hollow, band], loc="upper center", ncol=4, frameon=False, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0))


def save(fig, out, name):
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(out / name)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="test")
    a = ap.parse_args()
    d, h = Data(a.tag), human_effects()
    out = ROOT / "reports" / "figures" / a.tag
    # Labels for the human bands sit in a header strip inside the axes, above the top model row.
    ROW1, ROW2 = len(d.models) - 0.15, len(d.models) + 0.75

    # ---- E1 balance
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3), sharey=True, gridspec_kw={"wspace": 0.08})
    ax = axes[0]
    style(ax, (-1, 1), "r (balance score, preference)   negative = prefers balance", chance=0)
    ind = [h[("apb", k)] for k in ("hf_e2_indiv_circles", "hf_e2_indiv_hexagons")]
    mean_ind = np.mean([x["estimate"] for x in ind])
    sd_ind = np.mean([x["estimate"] - x["ci_lo"] for x in ind])
    human_band(ax, mean_ind - sd_ind, mean_ind + sd_ind, None, "individual raters (mean ± 1 SD)", ROW1, light=True)
    agg = h[("apb", "hf_e2_all")]
    human_band(ax, agg["ci_lo"], agg["ci_hi"], agg["estimate"], "people, aggregate", ROW2)
    handles = forest(ax, d, "apb", "r_apb_all", [("two", "you"), ("sbs", "you")])
    ax.set_title("Correlation over images", loc="left")
    ax = axes[1]
    style(ax, (0, 1), "P(more balanced layout chosen)", chance=0.5)
    forest(ax, d, "apb", "p_balanced", [("two", "you"), ("sbs", "you")])
    ax.text(0.98, ROW1, "no human figure\n(source used ratings)", ha="right", va="bottom", fontsize=8.5, color=INK2)
    ax.set_title("Forced choice between layouts", loc="left")
    fig.suptitle("E1  Balance (Wilson & Chatterjee 2005)", x=0.12, ha="left", fontsize=12, y=1.04)
    legend(fig, handles)
    save(fig, out, "e1_balance.png")

    # ---- E2 two objects
    fig, ax = plt.subplots(figsize=(6.2, 4.3))
    style(ax, (0, 1), "P(balanced picture chosen over the 90 px shift)", chance=0.5)
    e = h[("multiobject", "p_balanced")]
    human_band(ax, e["ci_lo"], e["ci_hi"], e["estimate"], "people: .53\n(range of 8 object sets)", ROW1)
    handles = forest(ax, d, "multiobject", "p_balanced", [("two", "you"), ("two", "most")], labels=FRAMING_LABELS)
    fig.suptitle("E2  Two objects, the contested null (Leyssen et al. 2012)", x=0.02, ha="left", fontsize=12, y=1.04)
    legend(fig, handles)
    save(fig, out, "e2_two_objects.png")

    # ---- E3 one object
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3), sharey=True, gridspec_kw={"wspace": 0.08})
    ax = axes[0]
    style(ax, (0, 1), "P(inward-facing view chosen over its mirror flip)", chance=0.5)
    e = h[("framing", "p_inward")]
    human_band(ax, e["ci_lo"], e["ci_hi"], e["estimate"], "people: .74\n(range over positions)", ROW1)
    handles = forest(ax, d, "framing", "p_inward", [("two", "you"), ("two", "most")], labels=FRAMING_LABELS)
    ax.set_title("Inward bias (in-place mirror flip)", loc="left")
    ax = axes[1]
    style(ax, (0, 1), "P(centre chosen over a quarter-line position)", chance=0.5)
    human_band(ax, 0.5, 1.0, None, "people: above .50\n(no proportion published)", ROW1, light=True)
    forest(ax, d, "framing", "p_centre", [("two", "you"), ("two", "most")])
    ax.set_title("Centre bias, symmetrical objects", loc="left")
    fig.suptitle("E3  One object in a frame (Palmer, Gardner & Wickens 2008), two-image layout", x=0.12, ha="left",
                 fontsize=12, y=1.04)
    legend(fig, handles)
    save(fig, out, "e3_one_object.png")

    # ---- E4 colour
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3), sharey=True, gridspec_kw={"wspace": 0.08})
    ax = axes[0]
    style(ax, (0, 1), "P(red version named heavier than yellow)", chance=0.5)
    human_band(ax, 0.5, 1.0, None, "people: red rated heavier\n(direction only)", ROW1, light=True)
    handles = forest(ax, d, "colour", "weight_red_vs_yellow_anchor", [("two", "plain"), ("sbs", "plain")], task="weight")
    ax.set_title("Which looks heavier (the source's question)", loc="left")
    ax = axes[1]
    style(ax, (0, 1), "P(red version preferred over yellow)", chance=0.5)
    forest(ax, d, "colour", "prefer_red_vs_yellow_anchor", [("two", "you"), ("sbs", "you")])
    ax.text(0.98, ROW1, "no human figure\n(source asked no preference)", ha="right", va="bottom", fontsize=8.5, color=INK2)
    ax.set_title("Which is more pleasing", loc="left")
    fig.suptitle("E4  Colour swap in a grid (after Locher et al. 2005)", x=0.12, ha="left", fontsize=12, y=1.04)
    legend(fig, handles)
    save(fig, out, "e4_colour.png")

    # ---- E5 proportion (control, no anchor)
    fig, ax = plt.subplots(figsize=(6.2, 4.3))
    style(ax, (0, 1), "P(less altered grid chosen)", chance=0.5)
    ax.text(0.98, ROW1, "control: no human anchor\n(.50 = indifferent)", ha="right", va="bottom", fontsize=8.5, color=INK2)
    handles = forest(ax, d, "proportion", "p_less_altered", [("two", "you"), ("sbs", "you")])
    fig.suptitle("E5  Altered proportions (after McManus et al. 1993)", x=0.02, ha="left", fontsize=12, y=1.04)
    legend(fig, handles)
    save(fig, out, "e5_proportion.png")

    # ---- dose response: one row per experiment, one column per model (primary layout, "you")
    rows = [("apb", [("p_balanced_dose_0_12", "<12"), ("p_balanced_dose_12_25", "12-25"), ("p_balanced_dose_25_40", "25-40"),
                     ("p_balanced_dose_40_100", "40+")], "E1: score difference", None),
            ("multiobject", [("p_balanced_shift_45", "45"), ("p_balanced_shift_90", "90"), ("p_balanced_shift_135", "135")],
             "E2: shift (px)", {"p_balanced_shift_90": "p_balanced"}),
            ("framing", [("p_inward_ecc_8", "8"), ("p_inward_ecc_17", "17"), ("p_inward_ecc_25", "25")],
             "E3: % from centre", {"p_inward_ecc_8": "p_inward_ecc_8", "p_inward_ecc_17": "p_inward_ecc_17",
                                   "p_inward_ecc_25": "p_inward_ecc_25"})]
    nm = len(d.models)
    fig, axes = plt.subplots(3, nm, figsize=(1.75 * nm + 1, 6.6), sharey=True, gridspec_kw={"hspace": 0.75, "wspace": 0.12})
    for r, (exp, keys, xlabel, hmap) in enumerate(rows):
        for c, m in enumerate(d.models):
            ax = axes[r, c]
            xs = np.arange(len(keys))
            est, lo, hi = [], [], []
            for k, _ in keys:
                v = d.get(m, exp, k, "two", "you")
                est.append(np.nan if v is None else v.estimate)
                lo.append(np.nan if v is None else v.lo)
                hi.append(np.nan if v is None else v.hi)
            vis = d.visible(m, exp, "two")
            ax.fill_between(xs, lo, hi, color=BLUE, alpha=0.15, linewidth=0)
            ax.plot(xs, est, color=BLUE, linewidth=1.8, marker="o", markersize=5,
                    markerfacecolor=BLUE if vis else SURFACE, markeredgewidth=1.4)
            if hmap:
                hx = [i for i, (k, _) in enumerate(keys) if k in hmap]
                hy = [h[(exp, hmap[k])]["estimate"] for k, _ in keys if k in hmap]
                ax.plot(hx, hy, linestyle="none", marker="_", markersize=14, markeredgewidth=2.2, color=INK)
            ax.axhline(0.5, color=MUTED, linewidth=0.9)
            ax.set_ylim(0, 1)
            ax.set_xticks(xs)
            ax.set_xticklabels([lab for _, lab in keys], fontsize=7.5)
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            ax.spines["left"].set_color("#c3c2b7")
            ax.spines["bottom"].set_color("#c3c2b7")
            ax.tick_params(axis="both", labelsize=7.5)
            if r == 0:
                ax.set_title(NICE.get(m, m), fontsize=8.5)
            if c == 0:
                ax.set_ylabel("P(reference chosen)", fontsize=8)
            if c == nm // 2:
                ax.set_xlabel(xlabel, fontsize=8.5)
    fig.suptitle("Dose response, two-image layout. Black dash: people. Hollow points: model cannot see the manipulation.",
                 x=0.02, ha="left", fontsize=10.5, y=0.99)
    save(fig, out, "dose_response.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
