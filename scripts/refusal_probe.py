"""What does a model say when it answers a preference trial unaided?

The scored readout starts the reply with "Answer:" and reads the next token, which
cannot refuse. This probe lets the model write freely on a sample of the same
trials and classifies each reply, so that genuine refusals are counted (the brief's
rule: a model refusing more than a fifth of trials is reported as refusing) and so
that the forced readout can be checked against the model's own unaided answer.

    uv run python scripts/refusal_probe.py gemma-4-e2b --n 60                # dev pilot subset
    uv run python scripts/refusal_probe.py gemma-4-e2b --split test --n 60   # main run (frozen design)
    -> runs/<pilot|test>/<model>/free_text.jsonl, runs/<pilot|test>/<model>/refusal_probe.json

Classes:  direct   the reply opens with one of the two letters
          commits  the reply names one letter as its choice later on
          refuses  no choice, and wording that declines (cannot, no personal preference...)
          unclear  anything else (usually a preamble cut off before the choice)
"""
from __future__ import annotations

import argparse
import json
import re
import sys

import numpy as np

from aesx import runner
from aesx.manifest import ROOT, read_manifest
from aesx.models import registry
from aesx.subsets import pilot_subset
from aesx.trials import build_trials

EXPS = ("apb", "multiobject", "framing", "colour", "proportion")
DECLINE = re.compile(r"\b(cannot|can't|can not|unable to|don't have (?:personal )?preferences?|do not have (?:personal )?preferences?"
                     r"|as an ai|i'm not able|no personal)\b", re.I)
# a letter presented as a choice: "Image B", "**B**", "(B)", "option B", "answer is B", "choose B"
CHOICE = re.compile(r"(?:\b[Ii]mage\s+|\b[Oo]ption\s+|\b[Aa]nswer(?:\s+is)?:?\s+|\b(?:choose|pick|select|prefer)\s+|\*\*\(?|\()([AB])\b")


def classify(text: str) -> tuple[str, str | None]:
    t = text.strip()
    m = re.match(r"^\**\(?([AB])\)?\**(?:[\s\.\,:\)]|$)", t)
    if m:
        return "direct", m.group(1)
    found = CHOICE.findall(t)
    if found:
        return "commits", found[-1]  # the last letter named as a choice is the conclusion
    return ("refuses" if DECLINE.search(t) else "unclear"), None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--max-new-tokens", type=int, default=160)
    a = ap.parse_args()

    frozen = None
    if a.split == "test":
        from aesx import freeze

        frozen = freeze.require()
        if a.n != frozen["refusal_probe"]["n"] or a.max_new_tokens != frozen["refusal_probe"]["max_new_tokens"]:
            print("Refusing: the test-split probe uses the frozen size and length.", file=sys.stderr)
            return 2
    trials = []
    for exp in EXPS:
        pairs = read_manifest(ROOT / "stimuli" / exp / a.split / "pairs.jsonl")
        if frozen:  # the trials the main run scores, in the frozen layouts
            layouts = tuple(frozen["layouts"][exp])
        else:  # the Gate 2 pilot subset, both layouts
            pairs, layouts = pilot_subset(pairs), ("two", "sbs")
        trials += [t for t in build_trials(pairs, tasks=("prefer",), layouts=layouts) if t.task == "prefer"]
    rng = np.random.default_rng(1)
    trials = [trials[int(i)] for i in rng.choice(len(trials), size=a.n, replace=False)]

    scorer = registry.load(a.model)
    out_dir = ROOT / "runs" / ("test" if frozen else "pilot") / a.model
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    with (out_dir / "free_text.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for t in trials:
            ims = runner.trial_images(t)
            text = scorer.generate(t, ims, max_new_tokens=a.max_new_tokens, use_prefix=False)
            cls, letter = classify(text)
            forced = scorer.score(t, ims)  # the scored readout on the same trial
            forced_letter = t.answers[0] if forced["lp_first"] > forced["lp_second"] else t.answers[1]
            row = {"trial_id": t.trial_id, "layout": t.layout, "class": cls, "letter": letter,
                   "forced_letter": forced_letter, "forced_mass": forced["mass"], "text": text}
            rows.append(row)
            f.write(json.dumps(row) + "\n")
            f.flush()

    n = len(rows)
    share = {c: sum(r["class"] == c for r in rows) / n for c in ("direct", "commits", "refuses", "unclear")}
    parsed = [r for r in rows if r["letter"]]
    agree = sum(r["letter"] == r["forced_letter"] for r in parsed) / len(parsed) if parsed else float("nan")
    summary = {"model": a.model, "n": n, **{k: round(v, 3) for k, v in share.items()},
               "n_parsed": len(parsed), "agreement_with_forced_readout": round(agree, 3),
               "max_new_tokens": a.max_new_tokens}
    (out_dir / "refusal_probe.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
