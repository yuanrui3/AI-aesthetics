"""Anti-aliased drawing primitives for code-generated stimuli.

All coordinates are in output pixels (floats allowed). Shapes are drawn on a
canvas supersampled by ``ss`` and reduced with a box filter, so edges are
smooth and the result is byte-for-byte reproducible for a given Pillow version.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

from PIL import Image, ImageDraw, ImageFont

RGB = tuple[int, int, int]

WHITE: RGB = (255, 255, 255)
BLACK: RGB = (0, 0, 0)
GREY: RGB = (128, 128, 128)


class Canvas:
    def __init__(self, width: int, height: int, bg: RGB = WHITE, ss: int = 4):
        self.width, self.height, self.ss = int(width), int(height), int(ss)
        self._im = Image.new("RGB", (self.width * ss, self.height * ss), bg)
        self._d = ImageDraw.Draw(self._im)

    # -- primitives ---------------------------------------------------------
    def rect(self, x0: float, y0: float, x1: float, y1: float, fill: RGB) -> None:
        s = self.ss
        # Pillow rectangles include the end pixel, hence the -1.
        self._d.rectangle(
            [round(x0 * s), round(y0 * s), round(x1 * s) - 1, round(y1 * s) - 1], fill=fill
        )

    def circle(self, cx: float, cy: float, r: float, fill: RGB) -> None:
        s = self.ss
        self._d.ellipse(
            [round((cx - r) * s), round((cy - r) * s), round((cx + r) * s) - 1, round((cy + r) * s) - 1],
            fill=fill,
        )

    def ellipse(self, x0: float, y0: float, x1: float, y1: float, fill: RGB) -> None:
        s = self.ss
        self._d.ellipse([round(x0 * s), round(y0 * s), round(x1 * s) - 1, round(y1 * s) - 1], fill=fill)

    def polygon(self, pts: Iterable[Sequence[float]], fill: RGB) -> None:
        s = self.ss
        self._d.polygon([(x * s, y * s) for x, y in pts], fill=fill)

    def regular_polygon(
        self, cx: float, cy: float, r: float, n: int, fill: RGB, rotation_deg: float = 0.0
    ) -> None:
        """Regular n-gon with circumradius r. rotation 0 puts a vertex at 3 o'clock."""
        a0 = math.radians(rotation_deg)
        self.polygon(
            [(cx + r * math.cos(a0 + 2 * math.pi * k / n), cy + r * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)],
            fill,
        )

    def frame(self, thickness: float, colour: RGB = BLACK) -> None:
        """Border drawn inside the canvas edge."""
        w, h, t = self.width, self.height, thickness
        self.rect(0, 0, w, t, colour)
        self.rect(0, h - t, w, h, colour)
        self.rect(0, 0, t, h, colour)
        self.rect(w - t, 0, w, h, colour)

    # -- output -------------------------------------------------------------
    def image(self) -> Image.Image:
        if self.ss == 1:
            return self._im.copy()
        return self._im.resize((self.width, self.height), Image.Resampling.BOX)


def mirror(im: Image.Image) -> Image.Image:
    """Left-right mirror image."""
    return im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)  # bundled with Pillow, same on every machine
    except TypeError:  # very old Pillow
        return ImageFont.load_default()


def side_by_side(
    left: Image.Image,
    right: Image.Image,
    tags: tuple[str, str] | None = None,
    gap: int = 48,
    margin: int = 32,
    bg: RGB = GREY,
) -> Image.Image:
    """One image holding both panels on a neutral ground.

    ``tags`` are optional captions drawn under the left and right panels (used
    when answer labels are letters; omitted when the answer is left/right).
    """
    assert left.size == right.size, "panels must be the same size"
    w, h = left.size
    tag_h = 56 if tags else 0
    out = Image.new("RGB", (2 * w + gap + 2 * margin, h + 2 * margin + tag_h), bg)
    out.paste(left, (margin, margin))
    out.paste(right, (margin + w + gap, margin))
    if tags:
        d = ImageDraw.Draw(out)
        f = _font(40)
        for tag, x0 in zip(tags, (margin, margin + w + gap)):
            d.text((x0 + w / 2, margin + h + tag_h / 2 + 4), tag, fill=WHITE, font=f, anchor="mm")
    return out


def contact_sheet(
    rows: list[tuple[str, Image.Image, Image.Image]],
    cols: int = 3,
    thumb: int = 220,
    title: str = "",
) -> Image.Image:
    """Grid of (caption, reference, manipulated) pairs for human inspection."""
    pad, cap_h, title_h = 14, 34, 54 if title else 0
    cell_w = 2 * thumb + 3 * pad
    scale_h = max(int(thumb * r.size[1] / r.size[0]) for _, r, _ in rows)
    cell_h = scale_h + cap_h + 2 * pad
    n_rows = math.ceil(len(rows) / cols)
    sheet = Image.new("RGB", (cols * cell_w, n_rows * cell_h + title_h), (235, 235, 235))
    d = ImageDraw.Draw(sheet)
    if title:
        d.text((pad, title_h / 2), title, fill=BLACK, font=_font(26), anchor="lm")
    f = _font(15)
    for i, (cap, ref, alt) in enumerate(rows):
        cx, cy = (i % cols) * cell_w, (i // cols) * cell_h + title_h
        for j, im in enumerate((ref, alt)):
            th = im.resize((thumb, int(thumb * im.size[1] / im.size[0])), Image.Resampling.LANCZOS)
            x, y = cx + pad + j * (thumb + pad), cy + pad
            sheet.paste(th, (x, y))
            d.rectangle([x - 1, y - 1, x + th.size[0], y + th.size[1]], outline=(90, 90, 90))
        d.text((cx + pad, cy + pad + scale_h + cap_h / 2), cap, fill=BLACK, font=f, anchor="lm")
    return sheet
