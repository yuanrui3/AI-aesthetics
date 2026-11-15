"""Where do the two permitted answers fail to dominate, and what does the model want to say instead?

    uv run python scripts/off_menu.py qwen3.5-0.8b
"""
from __future__ import annotations

import sys

from aesx import analysis
from aesx.manifest import ROOT


def main() -> int:
    model = sys.argv[1]
    df = analysis.load_results(ROOT / "runs" / "dev" / model / "results.jsonl")
    print(f"{model}: {len(df)} trials, off-menu rate {df.off_menu.mean():.3f}, median mass {df.mass.median():.3f}")
    g = df.groupby(["task", "layout"]).agg(n=("mass", "size"), off_menu=("off_menu", "mean"),
                                           mass_median=("mass", "median"), mass_p10=("mass", lambda s: s.quantile(0.1)))
    print(g.round(3).to_string())
    print("\nTop tokens on off-menu trials, by task and layout:")
    off = df[df.off_menu]
    for (task, layout), x in off.groupby(["task", "layout"]):
        print(f"  {task:9s} {layout:4s} ", dict(x.top_token.value_counts().head(6)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
