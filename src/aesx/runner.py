"""Resumable trial runner.

A run is a directory holding ``run.json`` (what was asked for) and
``results.jsonl`` (one line per finished trial, appended and flushed as it
goes). Re-running the same command skips every trial_id already present, so a
job killed at any point resumes where it stopped.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Protocol

from PIL import Image

from .manifest import ROOT
from .render import side_by_side
from .trials import Trial


class Scorer(Protocol):
    """A model backend: returns the log-probabilities of the two candidate answers."""

    spec: dict

    def score(self, trial: Trial, images: list[Image.Image]) -> dict: ...


def trial_images(trial: Trial) -> list[Image.Image]:
    """Images in the order the trial's segments consume them."""
    first, second = (Image.open(ROOT / p).convert("RGB") for p in trial.image_paths)
    if trial.layout == "sbs":
        return [side_by_side(first, second, tags=trial.labels)]
    return [first, second]


def done_ids(results_path: Path) -> set[str]:
    if not results_path.exists():
        return set()
    ids = set()
    with results_path.open(encoding="utf-8") as f:
        for line in f:
            try:
                ids.add(json.loads(line)["trial_id"])
            except (json.JSONDecodeError, KeyError):
                continue  # a torn last line from an interrupted write is simply redone
    return ids


def run(trials: list[Trial], scorer: Scorer, run_dir: Path, meta: dict | None = None, log_every: int = 50) -> Path:
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    results_path = run_dir / "results.jsonl"
    (run_dir / "run.json").write_text(
        json.dumps({"model": scorer.spec, "n_trials": len(trials), **(meta or {})}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    done = done_ids(results_path)
    todo = [t for t in trials if t.trial_id not in done]
    print(f"[run] {len(done)} done, {len(todo)} to do -> {results_path}", flush=True)
    t0 = time.time()
    with results_path.open("a", encoding="utf-8", newline="\n") as f:
        for i, t in enumerate(todo, 1):
            out = scorer.score(t, trial_images(t))
            rec = {
                "trial_id": t.trial_id, "pair_id": t.pair_id, "experiment": t.experiment,
                "task": t.task, "framing": t.framing, "layout": t.layout, "first": t.first,
                "labels": list(t.labels), "answers": list(t.answers),
                "prompt_version": t.prompt_version, **out,
            }
            f.write(json.dumps(rec, sort_keys=True) + "\n")
            f.flush()
            if i % log_every == 0 or i == len(todo):
                dt = time.time() - t0
                print(f"[run] {i}/{len(todo)}  {dt / i:.2f} s/trial  elapsed {dt / 60:.1f} min", flush=True)
    return results_path
