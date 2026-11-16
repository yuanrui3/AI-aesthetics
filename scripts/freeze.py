"""Write FROZEN.json: the commit, prompt, models and layouts the test split is run with.

    uv run python scripts/freeze.py

Run once, after the owner's Gate 2 approval and before any test stimulus exists.
Refuses if FROZEN.json already exists, if any frozen path has uncommitted changes,
or if a test manifest already exists.
"""
from __future__ import annotations

import datetime
import json
import sys

from aesx.freeze import FROZEN_FILE, FROZEN_PATHS, head, uncommitted
from aesx.manifest import ROOT
from aesx.models.registry import MODELS
from aesx.trials import ASSISTANT_PREFIX, PROMPT_VERSION

# Approved at Gate 2 (2026-11-16): seven models, two images for every experiment,
# side by side additionally for E1, E4 and E5.
MAIN_MODELS = ["qwen3.5-0.8b", "minicpm-v-4.7-1b", "smolvlm2-2.2b", "internvl3.5-2b",
               "north-micro-vision", "qwen3.5-4b", "gemma-4-e2b"]
LAYOUTS = {"apb": ["two", "sbs"], "multiobject": ["two"], "framing": ["two"],
           "colour": ["two", "sbs"], "proportion": ["two", "sbs"]}


def main() -> int:
    if FROZEN_FILE.exists():
        print("Refusing: FROZEN.json already exists. The freeze is written once.", file=sys.stderr)
        return 2
    dirty = uncommitted()
    if dirty:
        print("Refusing: commit these first: " + ", ".join(dirty), file=sys.stderr)
        return 2
    existing = [e for e in LAYOUTS if (ROOT / "stimuli" / e / "test" / "pairs.jsonl").exists()]
    if existing:
        print("Refusing: test manifests already exist for " + ", ".join(existing), file=sys.stderr)
        return 2
    data = {
        "frozen_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "commit": head(),
        "approval": "Gate 2, owner reply 'Approve as recommended', 2026-11-16",
        "prompt_version": PROMPT_VERSION,
        "assistant_prefix": ASSISTANT_PREFIX,
        "primary_layout": "two",
        "layouts": LAYOUTS,
        "models": MAIN_MODELS,
        "model_commits": {m: MODELS[m]["revision"] for m in MAIN_MODELS},
        "refusal_probe": {"n": 60, "max_new_tokens": 160, "seed": 1},
        "frozen_paths": list(FROZEN_PATHS),
    }
    FROZEN_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
