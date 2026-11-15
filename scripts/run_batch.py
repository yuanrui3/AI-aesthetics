"""Run the pilot for several models, at most two at a time, without overfilling the GPU.

    uv run python scripts/run_batch.py                      # every Tier 1 candidate
    uv run python scripts/run_batch.py qwen3.5-0.8b gemma-4-e2b

For each model: the pilot trials (resumable), then the free-text refusal probe.
A job starts only when the GPU has its estimated memory free. Logs go to
runs/pilot/<model>/log.txt. The script exits when every job has finished, so
nothing is left running.
"""
from __future__ import annotations

import subprocess
import sys
import time

from aesx.manifest import ROOT

# (model, memory to reserve in MiB). Estimates with margin; measured peaks are written to timing.json.
JOBS = [
    ("qwen3.5-4b", 11500),
    ("gemma-4-e2b", 12500),
    ("smolvlm2-500m", 3000),
    ("qwen3.5-0.8b", 3500),
    ("minicpm-v-4.7-1b", 5000),
    ("internvl3.5-2b", 7500),
    ("north-micro-vision", 7000),
    ("smolvlm2-2.2b", 7000),
]
MAX_PARALLEL = 2
HEADROOM = 800  # MiB kept free


def gpu_total() -> int:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, check=True).stdout
    return int(out.strip().splitlines()[0])


def launch(model: str) -> subprocess.Popen:
    d = ROOT / "runs" / "pilot" / model
    d.mkdir(parents=True, exist_ok=True)
    log = (d / "log.txt").open("a", encoding="utf-8")
    py = sys.executable
    cmd = (f'"{py}" "{ROOT / "scripts" / "run_model.py"}" {model} --pilot && '
           f'"{py}" "{ROOT / "scripts" / "refusal_probe.py"}" {model} --n 60')
    return subprocess.Popen(cmd, shell=True, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)


def main() -> int:
    wanted = sys.argv[1:]
    queue = [j for j in JOBS if not wanted or j[0] in wanted]
    running: dict[str, tuple[subprocess.Popen, int, float]] = {}
    reserved, total = 0, gpu_total()
    t0 = time.time()
    while queue or running:
        for name, (proc, need, started) in list(running.items()):
            if proc.poll() is not None:
                print(f"[{(time.time() - t0) / 60:6.1f} min] done  {name}  exit {proc.returncode}  ({(time.time() - started) / 60:.1f} min)", flush=True)
                reserved -= need
                del running[name]
        if queue and len(running) < MAX_PARALLEL:
            # Start the first queued job whose reservation fits beside those already running.
            # Reservations, not live free memory, decide: a job that has just started has not
            # allocated yet.
            for i, (name, need) in enumerate(queue):
                if reserved + need + HEADROOM <= total:
                    running[name] = (launch(name), need, time.time())
                    reserved += need
                    queue.pop(i)
                    print(f"[{(time.time() - t0) / 60:6.1f} min] start {name}  (reserved {reserved} of {total} MiB)", flush=True)
                    break
        time.sleep(15)
    print(f"all done in {(time.time() - t0) / 60:.1f} min", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
