"""Run one local model over one split. Resumable: re-running skips finished trials.

    uv run python scripts/run_model.py qwen3.5-0.8b                    # all dev pairs -> runs/dev/<model>
    uv run python scripts/run_model.py qwen3.5-0.8b --pilot            # about 40 pairs per experiment -> runs/pilot/<model>
    uv run python scripts/run_model.py qwen3.5-0.8b --probe 6          # print prompts + free-text replies only

Results go to runs/<tag>/<model>/results.jsonl (one line per trial); timing to run.json.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time

from aesx import runner
from aesx.manifest import ROOT, read_manifest
from aesx.models import registry
from aesx.subsets import pilot_subset
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
    ap.add_argument("--tag", default=None, help="run directory name under runs/ (default: the split, or 'pilot')")
    ap.add_argument("--pilot", action="store_true", help="the Gate 2 pilot subset of the dev split")
    ap.add_argument("--experiments", default=",".join(EXPERIMENTS))
    ap.add_argument("--layouts", default="two,sbs")
    ap.add_argument("--tasks", default="prefer,samediff")
    ap.add_argument("--probe", type=int, default=0, help="print N prompts with free-text replies and exit")
    a = ap.parse_args()

    if a.split == "test" and not (ROOT / "FROZEN.json").exists():
        print("Refusing: the test split is run only after the freeze (no FROZEN.json).", file=sys.stderr)
        return 2
    tag = a.tag or ("pilot" if a.pilot else a.split)

    trials = []
    for exp in a.experiments.split(","):
        man = ROOT / "stimuli" / exp / a.split / "pairs.jsonl"
        if not man.exists():
            print(f"[skip] no manifest for {exp}/{a.split}")
            continue
        pairs = read_manifest(man)
        if a.pilot:
            pairs = pilot_subset(pairs)
        trials += build_trials(pairs, tasks=tuple(a.tasks.split(",")), layouts=tuple(a.layouts.split(",")))
    print(f"{len(trials)} trials, prompt version {PROMPT_VERSION}; GPU free {gpu_free_mib()} MiB", flush=True)

    scorer = registry.load(a.model)
    print("loaded", scorer.spec, flush=True)

    if a.probe:
        step = max(1, len(trials) // a.probe)
        for t in trials[::step][: a.probe]:
            ims = runner.trial_images(t)
            print("\n---", t.trial_id)
            print(scorer.prompt_text(t, ims)[-460:])
            print("answer ids:", {x: scorer.answer_ids(x) for x in t.answers})
            print("score:", scorer.score(t, ims))
            print("free text:", repr(scorer.generate(t, ims)))
        return 0

    run_dir = ROOT / "runs" / tag / a.model
    n_before = len(runner.done_ids(run_dir / "results.jsonl"))
    t0 = time.time()
    runner.run(trials, scorer, run_dir, meta={"split": a.split, "tag": tag, "prompt_version": PROMPT_VERSION})
    done = len(trials) - n_before
    if done > 0:  # timing of this invocation, for the main-run estimate
        import torch

        timing = {"trials_this_invocation": done, "seconds": round(time.time() - t0, 1),
                  "seconds_per_trial": round((time.time() - t0) / done, 4),
                  "peak_vram_mib": int(torch.cuda.max_memory_allocated() / 2**20)}
        (run_dir / "timing.json").write_text(json.dumps(timing, indent=2), encoding="utf-8")
        print("timing", timing, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
