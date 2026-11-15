"""Prompt development on DEV stimuli only: does a wording change keep a model on the
two permitted answers? Compares variants of the final instruction on the same trials.

    uv run python scripts/prompt_probe.py qwen3.5-0.8b --layout sbs --n 80

Prints, per variant: mean probability mass on the two answers, the off-menu rate, the
mean log-odds toward the first/left image, and how strongly the variant's per-trial
log-odds agree with the current wording (so a variant that merely adds noise is visible).
"""
from __future__ import annotations

import argparse
import copy
import sys

import numpy as np

from aesx import runner
from aesx.manifest import ROOT, read_manifest
from aesx.models import registry
from aesx.trials import build_trials

# Each variant: (change to the user-turn text, text the assistant turn is started with).
# "current" is the dev-1 wording the Gate 1 checks used; "answer_colon" was dev-2;
# "assistant_prefix" is dev-3, the wording the pilot uses.
VARIANTS = {
    "current": (lambda text: text, ""),
    "answer_colon": (lambda text: text + "\nAnswer:", ""),
    "letter_first": (lambda text: text.replace("Answer with one letter only:", "Reply with just the letter, nothing else:"), ""),
    "both": (lambda text: text.replace("Answer with one letter only:", "Reply with just the letter, nothing else:") + "\nAnswer:", ""),
    "assistant_prefix": (lambda text: text, "Answer:"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--layout", default="sbs")
    ap.add_argument("--n", type=int, default=80)
    a = ap.parse_args()

    trials = []
    for exp in ("apb", "multiobject", "framing", "colour", "proportion"):
        pairs = read_manifest(ROOT / "stimuli" / exp / "dev" / "pairs.jsonl")
        trials += [t for t in build_trials(pairs, tasks=("prefer",), layouts=(a.layout,), framings=("you",)) if t.task == "prefer"]
    rng = np.random.default_rng(0)
    trials = [trials[int(i)] for i in rng.choice(len(trials), size=a.n, replace=False)]

    scorer = registry.load(a.model)
    out = {}
    for name, (fn, prefix) in VARIANTS.items():
        mass, lo = [], []
        for t in trials:
            t2 = copy.deepcopy(t)
            t2.segments[-1][1] = fn(t2.segments[-1][1])
            t2.assistant_prefix = prefix
            r = scorer.score(t2, runner.trial_images(t2))
            mass.append(r["mass"])
            lo.append(r["lp_first"] - r["lp_second"])
        out[name] = (np.array(mass), np.array(lo))
    base = out["current"][1]
    print(f"{a.model}, layout {a.layout}, {a.n} dev preference trials")
    print(f"{'variant':14s} {'mean mass':>9s} {'off-menu':>9s} {'lo_first':>9s} {'r with current':>15s}")
    for name, (mass, lo) in out.items():
        print(f"{name:14s} {mass.mean():9.3f} {(mass < 0.5).mean():9.3f} {lo.mean():9.2f} {np.corrcoef(base, lo)[0, 1]:15.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
