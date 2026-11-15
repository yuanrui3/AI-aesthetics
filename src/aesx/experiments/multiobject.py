"""E2. Two objects in a frame, the contested null: Leyssen, Linsen, Sammartino & Palmer
(2012), i-Perception 3:25-49, Experiment 5.

Source: a 680 x 430 px framed picture (wall above, floor below) holding two
objects at two of six positions, 45 / 135 / 225 px either side of the centre.
A picture is "balanced" when the two objects are equidistant from the centre.
The balance comparisons pair a balanced picture with the same picture shifted
so the pair's midpoint lies 90 px (13 % of the width) left or right of centre,
keeping the distance between the objects fixed:

      C (-45, +45)    vs  A (-135, -45)   or  F (+45, +135)       1 unit apart
      D (-135, +135)  vs  B (-225, +45)   or  G (-45, +225)       3 units apart

20 participants chose "the most aesthetically pleasing"; the balanced picture
was not chosen above chance in any object set (F(1,19) < 1 each).

The source objects were photographs of everyday things in semantically related
or unrelated pairs. Here they are two plain abstract shapes, which have no
semantic relation; see docs/experiments.md for what that does to the comparison.

Pairs generated per unit (one unit = two shapes, two colours, a left/right order):
  balance   4 pairs at the source's 90 px shift (the human anchor)
  dose      4 pairs at 45 and 135 px shifts (no human anchor; response curve only)
  distance  2 pairs of balanced pictures differing in inter-object distance
"""
from __future__ import annotations

from itertools import permutations

import numpy as np
from PIL import Image

from ..icons import BY_NAME, PALETTE, draw_icon
from ..manifest import Pair, rng_for, save_pair
from ..render import Canvas

NAME = "multiobject"
TITLE = "E2 Two objects, the contested null (Leyssen et al. 2012, Exp 5)"
W, H = 680, 430  # as in the source
BORDER = 12
FRAME, WALL, FLOOR = (21, 21, 21), (236, 205, 150), (128, 72, 36)
FLOOR_FRAC = 0.40  # floor = bottom 40 % of the inner picture
STAND = 0.30  # objects stand this far down into the floor band
UNIT_PX = 90
SIZE = 80.0  # largest dimension of a shape, px (objects just clear each other at 1 unit apart)
SHAPES = {"dev": ("disc", "square", "triangle", "star"),
          "test": ("pentagon", "hexagon", "diamond", "cross", "dome", "trapezoid")}
UNITS = {"dev": 8, "test": 30}

BALANCED = {1: (-45, 45), 3: (-135, 135), 5: (-225, 225)}  # inter-object distance in units -> x offsets


def caption(p: Pair) -> str:
    q = p.params
    if p.condition == "distance":
        return f"{q['left']}+{q['right']}: {q['dist_ref']} vs {q['dist_alt']} units apart (both balanced)"
    return f"{q['left']}+{q['right']}: balanced vs shifted {q['shift']:+d} px ({q['dist_ref']} unit{'s' if q['dist_ref'] > 1 else ''} apart)"


def draw(left: str, right: str, col_left: tuple, col_right: tuple, x_left: float, x_right: float) -> Image.Image:
    c = Canvas(W, H, FRAME)
    inner_h = H - 2 * BORDER
    floor_top = BORDER + inner_h * (1 - FLOOR_FRAC)
    c.rect(BORDER, BORDER, W - BORDER, floor_top, WALL)
    c.rect(BORDER, floor_top, W - BORDER, H - BORDER, FLOOR)
    base_y = floor_top + inner_h * FLOOR_FRAC * STAND
    for name, col, x in ((left, col_left, x_left), (right, col_right, x_right)):
        icon = BY_NAME[name]
        draw_icon(c, icon, W / 2 + x, base_y, SIZE / max(1.0, icon.aspect), col, 1)
    return c.image()


def generate(split: str, n_units: int) -> list[Pair]:
    out = f"stimuli/{NAME}/{split}"
    pairs: list[Pair] = []
    combos = list(permutations(SHAPES[split], 2))  # ordered: (left shape, right shape)
    order = rng_for(NAME, split, 99_999).permutation(len(combos))
    colour_names = list(PALETTE)
    for u in range(n_units):
        rng = rng_for(NAME, split, u)
        left, right = combos[int(order[u % len(combos)])]
        cl, cr = (colour_names[int(i)] for i in rng.choice(len(colour_names), size=2, replace=False))
        fam = f"{NAME}-{split}-u{u:03d}"
        cache: dict[tuple, tuple[str, Image.Image]] = {}

        def pic(xl: float, xr: float) -> tuple[str, Image.Image]:
            key = (xl, xr)
            if key not in cache:
                cache[key] = (f"{out}/u{u:03d}_{int(xl):+04d}_{int(xr):+04d}.png",
                              draw(left, right, PALETTE[cl], PALETTE[cr], xl, xr))
            return cache[key]

        common = {"left": left, "right": right, "colour_left": cl, "colour_right": cr}

        def add(tag: str, condition: str, ref_x, alt_x, dose, direction, extra, kind="manipulation") -> None:
            (rp, rim), (ap, aim) = pic(*ref_x), pic(*alt_x)
            p = Pair(experiment=NAME, pair_id=f"{fam}-{tag}", split=split, index=u, kind=kind, condition=condition,
                     ref=rp, alt=ap, dose=dose, human_direction=direction, cluster=fam, params={**common, **extra})
            pairs.append(save_pair(p, rim, aim))

        # balance at the source's shift (both directions, both distances), then two other shift sizes
        for dist in (1, 3):
            xl, xr = BALANCED[dist]
            for shift in (-UNIT_PX, UNIT_PX):
                add(f"bal-d{dist}-s{shift:+d}", "balance", (xl, xr), (xl + shift, xr + shift), float(abs(shift)), "none",
                    {"dist_ref": dist, "dist_alt": dist, "shift": shift})
            for mag in (45, 135):
                shift = int(mag * rng.choice((-1, 1)))
                add(f"dose-d{dist}-s{shift:+d}", "dose", (xl, xr), (xl + shift, xr + shift), float(mag), "none",
                    {"dist_ref": dist, "dist_alt": dist, "shift": shift})
        # distance: both balanced, reference = the closer arrangement
        for d_ref, d_alt in ((1, 3), (3, 5)):
            add(f"dist-{d_ref}v{d_alt}", "distance", BALANCED[d_ref], BALANCED[d_alt], float(d_alt - d_ref), "none",
                {"dist_ref": d_ref, "dist_alt": d_alt, "shift": 0})
        # identical-pair control
        k = int(rng.choice((1, 3)))
        add(f"ident-d{k}", "balance", BALANCED[k], BALANCED[k], 0.0, "none",
            {"dist_ref": k, "dist_alt": k, "shift": 0}, kind="identical")
    return pairs
