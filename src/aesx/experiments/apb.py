"""E1. Balance: Wilson & Chatterjee (2005), Assessment of Preference for Balance.

Source stimuli: a 750 x 750 px white square holding seven black elements of
varying sizes, all circles or all hexagons, hand-arranged to span balance scores
from 3.6 to 65.9 (lower = more balanced). Source task: 1-5 preference ratings.

Here: a *family* is one set of seven elements arranged at five balance levels.
Each level is derived from the previous one by moving elements (a shift of
visual weight) until the score reaches the next target, so all members of a
family contain exactly the same shapes. Every pair of levels within a family is
a forced-choice pair (10 per family): reference = the more balanced member,
manipulated twin = the less balanced one, dose = difference in balance score.
"""
from __future__ import annotations

import math
from itertools import combinations

import numpy as np
from PIL import Image

from ..balance import apb_measures, apb_score, dcm, ink
from ..manifest import Pair, rng_for, save_pair
from ..render import BLACK, WHITE, Canvas

NAME = "apb"
TITLE = "E1 Balance (Wilson & Chatterjee 2005)"
SIDE = 512  # px; the source used 750 (geometry is specified relative to the side)
N_ELEM = 7
LEVELS = (6.0, 15.0, 25.0, 40.0, 58.0)  # target balance scores (source range 3.6-65.9)
TOL = 1.0  # search tolerance around each target, in score points
# Minimum displacement of the centre of mass (/ side) required at each level; -1 = no constraint.
MIN_SHIFT = (-1.0, 0.03, 0.07, 0.13, 0.22)
D_RANGE = (0.07, 0.20)  # element diameter / side
EDGE = 0.02  # min distance from an element to the frame, / side
GAP = 0.012  # min gap between elements, / side
SHAPES = ("circle", "hexagon")
PAIRS_PER_FAMILY = math.comb(len(LEVELS), 2)
UNITS = {"dev": 8, "test": 20}  # families -> 80 dev pairs, 200 test pairs (+ identical controls)


def caption(p: Pair) -> str:
    return f"{p.params['shape']}  balance {p.params['apb_ref']:.1f} vs {p.params['apb_alt']:.1f}  (dose {p.dose:.1f})"


def draw(elems: np.ndarray, shape: str, side: int = SIDE, ss: int = 4) -> Image.Image:
    """elems: rows of (cx, cy, diameter) in units of the side."""
    c = Canvas(side, side, WHITE, ss)
    for cx, cy, d in elems:
        if shape == "circle":
            c.circle(cx * side, cy * side, d / 2 * side, BLACK)
        else:  # regular hexagon inscribed in the same circle, flat top and bottom
            c.regular_polygon(cx * side, cy * side, d / 2 * side, 6, BLACK)
    return c.image()


def _quick_score(elems: np.ndarray, shape: str) -> float:
    return apb_score(ink(draw(elems, shape, side=128, ss=2)))


def _legal(elems: np.ndarray, i: int, p: np.ndarray) -> bool:
    r = elems[i, 2] / 2
    if not (EDGE + r <= p[0] <= 1 - EDGE - r and EDGE + r <= p[1] <= 1 - EDGE - r):
        return False
    for j in range(len(elems)):
        if j != i and not np.isnan(elems[j, 0]):
            if math.hypot(p[0] - elems[j, 0], p[1] - elems[j, 1]) < r + elems[j, 2] / 2 + GAP:
                return False
    return True


def _random_layout(rng: np.random.Generator, diam: np.ndarray) -> np.ndarray | None:
    elems = np.full((len(diam), 3), np.nan)
    elems[:, 2] = diam
    for i in np.argsort(-diam):  # largest first
        for _ in range(200):
            r = diam[i] / 2
            p = rng.uniform(EDGE + r, 1 - EDGE - r, size=2)
            if _legal(elems, i, p):
                elems[i, :2] = p
                break
        else:
            return None
    return elems


def _shift(elems: np.ndarray, direction: np.ndarray) -> float:
    """Displacement of the elements' centre of mass from the frame centre along ``direction`` (/ side)."""
    wts = elems[:, 2] ** 2  # area is proportional to diameter squared for both shapes
    com = (elems[:, :2] * wts[:, None]).sum(axis=0) / wts.sum()
    return float((com - 0.5) @ direction)


def _climb(rng: np.random.Generator, elems: np.ndarray, shape: str, target: float, min_shift: float,
           direction: np.ndarray, max_iter: int = 8000):
    """Move one element at a time, keeping moves that bring the layout closer to the target.

    The target is a balance score AND a minimum displacement of the centre of mass
    in the family's direction, so that a high score means weight pushed toward a
    side or corner (as in the source's Figure 3) and never a clump in the middle,
    which the APB formula would also score as "unbalanced".
    """

    def cost(e: np.ndarray, s: float) -> float:
        return abs(s - target) + 100.0 * max(0.0, min_shift - _shift(e, direction))

    elems = elems.copy()
    s = _quick_score(elems, shape)
    c = cost(elems, s)
    for _ in range(max_iter):
        if abs(s - target) <= TOL and _shift(elems, direction) >= min_shift:
            return elems
        i = int(rng.integers(len(elems)))
        step = rng.normal(0, 0.03 if rng.random() < 0.5 else 0.15, size=2)
        p = elems[i, :2] + step
        if not _legal(elems, i, p):
            continue
        trial = elems.copy()
        trial[i, :2] = p
        s2 = _quick_score(trial, shape)
        c2 = cost(trial, s2)
        if c2 < c:
            elems, s, c = trial, s2, c2
    return None


def make_family(rng: np.random.Generator, shape: str) -> list[np.ndarray]:
    """Five layouts of the same seven elements, one per balance level, each derived from the last."""
    while True:
        diam = rng.uniform(*D_RANGE, size=N_ELEM)
        theta = rng.uniform(0, 2 * math.pi)  # the direction this family's weight drifts in
        direction = np.array([math.cos(theta), math.sin(theta)])
        cur = _random_layout(rng, diam)
        if cur is None:
            continue
        layouts = []
        for target, min_shift in zip(LEVELS, MIN_SHIFT):
            cur = _climb(rng, cur, shape, target, min_shift, direction)
            if cur is None:
                break
            layouts.append(cur)
        if len(layouts) == len(LEVELS):
            return layouts


def generate(split: str, n_families: int, n_identical: int | None = None) -> list[Pair]:
    """n_families x 10 manipulation pairs, plus identical-pair controls (default 2 per family)."""
    pairs: list[Pair] = []
    out = f"stimuli/{NAME}/{split}"
    for f in range(n_families):
        rng = rng_for(NAME, split, f)
        shape = SHAPES[f % 2]
        layouts = make_family(rng, shape)
        images = [draw(e, shape) for e in layouts]
        info = []
        for e, im in zip(layouts, images):
            w = ink(im)
            info.append({"apb": round(apb_score(w), 3), "dcm": round(dcm(w), 3),
                         "measures": {k: round(v, 3) for k, v in apb_measures(w).items()},
                         "elements": np.round(e, 5).tolist()})
        paths = [f"{out}/f{f:03d}_L{k}.png" for k in range(len(LEVELS))]
        fam = f"{NAME}-{split}-f{f:03d}"
        for a, b in combinations(range(len(LEVELS)), 2):
            lo, hi = (a, b) if info[a]["apb"] <= info[b]["apb"] else (b, a)  # ref = more balanced
            p = Pair(
                experiment=NAME, pair_id=f"{fam}-L{lo}L{hi}", split=split, index=f, kind="manipulation",
                condition=shape, ref=paths[lo], alt=paths[hi],
                dose=round(info[hi]["apb"] - info[lo]["apb"], 3), human_direction="ref", cluster=fam,
                params={"shape": shape, "family": fam, "level_ref": lo, "level_alt": hi,
                        "apb_ref": info[lo]["apb"], "apb_alt": info[hi]["apb"],
                        "dcm_ref": info[lo]["dcm"], "dcm_alt": info[hi]["dcm"],
                        "ref": info[lo], "alt": info[hi]},
            )
            pairs.append(save_pair(p, images[lo], images[hi]))
        k_ident = 2 if n_identical is None else n_identical
        for k in rng.choice(len(LEVELS), size=k_ident, replace=False):
            k = int(k)
            p = Pair(
                experiment=NAME, pair_id=f"{fam}-L{k}L{k}", split=split, index=f, kind="identical",
                condition=shape, ref=paths[k], alt=paths[k], dose=0.0, human_direction="none", cluster=fam,
                params={"shape": shape, "family": fam, "level_ref": k, "level_alt": k,
                        "apb_ref": info[k]["apb"], "apb_alt": info[k]["apb"]},
            )
            pairs.append(save_pair(p, images[k], images[k]))
    return pairs
