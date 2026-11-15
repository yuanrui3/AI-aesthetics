"""The model-side counterpart of each paper's statistic.

Every function takes the per-pair table for ONE model, ONE layout and ONE framing
(``analysis.prefer_by_pair`` joined to the manifest) and returns rows of

    {experiment, key, label, estimate, lo, hi, n, unit}

where [lo, hi] is a 95% bootstrap interval over stimuli. Pairs that share images
are resampled together: the bootstrap draws whole clusters (a family in E1, a
unit in E2, an icon in E3, a layout in E4 and E5) with replacement.

Two versions of a choice are used throughout:
  choice  1 if the bias-cancelled preference (mean log-odds over the four
          counterbalanced presentations) favours the reference, else 0
  pref    that mean log-odds itself (graded)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .manifest import ROOT, read_manifest

N_BOOT = 2000
NAN3 = (float("nan"), float("nan"), float("nan"))


def manifest_table(split: str) -> pd.DataFrame:
    """One row per pair with its manifest fields and flattened scalar params."""
    rows = []
    for man in sorted((ROOT / "stimuli").glob(f"*/{split}/pairs.jsonl")):
        for p in read_manifest(man):
            row = {"pair_id": p.pair_id, "kind": p.kind, "condition": p.condition, "dose": p.dose,
                   "cluster": p.cluster, "human_direction": p.human_direction}
            row.update({f"p_{k}": v for k, v in p.params.items() if not isinstance(v, (dict, list))})
            rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------------------------ bootstrap core
def _draws(k: int, seed: int) -> np.ndarray:
    return np.random.default_rng(seed).integers(0, k, size=(N_BOOT, k))


def _ci(est: float, boots: np.ndarray) -> tuple[float, float, float]:
    boots = boots[np.isfinite(boots)]
    if len(boots) == 0:
        return est, float("nan"), float("nan")
    lo, hi = np.quantile(boots, [0.025, 0.975])
    return float(est), float(lo), float(hi)


def boot_ratio(cluster, num, den=None, seed: int = 0) -> tuple[float, float, float]:
    """sum(num) / sum(den) over rows (den = 1 gives a mean), resampling clusters."""
    num = np.asarray(num, float)
    if len(num) == 0:
        return NAN3
    den = np.ones_like(num) if den is None else np.asarray(den, float)
    codes, uniq = pd.factorize(np.asarray(cluster))
    k = len(uniq)
    s_num = np.bincount(codes, weights=num, minlength=k)
    s_den = np.bincount(codes, weights=den, minlength=k)
    est = s_num.sum() / s_den.sum()
    if k < 2:
        return float(est), float("nan"), float("nan")
    idx = _draws(k, seed)
    with np.errstate(invalid="ignore", divide="ignore"):
        return _ci(est, s_num[idx].sum(axis=1) / s_den[idx].sum(axis=1))


def _rowwise_r(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    xc, yc = x - x.mean(axis=1, keepdims=True), y - y.mean(axis=1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (xc * yc).sum(axis=1) / np.sqrt((xc ** 2).sum(axis=1) * (yc ** 2).sum(axis=1))


def boot_corr(x: np.ndarray, y: np.ndarray, seed: int = 0) -> tuple[float, float, float]:
    """Pearson r over all entries of x, y (shape: clusters x items), resampling clusters."""
    k = x.shape[0]
    if k == 0 or x.size < 3:
        return NAN3
    est = _rowwise_r(x.reshape(1, -1), y.reshape(1, -1))[0]
    if k < 2:
        return float(est), float("nan"), float("nan")
    idx = _draws(k, seed)
    return _ci(est, _rowwise_r(x[idx].reshape(N_BOOT, -1), y[idx].reshape(N_BOOT, -1)))


def _row(exp, key, label, res, n, unit):
    return {"experiment": exp, "key": key, "label": label, "estimate": res[0], "lo": res[1], "hi": res[2], "n": int(n), "unit": unit}


def _mean(d: pd.DataFrame, col: str = "choice_ref"):
    return boot_ratio(d.cluster.values, d[col].values)


# ------------------------------------------------------------------ E1: APB
def apb_scale(d: pd.DataFrame, value: str = "pref") -> pd.DataFrame:
    """Per-image scale value within each family: mean preference for the image over
    the four other layouts of the same seven elements (the least-squares solution
    for a complete paired-comparison design). ``value`` = 'pref' (graded log-odds)
    or 'choice' (wins minus losses)."""
    v = d["pref"] if value == "pref" else d["choice_ref"] * 2 - 1
    a = pd.DataFrame({"family": d.p_family, "shape": d.p_shape, "level": d.p_level_ref, "apb": d.p_apb_ref, "dcm": d.p_dcm_ref, "s": v})
    b = pd.DataFrame({"family": d.p_family, "shape": d.p_shape, "level": d.p_level_alt, "apb": d.p_apb_alt, "dcm": d.p_dcm_alt, "s": -v})
    img = pd.concat([a, b]).groupby(["family", "level"], as_index=False).agg(
        shape=("shape", "first"), apb=("apb", "first"), dcm=("dcm", "first"), s=("s", "sum"))
    img["s"] = img["s"] / 5.0
    return img


def _family_arrays(img: pd.DataFrame, measure: str) -> tuple[np.ndarray, np.ndarray]:
    img = img.sort_values(["family", "level"])
    k = img.family.nunique()
    return img[measure].values.reshape(k, -1), img.s.values.reshape(k, -1)


def apb_effects(d: pd.DataFrame) -> list[dict]:
    d = d[(d.experiment == "apb") & (d.kind == "manipulation")].copy()
    out = []
    img = apb_scale(d, "pref")
    for shape, lab in ((None, "all"), ("circle", "circles"), ("hexagon", "hexagons")):
        sub = img if shape is None else img[img["shape"] == shape]
        out.append(_row("apb", f"r_apb_{lab}", f"r(balance score, preference scale value), {lab}",
                        boot_corr(*_family_arrays(sub, "apb")), len(sub), "images"))
    out.append(_row("apb", "r_dcm_all", "r(centre-of-mass deviation, preference scale value), all",
                    boot_corr(*_family_arrays(img, "dcm")), len(img), "images"))
    out.append(_row("apb", "r_apb_all_hard", "r(balance score, comparisons won minus lost), all",
                    boot_corr(*_family_arrays(apb_scale(d, "choice"), "apb")), len(img), "images"))
    out.append(_row("apb", "p_balanced", "P(more balanced member chosen), all pairs", _mean(d), len(d), "pairs"))
    # dose-response: by size of the balance-score difference, and the paper's "plateau below 20"
    for lo, hi in ((0, 12), (12, 25), (25, 40), (40, 100)):
        g = d[(d.dose >= lo) & (d.dose < hi)]
        out.append(_row("apb", f"p_balanced_dose_{lo}_{hi}", f"P(more balanced chosen), score difference {lo}-{hi}",
                        _mean(g), len(g), "pairs"))
    g = d[d.p_apb_alt < 20]
    out.append(_row("apb", "p_balanced_both_below_20", "P(more balanced chosen), both scores below 20 (human plateau)",
                    _mean(g), len(g), "pairs"))
    out.append(_row("apb", "slope_pref_per_point", "Slope of preference (log-odds) on score difference, through origin",
                    boot_ratio(d.cluster.values, d.pref.values * d.dose.values, d.dose.values ** 2), len(d), "pairs"))
    return out


# ---------------------------------------------------------- E2: multi-object
def multiobject_effects(d: pd.DataFrame) -> list[dict]:
    d = d[(d.experiment == "multiobject") & (d.kind == "manipulation")].copy()
    out = []
    bal = d[d.condition == "balance"]
    out.append(_row("multiobject", "p_balanced", "P(balanced chosen over 90 px shift)  [human anchor]", _mean(bal), len(bal), "pairs"))
    out.append(_row("multiobject", "pref_balanced_90", "Preference for balanced over 90 px shift (log-odds)",
                    _mean(bal, "pref"), len(bal), "pairs"))
    for dist in (1, 3):
        g = bal[bal.p_dist_ref == dist]
        out.append(_row("multiobject", f"p_balanced_90_d{dist}", f"P(balanced chosen), objects {dist} unit(s) apart", _mean(g), len(g), "pairs"))
    for sign, lab in ((-1, "left"), (1, "right")):
        g = bal[np.sign(bal.p_shift) == sign]
        out.append(_row("multiobject", f"p_balanced_90_{lab}", f"P(balanced chosen), twin shifted {lab}", _mean(g), len(g), "pairs"))
    both = d[d.condition.isin(["balance", "dose"])]
    for mag in (45, 90, 135):
        g = both[both.dose == mag]
        out.append(_row("multiobject", f"p_balanced_shift_{mag}", f"P(balanced chosen), shift {mag} px", _mean(g), len(g), "pairs"))
    dist = d[d.condition == "distance"]
    out.append(_row("multiobject", "p_closer_unrelated", "P(closer arrangement chosen), both balanced  [human: unrelated pairs]",
                    _mean(dist), len(dist), "pairs"))
    return out


# --------------------------------------------------------------- E3: framing
def framing_effects(d: pd.DataFrame) -> list[dict]:
    d = d[(d.experiment == "framing") & (d.kind == "manipulation")].copy()
    out = []
    flip = d[d.condition == "flip"]
    off = flip[flip.p_pos_ref != 50]
    out.append(_row("framing", "p_inward", "P(inward-facing chosen over outward-facing), six off-centre positions",
                    _mean(off), len(off), "pairs"))
    for kind in ("object", "abstract"):
        g = off[off.p_icon_kind == kind]
        out.append(_row("framing", f"p_inward_{kind}", f"P(inward-facing chosen), {kind} icons", _mean(g), len(g), "pairs"))
    # P(right-facing chosen) by position: the curve of the source's Figure 5
    right = np.where(flip.p_facing_ref == "R", flip.choice_ref, 1 - flip.choice_ref)
    for pos, key in zip(sorted(flip.p_pos_ref.unique()), (25, 33, 42, 50, 58, 67, 75)):
        m = (flip.p_pos_ref == pos).values
        out.append(_row("framing", f"p_right_facing_pos_{key}", f"P(right-facing chosen over left-facing) at {key}%",
                        boot_ratio(flip.cluster.values[m], right[m]), m.sum(), "pairs"))
    for ecc, key in zip(sorted(off.dose.unique()), (8, 17, 25)):
        g = off[off.dose == ecc]
        out.append(_row("framing", f"p_inward_ecc_{key}", f"P(inward-facing chosen), {key}% from centre", _mean(g), len(g), "pairs"))

    # Position profile: share of same-facing comparisons each position wins (source Figure 6),
    # left-facing objects mirrored so that index 0 is always furthest on the facing-in side.
    pos = d[d.condition == "position"]
    if len(pos):
        codes, uniq = pd.factorize(pos.cluster.values)
        k = len(uniq)
        wins, n = np.zeros((k, 7)), np.zeros((k, 7))
        for c, a, b, ch, f in zip(codes, pos.p_idx_ref.astype(int), pos.p_idx_alt.astype(int), pos.choice_ref, pos.p_facing):
            if f == "L":
                a, b = 6 - a, 6 - b
            wins[c, a] += ch
            wins[c, b] += 1 - ch
            n[c, a] += 1
            n[c, b] += 1
        est = wins.sum(0) / n.sum(0)
        idx = _draws(k, 0) if k >= 2 else None
        prof = (wins[idx].sum(1) / n[idx].sum(1)) if idx is not None else np.full((1, 7), np.nan)
        for j in range(7):
            lab = "facing-in side" if j < 3 else "centre" if j == 3 else "facing-out side"
            out.append(_row("framing", f"profile_{j}", f"Share of same-facing comparisons won, position {j} ({lab})",
                            _ci(est[j], prof[:, j]), len(pos), "pairs"))
        out.append(_row("framing", "profile_in_minus_out", "Facing-in side minus facing-out side, same-facing comparisons",
                        _ci(est[:3].mean() - est[4:].mean(), prof[:, :3].mean(1) - prof[:, 4:].mean(1)), len(pos), "pairs"))

    cen = d[(d.condition == "centre") & (d.human_direction == "ref")]
    out.append(_row("framing", "p_centre", "P(centre chosen over a quarter-line position), symmetrical objects", _mean(cen), len(cen), "pairs"))
    lr = d[(d.condition == "centre") & (d.human_direction == "none")]
    out.append(_row("framing", "p_left_over_right", "P(left quarter chosen over right quarter), symmetrical objects", _mean(lr), len(lr), "pairs"))
    return out


# ---------------------------------------------------------------- E4: colour
def colour_effects(d: pd.DataFrame, question: str = "weight") -> list[dict]:
    """``d`` must come from prefer_by_pair(df, task=question). ``question`` is 'weight'
    (the source's variable; direction-only anchor) or 'prefer' (no human anchor)."""
    d = d[(d.experiment == "colour") & (d.kind == "manipulation")].copy()
    what = "named as heavier" if question == "weight" else "preferred"
    out = []
    for contrast in ("red_vs_yellow", "red_vs_blue", "blue_vs_yellow"):
        a, b = contrast.split("_vs_")
        for level in ("small", "medium", "large"):
            g = d[(d.condition == contrast) & (d.p_size_level == level)]
            out.append(_row("colour", f"{question}_{contrast}_{level}", f"P({a} version {what} over {b}), largest area {level}",
                            _mean(g), len(g), "pairs"))
    g = d[d.human_direction == "ref"]
    tag = "  [human anchor: direction only]" if question == "weight" else "  [no human anchor]"
    out.append(_row("colour", f"{question}_red_vs_yellow_anchor", f"P(red version {what} over yellow), largest area 8-24% of field{tag}",
                    _mean(g), len(g), "pairs"))
    return out


# ------------------------------------------------------------ E5: proportion
def proportion_effects(d: pd.DataFrame) -> list[dict]:
    d = d[(d.experiment == "proportion") & (d.kind == "manipulation")].copy()
    out = []
    for cond, lab in (("G_vs_G1", "generated over small alteration"), ("G_vs_G2", "generated over large alteration"),
                      ("G1_vs_G2", "small over large alteration")):
        g = d[d.condition == cond]
        out.append(_row("proportion", f"p_{cond}", f"P({lab} chosen)  [no human anchor]", _mean(g), len(g), "pairs"))
    out.append(_row("proportion", "p_less_altered", "P(less altered member chosen), all pairs  [no human anchor]", _mean(d), len(d), "pairs"))
    return out


EFFECT_FUNCS = {"apb": apb_effects, "multiobject": multiobject_effects, "framing": framing_effects,
                "colour": colour_effects, "proportion": proportion_effects}
