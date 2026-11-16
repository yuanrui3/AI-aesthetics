"""Run several models, at most two at a time, without overfilling the GPU.

    uv run python scripts/run_batch.py --split dev                 # Gate 2 pilot -> runs/pilot
    uv run python scripts/run_batch.py --split test                # main run: the models in FROZEN.json -> runs/test
    uv run python scripts/run_batch.py --split test qwen3.5-4b     # a subset (e.g. to resume one model)

For each model: the trials (resumable: finished trials are skipped), then the
free-text refusal probe. A job starts only when its memory reservation fits beside
the jobs already running. Logs go to runs/<tag>/<model>/log.txt. The script exits
when every job has finished, so nothing is left running.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time

from aesx.manifest import ROOT

# Memory to reserve per model, in MiB: measured pilot peaks plus margin.
MEM = {
    "qwen3.5-4b": 11500,
    "gemma-4-e2b": 12500,
    "smolvlm2-500m": 3000,
    "qwen3.5-0.8b": 3500,
    "minicpm-v-4.7-1b": 5000,
    "internvl3.5-2b": 7500,
    "north-micro-vision": 7000,
    "smolvlm2-2.2b": 7000,
}
MAX_PARALLEL = 2
HEADROOM = 800  # MiB kept free


def gpu_total() -> int:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, check=True).stdout
    return int(out.strip().splitlines()[0])


def command(model: str, split: str) -> str:
    py, s = f'"{sys.executable}"', ROOT / "scripts"
    if split == "dev":
        return f'{py} "{s / "run_model.py"}" {model} --pilot && {py} "{s / "refusal_probe.py"}" {model} --n 60'
    return (f'{py} "{s / "run_model.py"}" {model} --split test && '
            f'{py} "{s / "refusal_probe.py"}" {model} --split test --n 60')


def launch(model: str, split: str) -> subprocess.Popen:
    d = ROOT / "runs" / ("pilot" if split == "dev" else "test") / model
    d.mkdir(parents=True, exist_ok=True)
    log = (d / "log.txt").open("a", encoding="utf-8")
    return subprocess.Popen(command(model, split), shell=True, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("models", nargs="*")
    a = ap.parse_args()
    if a.split == "test":
        allowed = json.loads((ROOT / "FROZEN.json").read_text(encoding="utf-8"))["models"]
    else:
        allowed = list(MEM)
    queue = [(m, MEM[m]) for m in MEM if m in allowed and (not a.models or m in a.models)]

    running: dict[str, tuple[subprocess.Popen, int, float]] = {}
    reserved, total = 0, gpu_total()
    t0 = time.time()
    failed = []
    while queue or running:
        for name, (proc, need, started) in list(running.items()):
            if proc.poll() is not None:
                print(f"[{(time.time() - t0) / 60:6.1f} min] done  {name}  exit {proc.returncode}  ({(time.time() - started) / 60:.1f} min)", flush=True)
                if proc.returncode:
                    failed.append(name)
                reserved -= need
                del running[name]
        if queue and len(running) < MAX_PARALLEL:
            # Reservations, not live free memory, decide: a job that has just started has not allocated yet.
            for i, (name, need) in enumerate(queue):
                if reserved + need + HEADROOM <= total:
                    running[name] = (launch(name, a.split), need, time.time())
                    reserved += need
                    queue.pop(i)
                    print(f"[{(time.time() - t0) / 60:6.1f} min] start {name}  (reserved {reserved} of {total} MiB)", flush=True)
                    break
        time.sleep(15)
    print(f"all done in {(time.time() - t0) / 60:.1f} min; failed: {failed or 'none'}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
