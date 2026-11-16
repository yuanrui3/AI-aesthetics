"""Generate the stimuli, manifest and contact sheet for one experiment.

    uv run python scripts/make_stimuli.py apb              # dev split
    uv run python scripts/make_stimuli.py apb --split test # refused unless the code matches FROZEN.json

Test stimuli are only generated after prompts and presentation have been frozen
(see PLAN.md); the freeze is recorded in FROZEN.json at the project root and checked
by aesx.freeze.require().
"""
from __future__ import annotations

import argparse
import importlib
import sys
import time

from PIL import Image

from aesx.manifest import ROOT, verify_manifest, write_manifest
from aesx.render import contact_sheet


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("experiment")
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--units", type=int, default=None, help="override the number of units (smoke tests only)")
    ap.add_argument("--sheet-pairs", type=int, default=18)
    a = ap.parse_args()

    if a.split == "test":
        from aesx import freeze

        freeze.require()  # exits unless FROZEN.json exists and the code matches the frozen commit
        if a.units is not None:
            print("Refusing: --units is for smoke tests on dev only.", file=sys.stderr)
            return 2

    mod = importlib.import_module(f"aesx.experiments.{a.experiment}")
    t0 = time.time()
    pairs = mod.generate(a.split, a.units or mod.UNITS[a.split])
    out = ROOT / "stimuli" / mod.NAME / a.split
    write_manifest(out / "pairs.jsonl", pairs)
    assert verify_manifest(out / "pairs.jsonl") == []
    manip = [p for p in pairs if p.kind == "manipulation"]
    print(f"{mod.NAME}/{a.split}: {len(manip)} manipulation pairs + {len(pairs) - len(manip)} identical "
          f"in {time.time() - t0:.1f}s -> {out / 'pairs.jsonl'}")

    if a.split == "dev":
        # The same number of examples from every condition, evenly spaced through the manifest,
        # so the sheet shows every kind of pair and a spread of doses.
        by_cond: dict[str, list] = {}
        for p in manip:
            by_cond.setdefault(p.condition, []).append(p)
        quota = -(-a.sheet_pairs // len(by_cond))
        shown = []
        for group in by_cond.values():
            k = min(quota, len(group))
            shown += [group[round(i * (len(group) - 1) / max(1, k - 1))] for i in range(k)]
        shown = shown[: a.sheet_pairs]
        rows = [(mod.caption(p), Image.open(ROOT / p.ref), Image.open(ROOT / p.alt)) for p in shown]
        sheet = contact_sheet(rows, title=f"{mod.TITLE}   (left: reference, right: manipulated twin)")
        sheet.save(out / f"contact_{mod.NAME}.png")
        print("contact sheet ->", out / f"contact_{mod.NAME}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
