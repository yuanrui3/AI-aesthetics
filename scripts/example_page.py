"""Static page of example pairs, with what each model chose on each pair.

    uv run python scripts/example_page.py --split test --tag test    -> reports/examples/index.html (+ img/)
    uv run python scripts/example_page.py --split dev --tag pilot    -> reports/examples_pilot/ (layout check)

Six pairs per experiment, spread evenly over its conditions. For each pair the page
shows the reference and the manipulated twin, what was changed, what people chose
(where the source reports it), and which models chose which image in the two-image
layout under the "you" framing (bias-cancelled: the sign of the mean log-odds over
the four counterbalanced presentations). Self-contained HTML; images are copied next
to it. Light and dark themes.
"""
from __future__ import annotations

import argparse
import html
import importlib
import shutil
import sys

import pandas as pd

from aesx import analysis
from aesx.manifest import ROOT, read_manifest
from aesx.models.registry import MODELS

EXPS = ("apb", "multiobject", "framing", "colour", "proportion")
PER_EXP = 6
NICE = {"smolvlm2-500m": "SmolVLM2 0.5B", "qwen3.5-0.8b": "Qwen3.5 0.8B", "minicpm-v-4.7-1b": "MiniCPM-V 1.6B",
        "smolvlm2-2.2b": "SmolVLM2 2.2B", "internvl3.5-2b": "InternVL3.5 2.3B", "north-micro-vision": "North Micro 2.5B",
        "qwen3.5-4b": "Qwen3.5 4.7B", "gemma-4-e2b": "Gemma 4 E2B"}
HUMAN = {  # what people chose, per experiment and condition (None = no published choice)
    ("apb", None): "People: balance and liking correlate (r = -.87 over images); no forced choice published.",
    ("multiobject", "balance"): "People: balanced picture chosen 53% of the time, not above chance (Leyssen et al. 2012).",
    ("multiobject", "dose"): "People: not tested at this shift.",
    ("multiobject", "distance"): "People: not comparable (the source's objects were related or unrelated things).",
    ("framing", "flip"): "People: inward-facing view chosen about 74% of the time (Palmer et al. 2008).",
    ("framing", "position"): "People: the best position is near the centre, a little to the side the object faces away from.",
    ("framing", "centre"): "People: the centre is preferred to either quarter line (direction only).",
    ("colour", None): "People: red rated heavier than yellow when the area covers 9-23% of the field (weight, not preference).",
    ("proportion", None): "People: no published figure for generated grids (55% for real Mondrians, against the original).",
}
CSS = """
:root{--bg:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--rule:#e2e1dc;--ref:#2a78d6;--alt:#eb6834}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--rule:#383835;--ref:#3987e5;--alt:#d95926}}
:root[data-theme="dark"]{--bg:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--rule:#383835;--ref:#3987e5;--alt:#d95926}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 64px}h1{font-size:1.6rem;margin:0 0 4px}h2{font-size:1.2rem;margin:40px 0 4px}
p.lede,p.note{color:var(--ink2);margin:4px 0 12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
.card{background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:12px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:8px}.pair figure{margin:0}.pair img{width:100%;height:auto;display:block;border-radius:4px;border:1px solid var(--rule)}
figcaption{font-size:.78rem;color:var(--ink2);margin-top:4px}figcaption b.ref{color:var(--ref)}figcaption b.alt{color:var(--alt)}
.what{font-size:.86rem;margin:8px 0 4px}.human{font-size:.8rem;color:var(--ink2);margin:0 0 6px}
ul.models{list-style:none;padding:0;margin:0;font-size:.8rem}ul.models li{display:flex;justify-content:space-between;border-top:1px solid var(--rule);padding:2px 0}
.tag-ref{color:var(--ref);font-weight:600}.tag-alt{color:var(--alt);font-weight:600}.tag-na{color:var(--ink2)}
"""


def choices(tag: str, split: str) -> dict[tuple[str, str], str]:
    """(model, pair_id) -> 'ref' | 'alt', two-image layout, "you" framing."""
    out = {}
    for run in sorted((ROOT / "runs" / tag).glob("*/results.jsonl")):
        df = analysis.load_results(run)
        pp = analysis.prefer_by_pair(df)
        pp = pp[(pp.layout == "two") & (pp.framing == "you")]
        for pid, c in zip(pp.pair_id, pp.choice_ref):
            out[(run.parent.name, pid)] = "ref" if c == 1 else "alt"
    return out


def pick(pairs: list) -> list:
    manip = [p for p in pairs if p.kind == "manipulation"]
    by: dict[str, list] = {}
    for p in manip:
        by.setdefault(p.condition, []).append(p)
    quota = -(-PER_EXP // len(by))
    out = []
    for group in by.values():
        k = min(quota, len(group))
        out += [group[round(i * (len(group) - 1) / max(1, k - 1))] for i in range(k)]
    return out[:PER_EXP]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    ap.add_argument("--tag", default="test")
    a = ap.parse_args()
    out = ROOT / "reports" / ("examples" if a.tag == "test" else f"examples_{a.tag}")
    shutil.rmtree(out / "img", ignore_errors=True)
    (out / "img").mkdir(parents=True)
    ch = choices(a.tag, a.split)
    models = sorted({m for m, _ in ch}, key=lambda m: MODELS[m]["params_b"])

    body = ["<main>", "<h1>Example pairs</h1>",
            "<p class='lede'>Each pair is a code-generated composition (<b style='color:var(--ref)'>reference</b>) and its "
            "manipulated twin (<b style='color:var(--alt)'>twin</b>). Below each pair: what people chose, where the source "
            f"reports it, and what each model chose ({html.escape(a.tag)} run, two-image layout, &ldquo;you&rdquo; framing, "
            "bias-cancelled over both orders and both letter assignments).</p>"]
    for exp in EXPS:
        mod = importlib.import_module(f"aesx.experiments.{exp}")
        pairs = pick(read_manifest(ROOT / "stimuli" / exp / a.split / "pairs.jsonl"))
        body += [f"<h2>{html.escape(mod.TITLE)}</h2>", "<div class='grid'>"]
        for p in pairs:
            imgs = []
            for role, rel in (("ref", p.ref), ("alt", p.alt)):
                name = f"{exp}_{p.pair_id.split('-', 2)[-1]}_{role}.png"
                shutil.copyfile(ROOT / rel, out / "img" / name)
                imgs.append(name)
            human = HUMAN.get((exp, p.condition)) or HUMAN.get((exp, None), "")
            rows = []
            for m in models:
                c = ch.get((m, p.pair_id))
                cls, txt = {"ref": ("tag-ref", "reference"), "alt": ("tag-alt", "twin"), None: ("tag-na", "not run")}[c]
                rows.append(f"<li><span>{html.escape(NICE.get(m, m))}</span><span class='{cls}'>{txt}</span></li>")
            body += ["<div class='card'><div class='pair'>",
                     f"<figure><img src='img/{imgs[0]}' alt='reference composition' loading='lazy'><figcaption><b class='ref'>Reference</b></figcaption></figure>",
                     f"<figure><img src='img/{imgs[1]}' alt='manipulated twin' loading='lazy'><figcaption><b class='alt'>Twin</b></figcaption></figure>",
                     "</div>", f"<p class='what'>{html.escape(mod.caption(p))}</p>", f"<p class='human'>{html.escape(human)}</p>",
                     "<ul class='models'>" + "".join(rows) + "</ul></div>"]
        body.append("</div>")
    body.append("<p class='note'>Generated by <code>scripts/example_page.py</code>. All images are drawn by code from a "
                "seed; none reproduces an artwork or a real design.</p></main>")
    page = ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'><title>Example pairs</title>"
            f"<style>{CSS}</style></head><body>" + "\n".join(body) + "</body></html>")
    (out / "index.html").write_text(page, encoding="utf-8")
    print(out / "index.html", f"({len(models)} models)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
