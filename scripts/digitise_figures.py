"""Measure published figures whose values are not printed in the text.

The page images are NOT in the repo (they are copyrighted pages of the papers);
pass their paths. The numbers this prints are copied into
scripts/human_effects.py with provenance "digitised".

    uv run python -I scripts/digitise_figures.py palmer <page-with-fig5.png> <page-with-fig6.png>
    uv run python -I scripts/digitise_figures.py leyssen <fig14.jpg>

Method (line plots): find the plot's axis lines (the longest dark vertical and
horizontal runs), take the x-axis row as 0 and the top end of the y-axis as 100,
remove the thin connecting lines by a morphological opening so only the square
markers remain, and read each marker's centroid.
Method (bar chart): calibrate on the x-axis (0) and the dashed chance line (0.5),
then read the top edge of each coloured bar.
"""
from __future__ import annotations

import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi


def longest_run(mask: np.ndarray, axis: int) -> tuple[int, int, int]:
    """(index of the line, start, end) of the longest unbroken dark run along ``axis``."""
    best = (0, 0, 0)
    lines = mask if axis == 1 else mask.T
    for i, row in enumerate(lines):
        padded = np.concatenate(([0], row.astype(np.int8), [0]))
        d = np.diff(padded)
        starts, ends = np.where(d == 1)[0], np.where(d == -1)[0]
        if len(starts):
            k = int(np.argmax(ends - starts))
            if ends[k] - starts[k] > best[2] - best[1]:
                best = (i, int(starts[k]), int(ends[k]))
    return best


def line_plot(path: str, n_x: int = 7) -> list[list[float]]:
    """Values (0-100) of the markers at each of ``n_x`` x positions, highest first."""
    dark = np.asarray(Image.open(path).convert("L")) < 110
    # Restrict to the figure: the top 45% of the page holds the plot in both pages used.
    dark[int(dark.shape[0] * 0.45):] = False
    col, y_top, y_bot = longest_run(dark, axis=0)  # y-axis: a column
    row, x_left, x_right = longest_run(dark, axis=1)  # x-axis: a row
    y0, y100 = row, y_top
    plot = dark[y100 - 5 : y0 - 6, col + 8 : x_right].copy()
    # Markers are filled squares several times thicker than the lines and the lettering.
    k = max(5, int(round((y0 - y100) * 0.013)))
    opened = ndi.binary_opening(plot, structure=np.ones((k, k), bool))
    lab, n = ndi.label(opened)
    blobs = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        h, w = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
        if 0.5 < h / w < 2.0:  # roughly square
            blobs.append((xs.mean() + col + 8, ys.mean() + y100 - 5, len(ys)))
    xs = np.array([b[0] for b in blobs])
    # Seven equally spaced positions between the leftmost and rightmost marker.
    grid = np.linspace(xs.min(), xs.max(), n_x)
    out: list[list[float]] = [[] for _ in range(n_x)]
    for x, y, _ in blobs:
        j = int(np.argmin(np.abs(grid - x)))
        if abs(grid[j] - x) < (grid[1] - grid[0]) * 0.25:
            out[j].append(round(float(100 * (y0 - y) / (y0 - y100)), 1))
    print(f"  axis: y=0 at row {y0}, y=100 at row {y100}, {n} blobs kept {len(blobs)}, kernel {k}px")
    return [sorted(v, reverse=True) for v in out]


def palmer(fig5: str, fig6: str) -> None:
    print("Palmer, Gardner & Wickens (2008) Figure 5: opposite-facing, % chosen at 25..75%")
    for pos, v in zip((25, 33, 42, 50, 58, 67, 75), line_plot(fig5)):
        print(f"  {pos}%: {v}   sum {sum(v):.1f}")
    print("Figure 6: same-facing, % of comparisons won at 25..75%")
    for pos, v in zip((25, 33, 42, 50, 58, 67, 75), line_plot(fig6)):
        print(f"  {pos}%: {v}")


def leyssen(fig14: str) -> None:
    im = np.asarray(Image.open(fig14).convert("RGB")).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    teal = (g > r + 40) & (b > r + 30)  # related
    red = (r > g + 80) & (r > b + 80)  # unrelated
    dark = (r < 90) & (g < 90) & (b < 90)
    h, w = dark.shape
    for name, x_lo, x_hi in (("(a) P(smaller distance chosen)", 0, w // 2), ("(b) P(balanced chosen)", w // 2, w)):
        sub_dark = dark[:, x_lo:x_hi]
        row0 = int(np.argmax(sub_dark.sum(axis=1)))  # the x-axis is the row with most dark pixels
        # the dashed chance line: the row above the axis with the next most dark pixels, away from text
        counts = sub_dark[: row0 - 10].sum(axis=1)
        row_half = int(np.argmax(counts))
        print(f"{name}: 0 at row {row0}, 0.5 at row {row_half}")
        for label, mask in (("related", teal), ("unrelated", red)):
            m = mask[:row0, x_lo:x_hi]
            lab, n = ndi.label(m)
            bars = []
            for i in range(1, n + 1):
                ys, xs = np.where(lab == i)
                if len(ys) > 200:  # a bar, not legend lettering
                    bars.append((xs.mean(), 0.5 * (row0 - ys.min()) / (row0 - row_half)))
            bars.sort()
            # the legend swatch sits at the far right of panel (b); bars are the four leftmost tall blobs
            print(f"  {label}: " + ", ".join(f"{v:.3f}" for _, v in bars[:4]))


if __name__ == "__main__":
    {"palmer": palmer, "leyssen": leyssen}[sys.argv[1]](*sys.argv[2:])
