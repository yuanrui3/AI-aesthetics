"""Code-drawn stand-ins for the object pictures used in the source experiments.

Palmer et al. (2008) and Leyssen et al. (2012) showed rendered or photographed
real objects. Those cannot be regenerated from a description, so the objects
here are flat schematic icons built from a few primitives, plus plain abstract
shapes. Nothing is traced or copied from any image.

An icon lives in a unit box: x runs 0 -> 1 left to right, y runs 0 -> 1 top to
bottom, and ``aspect`` is the box's width / height. DIRECTED icons are drawn
FACING RIGHT (front toward x = 1). Primitives:

    ("poly",   [(x, y), ...], shade)
    ("rect",   (x0, y0, x1, y1), shade)
    ("ellipse",(x0, y0, x1, y1), shade)
    ("circle", (cx, cy, r), shade)      r is a fraction of the box HEIGHT

Shades: 0 = main colour, 1 = dark accent, 2 = light accent.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .render import RGB, Canvas


@dataclass(frozen=True)
class Icon:
    name: str
    aspect: float
    kind: str  # "object" (schematic, meaningful) | "abstract"
    parts: tuple

    def x_extent(self) -> tuple[float, float]:
        """Leftmost and rightmost drawn x, in box units."""
        lo, hi = 1.0, 0.0
        for prim, geom, _ in self.parts:
            if prim == "poly":
                xs = [p[0] for p in geom]
            elif prim in ("rect", "ellipse"):
                xs = [geom[0], geom[2]]
            else:  # circle
                xs = [geom[0] - geom[2] / self.aspect, geom[0] + geom[2] / self.aspect]
            lo, hi = min(lo, *xs), max(hi, *xs)
        return lo, hi


def _arc(cx: float, cy: float, rx: float, ry: float, a0: float, a1: float, n: int = 40) -> list:
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def _star(n: int = 5, inner: float = 0.42) -> list:
    pts = []
    for k in range(2 * n):
        r = 0.5 if k % 2 == 0 else 0.5 * inner
        a = math.radians(-90 + 180 * k / n)
        pts.append((0.5 + r * math.cos(a), 0.5 + r * math.sin(a)))
    return pts


def _ngon(n: int, rot: float = -90.0) -> list:
    return [(0.5 + 0.5 * math.cos(math.radians(rot + 360 * k / n)), 0.5 + 0.5 * math.sin(math.radians(rot + 360 * k / n)))
            for k in range(n)]


# ------------------------------------------------------------------ directed
DIRECTED = [
    Icon("car", 2.2, "object", (
        ("rect", (0.00, 0.42, 1.00, 0.80), 0),
        ("poly", [(0.08, 0.42), (0.18, 0.08), (0.50, 0.08), (0.68, 0.42)], 0),
        ("poly", [(0.40, 0.38), (0.40, 0.15), (0.48, 0.15), (0.61, 0.38)], 2),
        ("poly", [(0.16, 0.38), (0.22, 0.15), (0.36, 0.15), (0.36, 0.38)], 2),
        ("circle", (0.20, 0.80, 0.20), 1),
        ("circle", (0.78, 0.80, 0.20), 1),
        ("rect", (0.94, 0.48, 1.00, 0.60), 2),
    )),
    Icon("truck", 2.2, "object", (
        ("rect", (0.00, 0.04, 0.62, 0.76), 0),
        ("poly", [(0.66, 0.76), (0.66, 0.26), (0.86, 0.26), (1.00, 0.52), (1.00, 0.76)], 0),
        ("poly", [(0.71, 0.50), (0.71, 0.32), (0.84, 0.32), (0.94, 0.50)], 2),
        ("rect", (0.00, 0.72, 1.00, 0.82), 1),
        ("circle", (0.16, 0.82, 0.18), 1),
        ("circle", (0.42, 0.82, 0.18), 1),
        ("circle", (0.84, 0.82, 0.18), 1),
    )),
    Icon("duck", 1.3, "object", (
        ("poly", [(0.06, 0.70), (0.00, 0.36), (0.26, 0.56)], 0),
        ("ellipse", (0.02, 0.42, 0.80, 1.00), 0),
        ("ellipse", (0.20, 0.56, 0.60, 0.86), 1),
        ("circle", (0.72, 0.28, 0.24), 0),
        ("poly", [(0.86, 0.24), (1.00, 0.33), (0.86, 0.40)], 1),
        ("circle", (0.76, 0.22, 0.04), 1),
    )),
    Icon("teapot", 1.5, "object", (
        ("poly", [(0.26, 0.40), (0.04, 0.42), (0.00, 0.60), (0.06, 0.80), (0.26, 0.84), (0.26, 0.74),
                  (0.13, 0.70), (0.10, 0.60), (0.13, 0.52), (0.26, 0.50)], 0),
        ("poly", [(0.70, 0.60), (0.88, 0.40), (0.94, 0.22), (1.00, 0.24), (0.96, 0.48), (0.80, 0.80)], 0),
        ("ellipse", (0.20, 0.26, 0.80, 1.00), 0),
        ("ellipse", (0.34, 0.16, 0.66, 0.36), 1),
        ("circle", (0.50, 0.11, 0.07), 1),
    )),
    Icon("chair", 0.62, "object", (
        ("rect", (0.00, 0.00, 0.17, 1.00), 0),
        ("rect", (0.00, 0.52, 1.00, 0.63), 0),
        ("rect", (0.83, 0.63, 1.00, 1.00), 0),
        ("rect", (0.00, 0.08, 0.17, 0.14), 1),
    )),
    Icon("boot", 1.25, "object", (
        ("rect", (0.00, 0.00, 0.46, 0.70), 0),
        ("poly", [(0.00, 0.58), (0.46, 0.58), (0.80, 0.66), (1.00, 0.80), (1.00, 0.90), (0.00, 0.90)], 0),
        ("rect", (0.00, 0.90, 1.00, 1.00), 1),
        ("rect", (0.00, 0.00, 0.46, 0.09), 1),
    )),
    Icon("dog", 1.6, "object", (
        ("poly", [(0.12, 0.44), (0.00, 0.12), (0.06, 0.10), (0.18, 0.40)], 0),
        ("ellipse", (0.08, 0.30, 0.76, 0.72), 0),
        ("rect", (0.15, 0.60, 0.23, 1.00), 0),
        ("rect", (0.27, 0.60, 0.35, 1.00), 0),
        ("rect", (0.52, 0.60, 0.60, 1.00), 0),
        ("rect", (0.64, 0.60, 0.72, 1.00), 0),
        ("circle", (0.80, 0.30, 0.20), 0),
        ("rect", (0.82, 0.30, 1.00, 0.46), 0),
        ("poly", [(0.70, 0.16), (0.74, 0.00), (0.84, 0.14)], 1),
        ("circle", (0.975, 0.33, 0.035), 1),
        ("circle", (0.84, 0.24, 0.03), 1),
    )),
    Icon("snail", 1.6, "object", (
        ("poly", [(0.00, 1.00), (0.06, 0.84), (0.70, 0.80), (0.80, 0.46), (0.92, 0.42), (1.00, 0.54), (0.96, 0.82), (0.90, 1.00)], 2),
        ("rect", (0.84, 0.16, 0.87, 0.46), 2),
        ("rect", (0.93, 0.16, 0.96, 0.46), 2),
        ("circle", (0.36, 0.48, 0.46), 0),
        ("circle", (0.36, 0.48, 0.28), 1),
        ("circle", (0.36, 0.48, 0.11), 0),
    )),
    Icon("locomotive", 1.7, "object", (
        ("rect", (0.30, 0.34, 0.95, 0.72), 0),
        ("rect", (0.00, 0.08, 0.34, 0.72), 0),
        ("rect", (0.08, 0.18, 0.26, 0.40), 2),
        ("rect", (0.76, 0.05, 0.88, 0.34), 1),
        ("poly", [(0.95, 0.56), (1.00, 0.82), (0.95, 0.82)], 1),
        ("circle", (0.16, 0.82, 0.18), 1),
        ("circle", (0.50, 0.84, 0.16), 1),
        ("circle", (0.78, 0.84, 0.16), 1),
    )),
    Icon("person", 0.42, "object", (
        ("poly", [(0.28, 0.22), (0.72, 0.22), (0.68, 0.60), (0.32, 0.60)], 0),
        ("poly", [(0.56, 0.27), (1.00, 0.42), (0.95, 0.48), (0.54, 0.36)], 0),
        ("rect", (0.34, 0.60, 0.64, 0.95), 1),
        ("poly", [(0.34, 0.93), (0.98, 0.93), (0.98, 1.00), (0.34, 1.00)], 1),
        ("circle", (0.50, 0.10, 0.10), 0),
        ("poly", [(0.70, 0.07), (0.90, 0.12), (0.70, 0.15)], 0),
    )),
    Icon("desk_lamp", 0.8, "object", (
        ("rect", (0.05, 0.92, 0.60, 1.00), 1),
        ("poly", [(0.28, 0.92), (0.37, 0.92), (0.40, 0.34), (0.31, 0.34)], 1),
        ("poly", [(0.28, 0.38), (0.18, 0.12), (0.48, 0.00), (1.00, 0.36), (0.84, 0.54)], 0),
        ("circle", (0.88, 0.47, 0.06), 2),
    )),
    Icon("watering_can", 1.5, "object", (
        ("poly", [(0.22, 0.40), (0.04, 0.44), (0.00, 0.66), (0.06, 0.86), (0.22, 0.90), (0.22, 0.80),
                  (0.12, 0.76), (0.10, 0.66), (0.12, 0.54), (0.22, 0.50)], 0),
        ("poly", [(0.64, 0.78), (0.90, 0.28), (0.98, 0.32), (0.68, 0.96)], 0),
        ("poly", [(0.86, 0.20), (1.00, 0.28), (0.97, 0.42), (0.85, 0.34)], 1),
        ("rect", (0.20, 0.34, 0.68, 1.00), 0),
        ("rect", (0.20, 0.34, 0.68, 0.42), 1),
    )),
    # ---- abstract directed shapes
    Icon("arrow", 1.8, "abstract", (
        ("poly", [(0.00, 0.33), (0.58, 0.33), (0.58, 0.05), (1.00, 0.50), (0.58, 0.95), (0.58, 0.67), (0.00, 0.67)], 0),
    )),
    Icon("wedge", 1.4, "abstract", (("poly", [(0.00, 0.00), (1.00, 0.50), (0.00, 1.00)], 0),)),
    Icon("notched_disc", 1.0, "abstract", (("poly", [(0.5, 0.5)] + _arc(0.5, 0.5, 0.5, 0.5, 35, 325), 0),)),
    Icon("chevron", 1.0, "abstract", (
        ("poly", [(0.00, 0.00), (0.45, 0.00), (1.00, 0.50), (0.45, 1.00), (0.00, 1.00), (0.55, 0.50)], 0),
    )),
]

# ----------------------------------------------------------------- symmetric
SYMMETRIC = [
    Icon("vase", 0.6, "object", (
        ("poly", [(0.30, 0.00), (0.70, 0.00), (0.62, 0.20), (0.95, 0.50), (1.00, 0.70), (0.80, 1.00),
                  (0.20, 1.00), (0.00, 0.70), (0.05, 0.50), (0.38, 0.20)], 0),
        ("rect", (0.28, 0.00, 0.72, 0.05), 1),
    )),
    Icon("tree", 0.72, "object", (("rect", (0.42, 0.62, 0.58, 1.00), 1), ("circle", (0.50, 0.36, 0.36), 0))),
    Icon("house", 1.0, "object", (
        ("rect", (0.08, 0.45, 0.92, 1.00), 0),
        ("poly", [(0.00, 0.47), (0.50, 0.00), (1.00, 0.47)], 1),
        ("rect", (0.42, 0.66, 0.58, 1.00), 1),
    )),
    Icon("mushroom", 1.0, "object", (
        ("rect", (0.38, 0.50, 0.62, 1.00), 2),
        ("poly", _arc(0.5, 0.56, 0.5, 0.56, 180, 360), 0),
    )),
    Icon("bottle", 0.34, "object", (
        ("rect", (0.00, 0.40, 1.00, 1.00), 0),
        ("poly", [(0.00, 0.40), (0.32, 0.20), (0.68, 0.20), (1.00, 0.40)], 0),
        ("rect", (0.32, 0.04, 0.68, 0.22), 0),
        ("rect", (0.26, 0.00, 0.74, 0.06), 1),
        ("rect", (0.00, 0.55, 1.00, 0.80), 2),
    )),
    Icon("goblet", 0.6, "object", (
        ("poly", [(0.00, 0.00), (1.00, 0.00), (0.85, 0.35), (0.56, 0.48), (0.56, 0.90), (0.90, 1.00),
                  (0.10, 1.00), (0.44, 0.90), (0.44, 0.48), (0.15, 0.35)], 0),
    )),
    Icon("snowman", 0.56, "object", (
        ("circle", (0.50, 0.72, 0.28), 0),
        ("circle", (0.50, 0.38, 0.20), 0),
        ("circle", (0.50, 0.13, 0.13), 0),
        ("rect", (0.30, 0.00, 0.70, 0.04), 1),
    )),
    Icon("rocket", 0.5, "object", (
        ("poly", [(0.20, 0.60), (0.00, 1.00), (0.20, 0.86)], 1),
        ("poly", [(0.80, 0.60), (1.00, 1.00), (0.80, 0.86)], 1),
        ("poly", [(0.50, 0.00), (0.80, 0.30), (0.80, 0.86), (0.20, 0.86), (0.20, 0.30)], 0),
        ("circle", (0.50, 0.38, 0.07), 2),
    )),
    Icon("table", 1.6, "object", (
        ("rect", (0.00, 0.00, 1.00, 0.18), 0),
        ("rect", (0.06, 0.18, 0.16, 1.00), 0),
        ("rect", (0.84, 0.18, 0.94, 1.00), 0),
    )),
    Icon("floor_lamp", 0.5, "object", (
        ("rect", (0.25, 0.95, 0.75, 1.00), 1),
        ("rect", (0.46, 0.30, 0.54, 0.95), 1),
        ("poly", [(0.20, 0.00), (0.80, 0.00), (1.00, 0.32), (0.00, 0.32)], 0),
    )),
    Icon("cactus", 0.8, "object", (
        ("rect", (0.38, 0.00, 0.62, 1.00), 0),
        ("rect", (0.08, 0.45, 0.38, 0.57), 0),
        ("rect", (0.08, 0.25, 0.20, 0.57), 0),
        ("rect", (0.62, 0.45, 0.92, 0.57), 0),
        ("rect", (0.80, 0.25, 0.92, 0.57), 0),
    )),
    Icon("flower", 0.62, "object", (
        ("rect", (0.47, 0.40, 0.53, 1.00), 1),
        ("ellipse", (0.14, 0.62, 0.48, 0.76), 1),
        ("ellipse", (0.52, 0.62, 0.86, 0.76), 1),
        *[("circle", (0.5 + 0.21 * math.cos(math.radians(a)), 0.20 + 0.13 * math.sin(math.radians(a)), 0.085), 0)
          for a in (30, 90, 150, 210, 270, 330)],
        ("circle", (0.50, 0.20, 0.075), 2),
    )),
    # ---- abstract symmetric shapes
    Icon("disc", 1.0, "abstract", (("circle", (0.5, 0.5, 0.5), 0),)),
    Icon("square", 1.0, "abstract", (("rect", (0.0, 0.0, 1.0, 1.0), 0),)),
    Icon("triangle", 1.15, "abstract", (("poly", [(0.5, 0.0), (1.0, 1.0), (0.0, 1.0)], 0),)),
    Icon("pentagon", 1.05, "abstract", (("poly", _ngon(5), 0),)),
    Icon("hexagon", 1.15, "abstract", (("poly", _ngon(6, 0.0), 0),)),
    Icon("diamond", 0.8, "abstract", (("poly", [(0.5, 0.0), (1.0, 0.5), (0.5, 1.0), (0.0, 0.5)], 0),)),
    Icon("star", 1.05, "abstract", (("poly", _star(), 0),)),
    Icon("cross", 1.0, "abstract", (("rect", (0.34, 0.0, 0.66, 1.0), 0), ("rect", (0.0, 0.34, 1.0, 0.66), 0))),
    Icon("dome", 1.7, "abstract", (("poly", _arc(0.5, 1.0, 0.5, 1.0, 180, 360), 0),)),
    Icon("trapezoid", 1.4, "abstract", (("poly", [(0.22, 0.0), (0.78, 0.0), (1.0, 1.0), (0.0, 1.0)], 0),)),
]

BY_NAME = {i.name: i for i in DIRECTED + SYMMETRIC}

# Mid-lightness hues that read against white, black and the coloured grounds used here.
PALETTE: dict[str, RGB] = {
    "red": (200, 70, 60), "blue": (60, 120, 200), "green": (70, 160, 90), "orange": (230, 150, 40),
    "purple": (140, 90, 180), "teal": (40, 160, 170), "pink": (200, 110, 150), "grey": (150, 150, 150),
}


def shades(base: RGB) -> tuple[RGB, RGB, RGB]:
    dark = tuple(int(c * 0.62) for c in base)  # still visible on the black floor
    light = tuple(int(c + (255 - c) * 0.65) for c in base)
    return base, dark, light  # type: ignore[return-value]


def draw_icon(canvas: Canvas, icon: Icon, cx: float, base_y: float, height: float, base: RGB, facing: int = 1) -> tuple[float, float]:
    """Draw ``icon`` standing on ``base_y`` with its horizontal extent centred on ``cx``.

    The object's centre is the midpoint between its leftmost and rightmost points,
    the definition used by Palmer et al. (2008). ``facing`` = +1 right, -1 left;
    a left-facing icon is the right-facing one reflected about that centre.
    Returns the (left, right) pixel extent actually drawn.
    """
    w = icon.aspect * height
    lo, hi = icon.x_extent()
    left = cx - (lo + hi) / 2 * w  # box origin such that the drawn extent is centred on cx
    top = base_y - height
    col = shades(base)

    def X(x: float) -> float:
        px = left + x * w
        return px if facing == 1 else 2 * cx - px

    def Y(y: float) -> float:
        return top + y * height

    for prim, g, shade in icon.parts:
        c = col[shade]
        if prim == "poly":
            canvas.polygon([(X(x), Y(y)) for x, y in g], c)
        elif prim == "rect":
            xa, xb = sorted((X(g[0]), X(g[2])))
            canvas.rect(xa, Y(g[1]), xb, Y(g[3]), c)
        elif prim == "ellipse":
            xa, xb = sorted((X(g[0]), X(g[2])))
            canvas.ellipse(xa, Y(g[1]), xb, Y(g[3]), c)
        else:
            r = g[2] * height
            canvas.circle(X(g[0]), Y(g[1]), r, c)
    return cx - (hi - lo) / 2 * w, cx + (hi - lo) / 2 * w
