"""Run one local model over one split. Resumable: re-running skips finished trials.

    uv run python scripts/run_model.py smolvlm2-500m --split dev
    uv run python scripts/run_model.py smolvlm2-500m --split dev --probe 6   # print prompts + free-text replies only

Results go to runs/<split>/<model>/results.jsonl (one line per trial).
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from aesx import runner
from aesx.manifest import ROOT, read_manifest
from aesx.models import registry
from aesx.trials import PROMPT_VERSION, build_trials

EXPERIMENTS = ("apb", "multiobject", "framing", "colour", "proportion")


def gpu_free_mib() -> int:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, check=True).stdout
    return int(out.strip().splitlines()[0])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=sorted(registry.MODELS))
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--experiments", default=",".join(EXPERIMENTS))
    ap.add_argument("--layouts", default="two,sbs")
    ap.add_argument("--tasks", default="prefer,samediff")
    ap.add_argument("--max-pairs", type=int, default=None, help="first N pairs per experiment (pilot)")
    ap.add_argument("--probe", type=int, default=0, help="print N prompts with free-text replies and exit")
    a = ap.parse_args()

    if a.split == "test" and not (ROOT / "FROZEN.json").exists():
        print("Refusing: the test split is run only after the freeze (no FROZEN.json).", file=sys.stderr)
        return 2

    trials = []
    for exp in a.experiments.split(","):
        man = ROOT / "stimuli" / exp / a.split / "pairs.jsonl"
        if not man.exists():
            print(f"[skip] no manifest for {exp}/{a.split}")
            continue
        pairs = read_manifest(man)
        if a.max_pairs:
            manip = [p for p in pairs if p.kind == "manipulation"][: a.max_pairs]
            ident = [p for p in pairs if p.kind == "identical"][: max(4, a.max_pairs // 5)]
            pairs = manip + ident
        trials += build_trials(pairs, tasks=tuple(a.tasks.split(",")), layouts=tuple(a.layouts.split(",")))
    print(f"{len(trials)} trials, prompt version {PROMPT_VERSION}; GPU free {gpu_free_mib()} MiB")

    scorer = registry.load(a.model)
    print("loaded", scorer.spec)

    if a.probe:
        step = max(1, len(trials) // a.probe)
        for t in trials[::step][: a.probe]:
            ims = runner.trial_images(t)
            print("\n---", t.trial_id)
            print(scorer.prompt_text(t, ims)[-420:])
            print("answer ids:", {x: scorer.answer_ids(x) for x in t.answers})
            print("score:", scorer.score(t, ims))
            print("free text:", repr(scorer.generate(t, ims)))
        return 0

    run_dir = ROOT / "runs" / a.split / a.model
    runner.run(trials, scorer, run_dir, meta={"split": a.split, "prompt_version": PROMPT_VERSION})
    return 0


if __name__ == "__main__":
    sys.exit(main())
