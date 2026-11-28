# Classic aesthetics experiments on vision-language models

Published empirical-aesthetics experiments re-run on vision-language models as forced
choices between a code-generated composition and a controlled manipulation of it. The
score is the model's effect beside the published human one.

- `docs/related.md`: how this differs from existing benchmarks.
- `docs/experiments.md`: the source experiments, their human results, our stimuli, and
  exactly how each model statistic is computed.
- `PLAN.md`: predictions and the rules fixed before the main run.
- `LOG.md`: every tooling and design decision, with its reason.
- `reports/main.md`: the findings (approved at Gate 3), with `reports/readout_math.md`
  and the literature review `reports/VLM aesthetic preference measurement methods.md`.

## Status and what is public

- **The core study is complete:** seven local open-weight models, pre-registered in
  `PLAN.md`, frozen in `FROZEN.json`, reported in `reports/main.md`.
- **The NVIDIA addendum is finished.** It covers Gemma 4 31B and Nemotron 3.5 Super VL on
  NVIDIA's free API. Its design and five amendments were all written before any result was
  opened, and `FROZEN_API.json` pins it.
- **NVIDIA addendum results:** the one-page summary is `reports/nvidia_addendum_summary.md`,
  and the full tables are in `reports/nvidia_addendum.md`.
- **The NVIDIA models' raw replies are not published.** NVIDIA's API Trial Terms of
  Service (section 4.2) do not allow redistributing generated content, so `runs/nvidia-*`
  is left out of the public copy, history included. Results for those models appear only as
  aggregates in the reports.
- **The public copy is a filtered copy of the working repository.** It has the same commits
  and dates. The NVIDIA reply files are removed, and local Windows user paths read `USER`.
- **Licences:** code under MIT (`LICENSE`); documents and data under CC BY 4.0
  (`LICENSE-docs.md`).

## Setup (this machine)

Everything lives inside this folder: a project-local `uv`, Python, package cache and
model cache. Nothing is installed system-wide. In PowerShell, from the project root:

```powershell
. .\scripts\env.ps1     # once per shell
uv sync                 # restore the exact environment from uv.lock
```

## One command per number

| What | Command | Output |
|---|---|---|
| Human effect sizes quoted in the docs | `uv run python scripts/human_effects.py` | printed table (`--json` for the report) |
| Figure values not printed in the papers | `uv run python -I scripts/digitise_figures.py palmer <fig5.png> <fig6.png>` | printed values (page images are not in the repo) |
| Stimuli, manifest and contact sheet for one experiment | `uv run python scripts/make_stimuli.py apb` | `stimuli/apb/dev/` |
| One model over the dev stimuli (resumable) | `uv run python scripts/run_model.py qwen3.5-0.8b` | `runs/dev/<model>/results.jsonl` |
| Position bias and visibility table (Gate 1) | `uv run python scripts/gate1_checks.py` | `reports/gate1_checks.md` |
| Plumbing self-test with a fake model | `uv run python tests/test_plumbing.py` | `plumbing OK` |

Experiments: `apb` (E1 balance), `multiobject` (E2 two objects, the contested null),
`framing` (E3 one object), `colour` (E4 colour swap), `proportion` (E5 altered
proportions). Test-split commands refuse to run until `FROZEN.json` exists.

## Layout

```
src/aesx/            library: rendering, balance score, icons, grids, trials, runner, analysis, effects
src/aesx/experiments one module per source experiment (stimulus generator)
src/aesx/models      local-model backend and the pinned model registry
scripts/             the commands above
stimuli/             manifests (committed) and PNGs (ignored; rebuilt from seeds)
runs/                raw per-trial results
reports/             tables and figures
```
