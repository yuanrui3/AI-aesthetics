"""Every human effect size quoted in docs/experiments.md, derived from the statistics
the papers print. Nothing here is fitted or estimated from a figure unless it says so.

    uv run python scripts/human_effects.py            # print the table
    uv run python scripts/human_effects.py --json     # machine-readable, used by the report
"""
from __future__ import annotations

import json
import math
import sys

from aesx.stats import fisher_ci

EFFECTS: list[dict] = []


def add(exp: str, key: str, label: str, stat: str, est: float, lo: float | None, hi: float | None,
        n: str, source: str, derivation: str) -> None:
    EFFECTS.append(dict(experiment=exp, key=key, label=label, statistic=stat, estimate=est,
                        ci_lo=lo, ci_hi=hi, n=n, source=source, derivation=derivation))


# ---------------------------------------------------------------- E1: APB
# Wilson & Chatterjee (2005). Regressions of mean preference rating (1-5) on the
# objective balance score across stimuli. The paper prints R^2; the slope is
# negative (higher score = less balanced = liked less), so r = -sqrt(R^2).
# CI: Fisher z over the number of stimuli in the regression.
for key, label, r2, n_stim, n_raters, where in [
    ("e2_circles", "Exp 2 (after outlier removal), circles", 0.73, 65, 30, "Table 2"),
    ("e2_hexagons", "Exp 2 (after outlier removal), hexagons", 0.78, 65, 30, "Table 2"),
    ("e2_squares", "Exp 2 (after outlier removal), squares", 0.44, 65, 30, "Table 2"),
    ("e2_overall", "Exp 2 (after outlier removal), all shapes", 0.54, 195, 30, "Table 2"),
    ("e1_circles", "Exp 1 (unselected set), circles", 0.49, 72, 10, "Table 1b"),
    ("e1_hexagons", "Exp 1 (unselected set), hexagons", 0.47, 72, 10, "Table 1b"),
    ("e1_squares", "Exp 1 (unselected set), squares", 0.39, 72, 10, "Table 1b"),
    ("e1_overall", "Exp 1 (unselected set), all shapes", 0.27, 216, 10, "Table 1b"),
]:
    r, lo, hi = fisher_ci(-math.sqrt(r2), n_stim)
    add("apb", key, label, "Pearson r, balance score vs mean preference rating, over stimuli", r, lo, hi,
        f"{n_stim} stimuli, {n_raters} raters", f"Wilson & Chatterjee 2005, {where}: R2 = {r2}",
        "r = -sqrt(R2); 95% CI by Fisher z with n = number of stimuli")


# Hübner & Fillinger (2016, Front. Psychol. 7:335): the same 130 circle and hexagon
# images with new raters (Exp 2, N = 21), and 144 newly generated images (Exp 3, N = 23).
# Aggregate r is over images; the individual figures are the mean and SD, across raters,
# of each rater's own correlation (their Tables 7, 8, 10 and p.11).
for key, label, r, n_stim, n_raters in [
    ("hf_e2_circles", "Hübner & Fillinger Exp 2, circles (aggregate)", -0.882, 65, 21),
    ("hf_e2_hexagons", "Hübner & Fillinger Exp 2, hexagons (aggregate)", -0.928, 65, 21),
    ("hf_e2_all", "Hübner & Fillinger Exp 2, all 130 (aggregate)", -0.867, 130, 21),
    ("hf_e3_all", "Hübner & Fillinger Exp 3, 144 generated images (aggregate)", -0.737, 144, 23),
]:
    _, lo, hi = fisher_ci(r, n_stim)
    add("apb", key, label, "Pearson r, balance score vs mean liking, over images", r, lo, hi,
        f"{n_stim} images, {n_raters} raters", "Hübner & Fillinger 2016, Tables 8 and 10 (printed r)",
        "95% CI by Fisher z with n = number of images")
for key, label, mean, sd, n in [
    ("hf_e2_indiv_circles", "Individual raters, Exp 2 circles: mean of each rater's r", -0.423, 0.363, 21),
    ("hf_e2_indiv_hexagons", "Individual raters, Exp 2 hexagons: mean of each rater's r", -0.459, 0.351, 21),
    ("hf_e3_indiv_circles", "Individual raters, Exp 3 circles: mean of each rater's r", -0.310, 0.356, 23),
    ("hf_e3_indiv_hexagons", "Individual raters, Exp 3 hexagons: mean of each rater's r", -0.241, 0.330, 23),
]:
    # the band shown for individuals is mean +/- 1 SD across raters (where single raters fall), not a CI of the mean
    add("apb", key, label, "mean (+/- 1 SD across raters) of within-rater r", mean, mean - sd, mean + sd,
        f"{n} raters", "Hübner & Fillinger 2016, Table 7 and p.11 (printed mean and SD)",
        "interval shown = mean +/- 1 SD across raters")

# ------------------------------------------------------ E2: two objects
# Leyssen et al. (2012) Exp 5, N = 20. Only "F(1,19) < 1 for all quartets" is printed.
# Proportions are DIGITISED from Fig. 14 with scripts/digitise_figures.py (about +/- .006).
FIG14B = {"related": (0.539, 0.539, 0.544, 0.561), "unrelated": (0.506, 0.489, 0.483, 0.561)}
FIG14A = {"related": (0.783, 0.856, 0.817, 0.839), "unrelated": (0.422, 0.494, 0.417, 0.500)}
_all_b = FIG14B["related"] + FIG14B["unrelated"]
add("multiobject", "p_balanced", "P(balanced picture chosen over the 90 px shift), all pairs",
    "mean proportion over participants and object sets", sum(_all_b) / 8, min(_all_b), max(_all_b),
    "20 participants", "Leyssen et al. 2012, Fig. 14b (digitised); text p.46: F(1,19) < 1 in every object set",
    "mean of the eight bars; interval shown = RANGE of the eight bars, NOT a confidence interval "
    "(no SE is printed; F < 1 means each set's mean is within one SE of .50)")
for rel in ("related", "unrelated"):
    add("multiobject", f"p_balanced_{rel}", f"P(balanced chosen), {rel} object pairs", "mean proportion",
        sum(FIG14B[rel]) / 4, min(FIG14B[rel]), max(FIG14B[rel]), "20 participants",
        "Leyssen et al. 2012, Fig. 14b (digitised)", "mean and range of four bars; not a confidence interval")
    add("multiobject", f"p_closer_{rel}", f"P(smaller inter-object distance chosen), {rel} object pairs",
        "mean proportion", sum(FIG14A[rel]) / 4, min(FIG14A[rel]), max(FIG14A[rel]), "20 participants",
        "Leyssen et al. 2012, Fig. 14a (digitised); printed F(1,19) = 217.55, 22.42, 17.50, 17.69 (related), "
        "5.92, 0.05, 5.32, 0.01 (unrelated)", "mean and range of four bars; not a confidence interval")

# ------------------------------------------------------- E3: one object
# Palmer, Gardner & Wickens (2008). Values DIGITISED with scripts/digitise_figures.py.
# Exp 2 (17 analysed), Fig. 5: % choosing each view over its reflection at the same
# position; the two markers at a position must sum to 100 and do to within 0.7.
POS = (25, 33, 42, 50, 58, 67, 75)
FIG5_HI_LO = ((87.3, 13.0), (68.8, 30.5), (69.3, 30.0), (56.1, 43.2), (70.6, 28.7), (70.0, 29.3), (75.6, 23.8))
# at 25-50% the higher marker is the right-facing view, at 58-75% it is the left-facing one
P_RIGHT = [hi / (hi + lo) if p <= 50 else lo / (hi + lo) for p, (hi, lo) in zip(POS, FIG5_HI_LO)]
P_INWARD = [hi / (hi + lo) for p, (hi, lo) in zip(POS, FIG5_HI_LO) if p != 50]
for p, v in zip(POS, P_RIGHT):
    add("framing", f"p_right_facing_pos_{p}", f"P(right-facing chosen over left-facing) at {p}%", "mean proportion",
        v, None, None, "17 participants, 6 objects", "Palmer et al. 2008, Fig. 5 (digitised)",
        "marker / (sum of the two markers at that position)")
add("framing", "p_inward", "P(inward-facing chosen over outward-facing), six off-centre positions", "mean proportion",
    sum(P_INWARD) / 6, min(P_INWARD), max(P_INWARD), "17 participants, 6 objects",
    "Palmer et al. 2008, Fig. 5 (digitised); printed: position F(6,96) = 38.11, linear F(1,16) = 67.68",
    "mean of six positions; interval shown = RANGE over positions, not a confidence interval")
for ecc, idx in ((8, (2, 3)), (17, (1, 4)), (25, (0, 5))):
    v = [P_INWARD[i] for i in idx]
    add("framing", f"p_inward_ecc_{ecc}", f"P(inward-facing chosen), {ecc}% from centre", "mean proportion",
        sum(v) / 2, None, None, "17 participants", "Palmer et al. 2008, Fig. 5 (digitised)", "mean of the two sides")
# Fig. 6: % of same-facing comparisons won at each position (right-facing, then left-facing).
# The two markers at 50% overlap and are read as one. The seven values of a curve should
# sum to 350 and sum to 357 and 365, so individual points are good to about +/- 2.
FIG6_RIGHT = (53.9, 61.4, 65.9, 65.2, 51.5, 36.3, 23.2)
FIG6_LEFT = (21.9, 38.5, 53.2, 65.2, 69.7, 63.7, 53.2)
PROFILE = [(r + l) / 2 for r, l in zip(FIG6_RIGHT, reversed(FIG6_LEFT))]  # index 0 = furthest on the facing-in side
for k, v in enumerate(PROFILE):
    add("framing", f"profile_{k}", f"Share of same-facing comparisons won, position {k} (0 = facing-in side)",
        "mean percentage / 100", v / 100, None, None, "17 participants, 6 objects",
        "Palmer et al. 2008, Fig. 6 (digitised)", "mean of the right-facing curve and the mirrored left-facing curve")
add("framing", "profile_in_minus_out", "Facing-in side minus facing-out side, same-facing comparisons",
    "difference of mean proportions", (sum(PROFILE[:3]) - sum(PROFILE[4:])) / 300, None, None, "17 participants",
    "Palmer et al. 2008, Fig. 6 (digitised); printed: facing x position F(6,96) = 19.05",
    "mean of positions 0-2 minus mean of positions 4-6")
# Exp 1 (N = 9): centre bias for symmetrical front views. Printed test only; the figure's
# front-view points do not sum to a valid set of win percentages, so no proportion is given.
add("framing", "p_centre", "P(centre chosen over a quarter-line position), symmetrical objects",
    "direction only", float("nan"), None, None, "9 participants, 10 objects",
    "Palmer et al. 2008, Exp 1: centre chosen more than either side, F(1,8) = 11.99, p < .01",
    "no proportion available; direction = above .50")

# --------------------------------------------------------- E4: colour
# Locher, Overbeeke & Stappers (2005). NOT YET CHECKED AGAINST THE PAPER BY ME: values as
# reported by a delegated reader from the full text. Mean 1-10 weight rating of the largest
# area by its colour, pooled over 60 participants (their Table 1), compositions 1-6.
TABLE1_RED = ((6.59, 6.39), (6.06, 6.12), (8.93, 8.88), (7.47, 7.45), (7.97, 7.94), (7.02, 7.17))
TABLE1_YELLOW = ((5.52, 5.51), (5.38, 5.45), (8.31, 8.42), (6.82, 6.51), (7.29, 7.08), (6.62, 6.74))
diffs = [sum(r) / 2 - sum(y) / 2 for r, y in zip(TABLE1_RED, TABLE1_YELLOW)]
add("colour", "weight_red_minus_yellow", "Rated weight of the largest area, red minus yellow (1-10 scale)",
    "difference of mean ratings; direction-only anchor for the forced choice", sum(diffs) / 6, min(diffs), max(diffs),
    "60 participants, 6 compositions", "Locher et al. 2005, Table 1 (READER-REPORTED, unchecked)",
    "mean and RANGE over the six compositions; reliable in four of six; no forced-choice proportion exists")

# ------------------------------------------------------ E5: proportion
# McManus, Cheema & Stoker (1993). READER-REPORTED, unchecked. Quoted for context only:
# the effect is defined against real paintings and is NOT an anchor for generated grids.
for key, label, k, n in [("m_vs_p1", "Original chosen over small alteration (real paintings)", 722, 1293),
                         ("m_vs_p2", "Original chosen over large alteration (real paintings)", 712, 1298),
                         ("p1_vs_p2", "Small alteration chosen over large (real paintings)", 672, 1300)]:
    add("proportion", key, label, "share of judgements (context only, not an anchor)", k / n, None, None,
        "52 participants, 25 paintings", "McManus et al. 1993, p.89 (READER-REPORTED, unchecked)",
        f"{k}/{n}; no interval given because judgements are clustered within participants")


def main() -> int:
    if "--json" in sys.argv:
        print(json.dumps(EFFECTS, indent=2))
        return 0
    for e in EFFECTS:
        ci = "" if e["ci_lo"] is None else f"  [{e['ci_lo']:+.3f}, {e['ci_hi']:+.3f}]"
        print(f"{e['experiment']:8s} {e['key']:14s} {e['estimate']:+.3f}{ci}   n = {e['n']}")
        print(f"{'':23s} {e['label']} | {e['source']} | {e['derivation']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
