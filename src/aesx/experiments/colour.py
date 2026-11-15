"""E4. Colour swap in a grid composition: Locher, Overbeeke & Stappers (2005),
Perception 34:169-189.

Source: six grid compositions adapted from specific Mondrian paintings, each with
three coloured areas (area 1 the largest). All six assignments of red, blue and
yellow to the three areas were shown (36 stimuli). Participants marked the
balance centre and rated each coloured area's visual weight from 1 to 10. They
were NOT asked which they preferred. Result used here: the largest area was
rated heavier when red than when yellow (by about 0.6 to 1.1 points) where it
covered 9 to 23 % of the field; blue fell between; at about 65 % of the field
untrained viewers showed no colour effect.

Here the line layouts are random partitions (no painting is copied), coloured
with the source's RGB values. A pair is one layout in two colour versions that
differ by exchanging the colour of the largest area with the colour of one small
area: a single colour swap.
"""
from __future__ import annotations

import numpy as np
from PIL import Image

from .. import grid
from ..manifest import Pair, rng_for, save_pair

NAME = "colour"
TITLE = "E4 Colour swap in a grid (after Locher, Overbeeke & Stappers 2005)"
UNITS = {"dev": 12, "test": 36}
# Share of the field covered by the largest coloured area. The source found the colour
# effect at 9-23 % and not (for untrained viewers) at about 65 %.
SIZE_LEVELS = {"small": (0.08, 0.13), "medium": (0.16, 0.24), "large": (0.55, 0.70)}
SMALL_AREA = (0.012, 0.08)  # the source's two small areas covered 1 to 8 % each
# Colours of areas 1, 2, 3 in the source's six versions (its Table 1).
VERSIONS = {"i": "RBY", "ii": "RYB", "iii": "BRY", "iv": "BYR", "v": "YBR", "vi": "YRB"}
# (reference, twin, contrast in area 1). The reference has the colour the weight
# literature ranks heavier (red > blue > yellow) in the largest area.
SWAPS = (("i", "v", "red_vs_yellow"), ("ii", "vi", "red_vs_yellow"),
         ("i", "iii", "red_vs_blue"), ("ii", "iv", "red_vs_blue"),
         ("iii", "vi", "blue_vs_yellow"), ("iv", "v", "blue_vs_yellow"))
# The extra question asked on these pairs (the source's dependent variable).
WEIGHT_QUESTION = "In which of these two images does the largest coloured rectangle look visually heavier?"


def caption(p: Pair) -> str:
    q = p.params
    return f"{p.condition.replace('_', ' ')}: largest area {q['area1_pct']:.0f}% of field ({q['size_level']})"


def make_layout(rng: np.random.Generator, level: str):
    """A partition with one cell in the level's size range and two small cells."""
    lo, hi = SIZE_LEVELS[level]
    for _ in range(50_000):
        tree = grid.random_tree(rng, int(rng.integers(5, 10)), 0.10, 0.90)
        cs = grid.cells(tree)
        big = [k for k, r in cs.items() if lo <= grid.area(r) <= hi]
        small = [k for k, r in cs.items() if SMALL_AREA[0] <= grid.area(r) <= SMALL_AREA[1]]
        if big and len(small) >= 2:
            a1 = big[int(rng.integers(len(big)))]
            s = [small[int(i)] for i in rng.choice(len(small), size=2, replace=False)]
            s.sort(key=lambda k: -grid.area(cs[k]))  # area 2 is the larger of the two small areas
            return tree, (a1, s[0], s[1]), tuple(grid.area(cs[k]) for k in (a1, s[0], s[1]))
    raise RuntimeError(f"no layout found for level {level}")


def generate(split: str, n_units: int) -> list[Pair]:
    out = f"stimuli/{NAME}/{split}"
    pairs: list[Pair] = []
    levels = list(SIZE_LEVELS)
    for u in range(n_units):
        rng = rng_for(NAME, split, u)
        level = levels[u % len(levels)]
        tree, areas, fracs = make_layout(rng, level)
        fam = f"{NAME}-{split}-c{u:03d}"
        images: dict[str, Image.Image] = {v: grid.render(tree, dict(zip(areas, cols))) for v, cols in VERSIONS.items()}
        path = {v: f"{out}/c{u:03d}_{v}.png" for v in VERSIONS}
        base = {"size_level": level, "area1_pct": round(fracs[0] * 100, 2), "area2_pct": round(fracs[1] * 100, 2),
                "area3_pct": round(fracs[2] * 100, 2), "n_cells": len(grid.cells(tree)),
                "proportions": [round(p, 4) for p in grid.proportions(tree)]}
        for ref, alt, contrast in SWAPS:
            # the source's reliable result: red heavier than yellow where the area is 9-23 % of the field
            anchored = contrast == "red_vs_yellow" and level != "large"
            p = Pair(experiment=NAME, pair_id=f"{fam}-{ref}_{alt}", split=split, index=u, kind="manipulation",
                     condition=contrast, ref=path[ref], alt=path[alt], dose=round(fracs[0] * 100, 2),
                     human_direction="ref" if anchored else "none", cluster=fam,
                     params={**base, "version_ref": ref, "version_alt": alt,
                             "colours_ref": VERSIONS[ref], "colours_alt": VERSIONS[alt]})
            pairs.append(save_pair(p, images[ref], images[alt]))
        if u % 2 == 0:
            v = list(VERSIONS)[int(rng.integers(len(VERSIONS)))]
            p = Pair(experiment=NAME, pair_id=f"{fam}-ident-{v}", split=split, index=u, kind="identical",
                     condition="identical", ref=path[v], alt=path[v], dose=0.0, human_direction="none", cluster=fam,
                     params={**base, "version_ref": v, "version_alt": v})
            pairs.append(save_pair(p, images[v], images[v]))
    return pairs
