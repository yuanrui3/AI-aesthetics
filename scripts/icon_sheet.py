"""Draw every icon once (directed icons facing right, then left) for a visual check.

    uv run python scripts/icon_sheet.py   ->  stimuli/_icons/contact_icons.png
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from aesx.icons import DIRECTED, PALETTE, SYMMETRIC, draw_icon
from aesx.manifest import ROOT
from aesx.render import BLACK, WHITE, Canvas, _font

CELL_W, CELL_H = 200, 170
COLS = 8


def cell(icon, colour, facing=1):
    c = Canvas(CELL_W, CELL_H, WHITE)
    c.rect(0, CELL_H * 0.62, CELL_W, CELL_H, BLACK)
    h = min(90.0, 150.0 / icon.aspect)
    draw_icon(c, icon, CELL_W / 2, CELL_H * 0.78, h, colour, facing)
    im = c.image()
    ImageDraw.Draw(im).text((6, 4), f"{icon.name}{'' if facing == 1 else ' (L)'}", fill=BLACK, font=_font(14))
    return im


def main() -> None:
    cols = list(PALETTE.values())
    cells = [cell(ic, cols[k % len(cols)]) for k, ic in enumerate(DIRECTED)]
    cells += [cell(ic, cols[k % len(cols)], -1) for k, ic in enumerate(DIRECTED)]
    cells += [cell(ic, cols[(k + 3) % len(cols)]) for k, ic in enumerate(SYMMETRIC)]
    rows = -(-len(cells) // COLS)
    sheet = Image.new("RGB", (COLS * CELL_W, rows * CELL_H), (200, 200, 200))
    for k, im in enumerate(cells):
        sheet.paste(im, ((k % COLS) * CELL_W, (k // COLS) * CELL_H))
    out = ROOT / "stimuli" / "_icons" / "contact_icons.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()
