"""Does NVIDIA's endpoint honour the request seed? Dev presentations only; plumbing, not results.

    .\\.venv\\Scripts\\python.exe scripts/seed_check.py gemma-4-31b nemotron-3.5-super-vl

For each of a few dev preference presentations it sends R requests with one fixed seed and R
with R different seeds (interleaved), at temperature 1 as in the run.

- If the fixed-seed repeats are always identical while different seeds sometimes disagree,
  the server seeds each request's sampler: the first test run's one-seed-per-pass design then
  coupled every reply in a pass, and its replies are set aside (PLAN.md, second amendment).
- If fixed-seed repeats disagree as often as different seeds do, the seed is ignored, draws
  were independent anyway, and the first run's replies are valid.
- If nothing varies at all (the model is certain on every presentation), the check is
  inconclusive and more or less certain presentations are needed.

Replies go to runs/nvidia-seedcheck/<model>/results.jsonl. The key is asked for once, hidden.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aesx import api_nvidia as api  # noqa: E402
from aesx.manifest import ROOT  # noqa: E402
import run_api  # noqa: E402

FIXED_SEED = 1


def pick(n: int, experiments: set[str] | None = None) -> list:
    """n dev preference presentations, spread over experiments (or only the ones named),
    identical pairs included (they are where a model is least certain)."""
    by_exp = defaultdict(list)
    for t in run_api.trials_for("dev"):
        if t.task == "prefer" and t.framing == "you" and t.labels == ("A", "B"):
            if experiments is None or t.experiment in experiments:
                by_exp[t.experiment].append(t)
    out, i = [], 0
    while len(out) < n and any(by_exp.values()):
        for exp in sorted(by_exp):
            if by_exp[exp] and len(out) < n:
                out.append(by_exp[exp].pop(i % max(len(by_exp[exp]), 1)))
        i += 7
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("models", nargs="+")
    ap.add_argument("--n", type=int, default=10, help="presentations per model")
    ap.add_argument("--repeats", type=int, default=4, help="requests per seed condition per presentation")
    ap.add_argument("--rpm", type=float, default=30)
    ap.add_argument("--experiments", default="", help="comma list, e.g. framing: where a model is least certain")
    ap.add_argument("--offset", type=int, default=0, help="skip this many picked presentations (fresh ones for a follow-up)")
    a = ap.parse_args()
    unknown = [m for m in a.models if m not in api.MODELS]
    if unknown:
        print(f"Unknown model(s): {', '.join(unknown)}", file=sys.stderr)
        return 2
    exps = set(a.experiments.split(",")) if a.experiments else None
    trials = pick(a.n + a.offset, exps)[a.offset:]
    client = api.Client(rpm=a.rpm)
    verdicts = {}
    for model in a.models:
        run_dir = ROOT / "runs" / "nvidia-seedcheck" / model
        run_dir.mkdir(parents=True, exist_ok=True)
        fixed_vary = diff_vary = 0
        print(f"\n=== {model}: {len(trials)} dev presentations x {a.repeats} fixed-seed + {a.repeats} different-seed requests", flush=True)
        with (run_dir / "results.jsonl").open("a", encoding="utf-8", newline="\n") as f:
            for t in trials:
                replies = {"fixed": [], "different": []}
                for r in range(a.repeats):
                    for cond, seed in (("fixed", FIXED_SEED), ("different", 1000 + r)):
                        try:
                            out = api.answer(client, model, t, seed=seed)
                        except (api.Fatal, api.RateLimited, api.Transient) as e:
                            print(f"[{type(e).__name__}] {e}", flush=True)
                            return 3
                        replies[cond].append(out["reply"])
                        f.write(json.dumps({"model": model, "trial_id": t.trial_id, "condition": cond, "seed": seed,
                                            "reply": out["reply"], "utc": datetime.now(timezone.utc).isoformat(timespec="seconds")},
                                           sort_keys=True) + "\n")
                        f.flush()
                fv, dv = len(set(replies["fixed"])) > 1, len(set(replies["different"])) > 1
                fixed_vary += fv
                diff_vary += dv
                print(f"  {t.experiment:11s} fixed seed: {''.join(str(x)[:1] for x in replies['fixed'])}"
                      f"   different seeds: {''.join(str(x)[:1] for x in replies['different'])}", flush=True)
        if fixed_vary == 0 and diff_vary > 0:
            v = "SEED HONOURED: same seed gives the same reply; one seed per pass coupled the replies"
        elif fixed_vary > 0:
            v = "SEED NOT HONOURED (or not deterministic): same-seed repeats differ; draws were independent"
        else:
            v = "INCONCLUSIVE: no variation under either condition; the model was certain on every presentation"
        verdicts[model] = v
        print(f"  -> presentations varying: fixed seed {fixed_vary}/{len(trials)}, different seeds {diff_vary}/{len(trials)}")
        print(f"  -> {v}", flush=True)
    print("\nSeed check finished. Leave this window open and tell Claude it is done.")
    (ROOT / "runs" / "nvidia-seedcheck" / "verdicts.json").write_text(json.dumps(verdicts, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
