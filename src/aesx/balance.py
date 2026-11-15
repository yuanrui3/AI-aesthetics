"""Objective balance measures.

``apb_score`` is the Assessment of Preference for Balance score of Wilson &
Chatterjee (2005, Empirical Studies of the Arts 23:165-180): the mean of eight
"measures of symmetry", each  |area1 - area2| / (area1 + area2) x 100, where
the two areas are element pixels on either side of a division of the square:

  1-4  halves about the vertical axis, the horizontal axis and the two diagonals
  5-8  equal-area inner vs outer regions about the same four axes:
       - vertical / horizontal: the two inner of four equal columns / rows
       - diagonals: the band |d| < (1 - 1/sqrt 2) * side around the diagonal,
         which has the same area as the two corner triangles outside it
         (the paper says "equal inner and outer areas"; its Figure 2 draws the
         band edge meeting the frame at ~0.293 of the side, i.e. 1 - 1/sqrt 2).

0 = perfectly balanced, 100 = everything on one side of every division.
LOWER IS MORE BALANCED.

``dcm`` is the deviation of the centre of mass used by Huebner & Fillinger
(2016, Front. Psychol. 7:335) as the rival measure.
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from PIL import Image

BAND = 1 - 1 / math.sqrt(2)

MEASURES = (
    "half_lr",  # left vs right  (symmetry about the vertical axis)
    "half_tb",  # top vs bottom  (symmetry about the horizontal axis)
    "half_d1",  # either side of the top-left -> bottom-right diagonal
    "half_d2",  # either side of the bottom-left -> top-right diagonal
    "io_cols",  # inner vs outer columns
    "io_rows",  # inner vs outer rows
    "io_d1",  # inner band vs outer corners about the TL-BR diagonal
    "io_d2",  # inner band vs outer corners about the BL-TR diagonal
)


def ink(im: Image.Image | np.ndarray) -> np.ndarray:
    """Element coverage in [0, 1] per pixel: black elements on a white ground."""
    a = np.asarray(im.convert("L") if isinstance(im, Image.Image) else im, dtype=np.float64)
    return 1.0 - a / 255.0


def _asym(w: np.ndarray, region: np.ndarray) -> float:
    """|a1 - a2| / (a1 + a2) * 100 where ``region`` holds each pixel's share in area 1."""
    total = w.sum()
    if total == 0:
        return 0.0
    a1 = (w * region).sum()
    return float(abs(a1 - (total - a1)) / total * 100.0)


@lru_cache(maxsize=8)
def _regions(n: int) -> dict[str, np.ndarray]:
    """For each measure, every pixel's share in 'area 1' (1, 0, or 0.5 on the dividing line)."""
    c = (np.arange(n) + 0.5) / n  # pixel centres in units of the side, origin top-left
    x, y = np.meshgrid(c, c)

    def side(v: np.ndarray) -> np.ndarray:
        return np.where(v < 0, 1.0, np.where(v > 0, 0.0, 0.5))

    d1 = x - y  # zero on the TL-BR diagonal
    d2 = x + y - 1.0  # zero on the BL-TR diagonal
    return {
        "half_lr": side(x - 0.5),
        "half_tb": side(y - 0.5),
        "half_d1": side(d1),
        "half_d2": side(d2),
        "io_cols": side(np.abs(x - 0.5) - 0.25),
        "io_rows": side(np.abs(y - 0.5) - 0.25),
        "io_d1": side(np.abs(d1) - BAND),
        "io_d2": side(np.abs(d2) - BAND),
    }


def apb_measures(w: np.ndarray) -> dict[str, float]:
    """The eight symmetry measures for a square coverage map ``w`` (see ``ink``)."""
    n = w.shape[0]
    assert w.shape == (n, n), "APB is defined on a square"
    return {name: _asym(w, region) for name, region in _regions(n).items()}


def apb_score(im: Image.Image | np.ndarray) -> float:
    """APB balance score, 0 (balanced) to 100 (unbalanced)."""
    w = ink(im) if isinstance(im, Image.Image) else im
    return float(np.mean(list(apb_measures(w).values())))


def centre_of_mass(w: np.ndarray) -> tuple[float, float]:
    """Centre of mass in units of width/height, origin top-left."""
    h, wd = w.shape
    total = w.sum()
    xs = (np.arange(wd) + 0.5) / wd
    ys = (np.arange(h) + 0.5) / h
    return float((w.sum(axis=0) * xs).sum() / total), float((w.sum(axis=1) * ys).sum() / total)


def dcm(im: Image.Image | np.ndarray) -> float:
    """Deviation of the centre of mass, as defined by Huebner & Fillinger (2016, p.4):

        DCM = sqrt(dx^2 + dy^2) / 0.5 * 100,   dx = 0.5 - bx/w,  dy = 0.5 - by/h

    0 = centre of mass at the frame centre. Lower is more balanced.
    """
    w = ink(im) if isinstance(im, Image.Image) else im
    cx, cy = centre_of_mass(w)
    return float(math.hypot(cx - 0.5, cy - 0.5) / 0.5 * 100.0)
