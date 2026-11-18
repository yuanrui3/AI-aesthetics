"""NVIDIA addendum: run the frozen two-image trials on hosted models (PLAN.md, "NVIDIA addendum").

    uv run python scripts/run_api.py dry-run                          # counts, payload sizes, time; no network, no key
    uv run python scripts/run_api.py probe gemma-4-31b mistral-large-4   # a few dev presentations each, replies printed
    uv run python scripts/run_api.py run gemma-4-31b --split dev --limit 40
    uv run python scripts/run_api.py run --all --split test           # the addendum run, as FROZEN_API.json fixes it

Results: runs/nvidia-<split>/<model>/results.jsonl, one line per (presentation, pass), appended and
flushed as it goes. Re-running the same command skips what is done, so a run stopped at any point
(Ctrl+C, a daily request cap, a reboot) resumes where it stopped.

The key is read from NVIDIA_API_KEY, or asked for at a hidden prompt, and never printed or stored.
In a plain terminal, where the project's PowerShell scripts may be blocked, run the venv's Python
directly:   .\\.venv\\Scripts\\python.exe scripts/run_api.py probe gemma-4-31b mistral-large-4
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone

from aesx import api_nvidia as api
from aesx.manifest import ROOT, read_manifest
from aesx.trials import PROMPT_VERSION, build_trials

EXPERIMENTS = ("apb", "multiobject", "framing", "colour", "proportion")
API_PATHS = ("src/aesx/api_nvidia.py", "scripts/run_api.py")
FROZEN_API = ROOT / "FROZEN_API.json"
ORDER_SEED = 0
PRIMARY = ["gemma-4-31b", "mistral-large-4"]  # nemotron-3.5-super-vl is the reserve


def trials_for(split: str) -> list:
    """Every two-image presentation of the split, whole pairs in a fixed random order, so any
    prefix of a pass is a random subset of complete pairs."""
    by_pair = defaultdict(list)
    for exp in EXPERIMENTS:
        pairs = read_manifest(ROOT / "stimuli" / exp / split / "pairs.jsonl")
        for t in build_trials(pairs, tasks=("prefer", "samediff"), layouts=("two",)):
            by_pair[t.pair_id].append(t)
    keys = sorted(by_pair)
    random.Random(ORDER_SEED).shuffle(keys)
    return [t for k in keys for t in by_pair[k]]


def require_api_freeze() -> dict:
    """The frozen addendum plan, or exit if the stimulus code or the API code moved since."""
    from aesx import freeze

    freeze.require()  # stimuli, trials and wording exactly as in the main run
    if not FROZEN_API.exists():
        raise SystemExit("Refusing: no FROZEN_API.json. The test split runs only after the dev probe and the freeze.")
    frozen = json.loads(FROZEN_API.read_text(encoding="utf-8"))
    changed = [x for x in freeze._git("diff", "--name-only", frozen["commit"], "--", *API_PATHS).splitlines() if x.strip()]
    changed += [x[3:] for x in freeze._git("status", "--porcelain", "--", *API_PATHS).splitlines() if x.strip()]
    if changed:
        raise SystemExit(f"Refusing: these files differ from the API freeze {frozen['commit'][:10]}: {', '.join(sorted(set(changed)))}")
    return frozen


def done_ids(path) -> set[str]:
    ids = set()
    if path.exists():
        with path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    ids.add(json.loads(line)["trial_id"])
                except (json.JSONDecodeError, KeyError):
                    continue  # a torn last line is simply redone
    return ids


def record(t, model: str, s: int, out: dict) -> dict:
    return {
        "trial_id": f"{t.trial_id}|s={s}", "base_trial_id": t.trial_id, "sample": s, "seed": s,
        "pair_id": t.pair_id, "experiment": t.experiment, "task": t.task, "framing": t.framing,
        "layout": t.layout, "first": t.first, "labels": list(t.labels), "answers": list(t.answers),
        "prompt_version": t.prompt_version, "model": model, "model_id": api.MODELS[model]["id"],
        "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), **out,
    }


def run_pass(client, model: str, trials: list, s: int, run_dir, workers: int, log_every: int = 100) -> str:
    """One pass (one sampled reply per presentation). Returns "done", "rate_limited" or "stopped"."""
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "results.jsonl"
    done = done_ids(path)
    todo = [t for t in trials if f"{t.trial_id}|s={s}" not in done]
    print(f"[{model} pass {s}] {len(trials) - len(todo)} done, {len(todo)} to do -> {path}", flush=True)
    if not todo:
        return "done"
    lock = threading.Lock()
    stop = threading.Event()
    status = {"why": "done", "n": 0, "transient_run": 0, "off_menu": 0}
    t0 = time.time()

    def one(t):
        if stop.is_set():
            return
        try:
            out = api.answer(client, model, t, seed=s)
        except api.Transient as e:
            with lock:
                status["transient_run"] += 1
                print(f"[skip] {t.trial_id}: {e}", flush=True)
                if status["transient_run"] >= 10:
                    status["why"] = "stopped"
                    stop.set()
            return
        except api.RateLimited as e:
            with lock:
                status["why"] = "rate_limited"
                print(f"[rate limited] {e}", flush=True)
            stop.set()
            return
        except api.Fatal as e:
            with lock:
                status["why"] = "stopped"
                print(f"[fatal] {e}", flush=True)
            stop.set()
            return
        with lock:
            f.write(json.dumps(record(t, model, s, out), sort_keys=True) + "\n")
            f.flush()
            status["n"] += 1
            status["transient_run"] = 0
            status["off_menu"] += out["choice"] is None
            n = status["n"]
            if n % log_every == 0 or n == len(todo):
                dt = time.time() - t0
                print(f"[{model} pass {s}] {n}/{len(todo)}  {60 * n / dt:.1f}/min  off-menu {status['off_menu']}  "
                      f"elapsed {dt / 60:.1f} min", flush=True)

    with path.open("a", encoding="utf-8", newline="\n") as f, ThreadPoolExecutor(max_workers=workers) as ex:
        it = iter(todo)
        pending = set()
        try:
            while True:
                while len(pending) < 2 * workers and not stop.is_set():
                    t = next(it, None)
                    if t is None:
                        break
                    pending.add(ex.submit(one, t))
                if not pending:
                    break
                finished, pending = wait(pending, return_when=FIRST_COMPLETED)
                for fut in finished:
                    fut.result()
        except KeyboardInterrupt:
            stop.set()
            print("[interrupted] finishing requests in flight; re-run the same command to resume", flush=True)
            wait(pending)
            return "stopped"
    if status["why"] == "done" and status["n"] < len(todo):
        status["why"] = "stopped"  # some presentations were skipped after retries; a re-run fills them in
    return status["why"]


def cmd_dry_run(a) -> int:
    trials = trials_for(a.split)
    sizes = [len(api.data_uri(p)) for t in trials[:400] for p in t.image_paths]
    body = api.request_body("gemma-4-31b", trials[0], seed=1)
    for part in body["messages"][0]["content"]:
        if part["type"] == "image_url":
            part["image_url"]["url"] = part["image_url"]["url"][:40] + "..."
    by = Counter((t.experiment, t.task) for t in trials)
    print(f"split {a.split}: {len(trials)} two-image presentations per model per pass")
    for k, v in sorted(by.items()):
        print(f"  {k[0]:12s} {k[1]:9s} {v}")
    print(f"image data URI: mean {sum(sizes) / len(sizes) / 1024:.0f} KB, max {max(sizes) / 1024:.0f} KB")
    for models, passes in ((2, 1), (2, 3)):
        n = len(trials) * models * passes
        print(f"{models} models x {passes} pass(es): {n} requests = {n / a.rpm / 60:.1f} h at {a.rpm}/min, "
              f"{n / 10000:.1f} days at 10,000/day")
    print("first request body (images shortened):")
    print(json.dumps(body, indent=1)[:1500])
    return 0


def cmd_probe(a) -> int:
    """A few dev presentations per experiment and task: are two images accepted, do replies parse,
    how fast is it. Plumbing only; nothing about any effect is read from it."""
    picked = defaultdict(list)
    for t in trials_for("dev"):
        if t.first == "ref" and t.labels == ("A", "B") and t.framing in ("you", "plain", "different"):
            if len(picked[(t.experiment, t.task)]) < a.per_cell:
                picked[(t.experiment, t.task)].append(t)
    trials = [t for v in picked.values() for t in v][: a.n]
    unknown = [m for m in a.models if m not in api.MODELS]
    if unknown:
        print(f"Unknown model(s): {', '.join(unknown)}. Known: {', '.join(api.MODELS)}", file=sys.stderr)
        return 2
    client = api.Client(rpm=a.rpm)
    code = 0
    for model in a.models:
        print(f"\n=== probe {model} ({api.MODELS[model]['id']}): {len(trials)} dev presentations ===", flush=True)
        run_dir = ROOT / "runs" / "nvidia-probe" / model
        run_dir.mkdir(parents=True, exist_ok=True)
        with (run_dir / "results.jsonl").open("a", encoding="utf-8", newline="\n") as f:
            for t in trials:
                try:
                    out = api.answer(client, model, t, seed=1)
                except (api.Fatal, api.RateLimited, api.Transient) as e:
                    msg = f"[{type(e).__name__}] {t.trial_id}: {e}"
                    print(msg, flush=True)
                    with (run_dir / "errors.log").open("a", encoding="utf-8", newline="\n") as log:
                        log.write(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {msg}\n")
                    code = 3
                    if isinstance(e, api.RateLimited):
                        return code
                    break  # this model fails; still try the next one
                f.write(json.dumps(record(t, model, 1, out), sort_keys=True) + "\n")
                print(f"{t.experiment:11s} {t.task:8s} {out['seconds']:5.1f}s  {str(out['choice']):4s} "
                      f"{out['reply']!r:40.40}  finish={out['finish_reason']}  "
                      f"tokens={(out['usage'] or {}).get('prompt_tokens')}  served={out['served_model']}  "
                      f"limits={out['limits']}", flush=True)
    print("\nProbe finished. Leave this window open and tell Claude it is done.", flush=True)
    return code


def cmd_run(a) -> int:
    unknown = [m for m in a.models if m not in api.MODELS]
    if unknown:
        print(f"Unknown model(s): {', '.join(unknown)}. Known: {', '.join(api.MODELS)}", file=sys.stderr)
        return 2
    if a.split == "test":
        frozen = require_api_freeze()
        if a.limit or a.passes or a.models or not a.all:
            print("Refusing: the test split runs exactly the frozen design: use --all, with no --limit, --passes "
                  "or model names.", file=sys.stderr)
            return 2
        models, passes = frozen["models"], frozen["passes"]
        meta = {"api_frozen_commit": frozen["commit"]}
    else:
        models = PRIMARY if a.all else a.models
        passes = a.passes or 1
        meta = {}
    if not models:
        print("Name a model, or --all.", file=sys.stderr)
        return 2
    trials = trials_for(a.split)[: a.limit or None]
    client = api.Client(rpm=a.rpm)
    tag = f"nvidia-{a.split}"
    for s in range(1, passes + 1):
        for m in models:
            run_dir = ROOT / "runs" / tag / m
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.json").write_text(json.dumps({
                "model": m, "model_id": api.MODELS[m]["id"], "endpoint": api.ENDPOINT, "sampling": api.SAMPLING,
                "extra": api.MODELS[m]["extra"], "parse_version": api.PARSE_VERSION, "prompt_version": PROMPT_VERSION,
                "split": a.split, "passes": passes, "n_presentations": len(trials), "order_seed": ORDER_SEED, **meta,
            }, indent=2, sort_keys=True), encoding="utf-8")
            why = run_pass(client, m, trials, s, run_dir, workers=a.workers)
            if why == "rate_limited":
                print("Stopped on the request limit. Re-run the same command later; it resumes.", flush=True)
                return 3
            if why == "stopped":
                print("Stopped before the pass finished. Re-run the same command to resume.", flush=True)
                return 4
    print("All passes complete.", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dry-run")
    d.add_argument("--split", default="test", choices=["dev", "test"])
    d.add_argument("--rpm", type=float, default=35)
    p = sub.add_parser("probe")
    p.add_argument("models", nargs="+", help=f"one or more of: {', '.join(api.MODELS)}")
    p.add_argument("--per-cell", type=int, default=2)
    p.add_argument("--n", type=int, default=30)
    p.add_argument("--rpm", type=float, default=20)
    r = sub.add_parser("run")
    r.add_argument("models", nargs="*", default=[], help=f"one or more of: {', '.join(api.MODELS)}")
    r.add_argument("--all", action="store_true", help="the primary models; on the test split, FROZEN_API.json's list")
    r.add_argument("--split", default="dev", choices=["dev", "test"])
    r.add_argument("--passes", type=int, default=0)
    r.add_argument("--limit", type=int, default=0)
    r.add_argument("--rpm", type=float, default=35, help="request starts per minute, across workers (free tier: 40)")
    r.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    return {"dry-run": cmd_dry_run, "probe": cmd_probe, "run": cmd_run}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
