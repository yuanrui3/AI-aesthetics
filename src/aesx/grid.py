"""Rectilinear grid compositions generated from a seed.

These are compositions *in the manner of* neoplasticist grids: black lines that
run to the frame or to another line, a white field, and three cells filled
with red, blue and yellow. No painting is copied: every layout is a random
recursive partition.

A composition is a binary tree. Each internal node cuts its rectangle with one
line at proportion ``p`` of the way across (vertical line) or down (horizontal
line). This is the coding McManus, Cheema & Stoker (1993) used to alter real
paintings: every line is a proportion between two other lines or edges, so
changing the proportions never changes which line meets which.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from PIL import Image

from .render import RGB, Canvas

# Colours used for all stimuli by Locher, Overbeeke & Stappers (2005, p.173).
RED: RGB = (220, 0, 0)
BLUE: RGB = (0, 0, 152)
YELLOW: RGB = (255, 223, 0)
LINE: RGB = (1, 1, 1)
FIELD: RGB = (231, 231, 231)
COLOURS = {"R": RED, "B": BLUE, "Y": YELLOW}

SIDE = 512
LINE_FRAC = 0.02  # line thickness / side
MIN_SIDE = 0.055  # smallest allowed cell side / side (a cell must stay wider than a line)


@dataclass(frozen=True)
class Node:
    p: float | None = None  # None = leaf
    vertical: bool = True  # True: a vertical line splits left|right; False: a horizontal line splits top|bottom
    a: "Node | None" = None  # left or top
    b: "Node | None" = None  # right or bottom


Rect = tuple[float, float, float, float]  # x0, y0, x1, y1 in units of the side


def _split(rect: Rect, node: Node) -> tuple[Rect, Rect]:
    x0, y0, x1, y1 = rect
    if node.vertical:
        xm = x0 + node.p * (x1 - x0)
        return (x0, y0, xm, y1), (xm, y0, x1, y1)
    ym = y0 + node.p * (y1 - y0)
    return (x0, y0, x1, ym), (x0, ym, x1, y1)


def cells(node: Node, rect: Rect = (0, 0, 1, 1), path: str = "") -> dict[str, Rect]:
    """Leaf rectangles keyed by their path ('0' = left/top child, '1' = right/bottom)."""
    if node.p is None:
        return {path: rect}
    ra, rb = _split(rect, node)
    return {**cells(node.a, ra, path + "0"), **cells(node.b, rb, path + "1")}


def lines(node: Node, rect: Rect = (0, 0, 1, 1)) -> list[tuple[float, float, float, float]]:
    if node.p is None:
        return []
    ra, rb = _split(rect, node)
    seg = (ra[2], rect[1], ra[2], rect[3]) if node.vertical else (rect[0], ra[3], rect[2], ra[3])
    return [seg] + lines(node.a, ra) + lines(node.b, rb)


def proportions(node: Node) -> list[float]:
    return [] if node.p is None else [node.p] + proportions(node.a) + proportions(node.b)


def area(rect: Rect) -> float:
    return (rect[2] - rect[0]) * (rect[3] - rect[1])


def min_side(node: Node) -> float:
    return min(min(r[2] - r[0], r[3] - r[1]) for r in cells(node).values())


def random_tree(rng: np.random.Generator, n_cells: int, p_lo: float = 0.15, p_hi: float = 0.85) -> Node:
    """Recursive partition into ``n_cells`` cells, cutting larger cells and longer sides more often."""
    for _ in range(200):
        tree: dict[str, tuple] = {"": ("leaf",)}
        rects: dict[str, Rect] = {"": (0.0, 0.0, 1.0, 1.0)}
        ok = True
        while len(rects) < n_cells and ok:
            keys = list(rects)
            wts = np.array([area(rects[k]) ** 1.5 for k in keys])
            for _ in range(40):
                k = keys[int(rng.choice(len(keys), p=wts / wts.sum()))]
                x0, y0, x1, y1 = rects[k]
                w, h = x1 - x0, y1 - y0
                vertical = bool(rng.random() < w / (w + h))
                p = float(np.clip(1 / (1 + math.exp(-rng.normal(0, 0.9))), p_lo, p_hi))
                span = w if vertical else h
                if min(p, 1 - p) * span >= MIN_SIDE * 1.6:  # leave room for later alteration
                    break
            else:
                ok = False
                break
            tree[k] = ("split", p, vertical)
            ra, rb = _split(rects.pop(k), Node(p, vertical))
            rects[k + "0"], rects[k + "1"] = ra, rb
            tree[k + "0"] = tree[k + "1"] = ("leaf",)
        if ok:
            def build(path: str) -> Node:
                t = tree[path]
                return Node() if t[0] == "leaf" else Node(t[1], t[2], build(path + "0"), build(path + "1"))
            return build("")
    raise RuntimeError("could not build a partition")


def alter(node: Node, delta: float, rng: np.random.Generator) -> Node:
    """McManus et al.'s alteration: logit-transform each proportion, add or subtract
    ``delta`` at random (independently per line), transform back."""
    if node.p is None:
        return node
    z = math.log(node.p / (1 - node.p)) + (delta if rng.random() < 0.5 else -delta)
    return Node(1 / (1 + math.exp(-z)), node.vertical, alter(node.a, delta, rng), alter(node.b, delta, rng))


def render(node: Node, fills: dict[str, str], side: int = SIDE) -> Image.Image:
    """``fills`` maps a cell path to 'R', 'B' or 'Y'; every other cell is the off-white field."""
    c = Canvas(side, side, FIELD)
    for path, (x0, y0, x1, y1) in cells(node).items():
        if path in fills:
            c.rect(x0 * side, y0 * side, x1 * side, y1 * side, COLOURS[fills[path]])
    t = LINE_FRAC * side / 2
    for x0, y0, x1, y1 in lines(node):
        c.rect(x0 * side - t, y0 * side - t, x1 * side + t, y1 * side + t, LINE)
    return c.image()
