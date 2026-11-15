"""E3. One object in a frame: Palmer, Gardner & Wickens (2008), Spatial Vision 21:421-449.

Source: a single object on a black floor against a white wall (horizon on the
horizontal midline) in a 4:3 frame; two such pictures of the same object per
trial, "which do you prefer". Experiment 2 (N = 17 analysed) used seven object
positions, 25 to 75 % of the frame width, and two kinds of pair:

  flip      same position, object reflected about its own centre (faces the other
            way). An in-place MIRROR FLIP. People chose the inward-facing view.
  position  same facing, two different positions. A SHIFT of the object.

Experiment 1 (N = 9) also used front views of roughly symmetrical objects at
25 / 50 / 75 %, which isolates the centre bias:

  centre    a symmetrical object at two of the three positions.

The source objects were rendered real objects (man, wolf, jeep, teapot...).
Here they are the schematic icons and abstract shapes of ``aesx.icons``.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
from PIL import Image

from ..icons import BY_NAME, PALETTE, draw_icon
from ..manifest import Pair, rng_for, save_pair
from ..render import BLACK, WHITE, Canvas

NAME = "framing"
TITLE = "E3 One object in a frame (Palmer, Gardner & Wickens 2008)"
W, H = 512, 384  # 4:3, as in the source
POSITIONS = (25.0, 100 / 3, 125 / 3, 50.0, 175 / 3, 200 / 3, 75.0)  # % of frame width (Exp 2)
CENTRE_POSITIONS = (25.0, 50.0, 75.0)  # Exp 1
HORIZON = 0.5  # floor/wall boundary as a fraction of the height
BASE = 0.60  # the object stands on the floor, a little below the horizon

# Icons are split between dev and test so that no test object is seen during development.
DIRECTED = {
    "dev": ("truck", "teapot", "boot", "wedge"),
    "test": ("car", "duck", "chair", "dog", "snail", "locomotive", "person", "desk_lamp",
             "watering_can", "arrow", "notched_disc", "chevron"),
}
SYMMETRIC = {
    "dev": ("tree", "bottle", "star", "table"),
    "test": ("vase", "house", "mushroom", "goblet", "snowman", "rocket", "floor_lamp", "cactus", "flower",
             "disc", "square", "triangle", "pentagon", "hexagon", "diamond", "cross", "dome", "trapezoid"),
}
FLIP_VARIANTS = {"dev": 1, "test": 2}  # colour/size variants of each directed icon in the flip pairs
N_POSITION_ICONS = {"dev": 4, "test": 8}  # icons given the full 21-pair position design (one facing each)
UNITS = {"dev": 1, "test": 1}  # the design is fixed by the icon lists; kept for the common CLI


def caption(p: Pair) -> str:
    q = p.params
    if p.condition == "flip":
        return f"{q['icon']} flip at {q['pos_ref']:.0f}%  (ref faces {'in' if q['pos_ref'] != 50 else 'right'})"
    if p.condition == "position":
        return f"{q['icon']} facing {q['facing']}: {q['pos_ref']:.0f}% vs {q['pos_alt']:.0f}%"
    return f"{q['icon']} (symmetric): {q['pos_ref']:.0f}% vs {q['pos_alt']:.0f}%"


def object_height(aspect: float, scale: float) -> float:
    """Tall objects are limited by frame height, wide ones by frame width."""
    return scale * min(0.42 * H, 0.38 * W / aspect)


def draw(icon_name: str, pos_pct: float, facing: int, colour: tuple, scale: float) -> Image.Image:
    icon = BY_NAME[icon_name]
    c = Canvas(W, H, WHITE)
    c.rect(0, H * HORIZON, W, H, BLACK)
    draw_icon(c, icon, W * pos_pct / 100, H * BASE, object_height(icon.aspect, scale), colour, facing)
    return c.image()


def _look(rng: np.random.Generator) -> tuple[str, float]:
    names = list(PALETTE)
    return names[int(rng.integers(len(names)))], float(rng.uniform(0.85, 1.0))


def generate(split: str, n_units: int = 1) -> list[Pair]:
    out = f"stimuli/{NAME}/{split}"
    pairs: list[Pair] = []
    cache: dict[str, Image.Image] = {}

    def img(path: str, *args) -> Image.Image:
        if path not in cache:
            cache[path] = draw(*args)
        return cache[path]

    def add(pair_id, index, condition, ref_path, alt_path, ref_args, alt_args, dose, direction, cluster, params, kind="manipulation"):
        p = Pair(experiment=NAME, pair_id=pair_id, split=split, index=index, kind=kind, condition=condition,
                 ref=ref_path, alt=alt_path, dose=dose, human_direction=direction, cluster=cluster, params=params)
        pairs.append(save_pair(p, img(ref_path, *ref_args), img(alt_path, *alt_args)))

    unit = 0
    # ---- flip: same position, opposite facing (Exp 2 "opposite-facing" comparisons)
    for name in DIRECTED[split]:
        for v in range(FLIP_VARIANTS[split]):
            rng = rng_for(NAME, split, unit)
            colour_name, scale = _look(rng)
            colour = PALETTE[colour_name]
            tag = f"{NAME}-{split}-{name}-v{v}"
            for k, pos in enumerate(POSITIONS):
                inward = 1 if pos < 50 else -1  # at the centre the reference is the right-facing view
                if pos == 50:
                    inward = 1
                paths = {f: f"{out}/{name}_v{v}_p{k}_{'R' if f == 1 else 'L'}.png" for f in (1, -1)}
                add(f"{tag}-flip-p{k}", unit, "flip", paths[inward], paths[-inward],
                    (name, pos, inward, colour, scale), (name, pos, -inward, colour, scale),
                    round(abs(pos - 50), 2), "ref", f"{NAME}-{name}",
                    {"icon": name, "icon_kind": BY_NAME[name].kind, "aspect": BY_NAME[name].aspect, "variant": v,
                     "colour": colour_name, "scale": round(scale, 4), "pos_ref": pos, "pos_alt": pos,
                     "facing_ref": "R" if inward == 1 else "L", "at_centre": pos == 50})
            unit += 1

    # ---- position: same facing, different positions (Exp 2 "same-facing" comparisons)
    rng = rng_for(NAME, split, 10_000)
    chosen = list(rng.permutation(DIRECTED[split]))[: N_POSITION_ICONS[split]]
    for j, name in enumerate(chosen):
        rng = rng_for(NAME, split, 10_001 + j)
        colour_name, scale = _look(rng)
        colour = PALETTE[colour_name]
        facing = 1 if j % 2 == 0 else -1
        f = "R" if facing == 1 else "L"
        tag = f"{NAME}-{split}-{name}-pos{f}"
        for a, b in combinations(range(len(POSITIONS)), 2):  # reference = the more leftward position
            add(f"{tag}-p{a}p{b}", 10_001 + j, "position",
                f"{out}/{name}_pos{f}_p{a}.png", f"{out}/{name}_pos{f}_p{b}.png",
                (name, POSITIONS[a], facing, colour, scale), (name, POSITIONS[b], facing, colour, scale),
                round(POSITIONS[b] - POSITIONS[a], 2), "profile", f"{NAME}-{name}",
                {"icon": name, "icon_kind": BY_NAME[name].kind, "aspect": BY_NAME[name].aspect, "facing": f,
                 "colour": colour_name, "scale": round(scale, 4), "pos_ref": POSITIONS[a], "pos_alt": POSITIONS[b],
                 "idx_ref": a, "idx_alt": b})

    # ---- centre: a symmetrical object at 25 / 50 / 75 % (Exp 1 front views)
    for j, name in enumerate(SYMMETRIC[split]):
        rng = rng_for(NAME, split, 20_000 + j)
        colour_name, scale = _look(rng)
        colour = PALETTE[colour_name]
        tag = f"{NAME}-{split}-{name}-sym"
        path = {p: f"{out}/{name}_sym_{int(p)}.png" for p in CENTRE_POSITIONS}
        for ref_pos, alt_pos, direction in ((50.0, 25.0, "ref"), (50.0, 75.0, "ref"), (25.0, 75.0, "none")):
            add(f"{tag}-{int(ref_pos)}v{int(alt_pos)}", 20_000 + j, "centre", path[ref_pos], path[alt_pos],
                (name, ref_pos, 1, colour, scale), (name, alt_pos, 1, colour, scale),
                25.0 if ref_pos == 50 else 0.0, direction, f"{NAME}-{name}",
                {"icon": name, "icon_kind": BY_NAME[name].kind, "aspect": BY_NAME[name].aspect,
                 "colour": colour_name, "scale": round(scale, 4), "pos_ref": ref_pos, "pos_alt": alt_pos})

    # ---- identical-pair controls: about one for every ten manipulation pairs
    rng = rng_for(NAME, split, 30_000)
    for k, i in enumerate(rng.choice(len(pairs), size=max(8, len(pairs) // 10), replace=False)):
        src = pairs[int(i)]
        p = Pair(experiment=NAME, pair_id=f"{NAME}-{split}-ident-{k:03d}", split=split, index=30_000 + k,
                 kind="identical", condition=src.condition, ref=src.ref, alt=src.ref, dose=0.0,
                 human_direction="none", cluster=src.cluster, params={"icon": src.params["icon"], "source": src.pair_id})
        pairs.append(save_pair(p, cache[src.ref], cache[src.ref]))
    return pairs
