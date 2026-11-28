# Decision log

One line per decision, newest at the bottom. Format: date, decision, reason.

## 2026-11-14 (session 1)

- **Machine found:** RTX 4090 Laptop GPU, 16 GB VRAM (16.0 GB free at start), 64 GB RAM,
  2.4 TB free disk, git 2.49. No Python on the machine (only the Microsoft Store stub).
- **Python: project-local via uv, not a system install.** uv 0.13.8 unpacked to
  `.tools/uv` (SHA-256 checked against the release's own checksum file), CPython 3.12.16
  installed to `.tools/python` with `--no-bin --no-registry`. Reason: the machine is
  shared; this needs no administrator rights and touches no PATH, registry or profile.
  Deleting the project folder removes everything.
- **All caches inside the project** (`.cache/uv`, `.cache/hf`, `.cache/torch`,
  `.cache/mpl`), set by `scripts/env.ps1`. Reason: Hugging Face would otherwise put
  multi-GB weights in the user profile, outside the project folder.
- **Python 3.12, not newer.** Reason: safest target for PyTorch CUDA wheels on Windows.
- **uv project with a lockfile (`uv.lock`)** rather than a loose requirements file.
  Reason: "pinned versions, one command per reported number".
- **Generated PNGs are git-ignored; manifests (seed + parameters + SHA-256) are
  committed.** Reason: stimuli are reproducible from seeds, and the repo stays small.
- **Literature search delegated to parallel readers, one per source experiment**, each
  told to tag every number as full-text, abstract or secondary. Reason: five papers plus
  replications is a lot of reading; numbers that go into `docs/experiments.md` are
  spot-checked by me against the PDF before being written down.
- **Paper PDFs stay in the session scratch folder, not in the repo.** Reason: they are
  copyrighted; the repo cites them and records page numbers instead.
- **PyTorch 2.15.0 + CUDA 13.2 wheels, transformers 5.23.0** (exact pins in `uv.lock`).
  Reason: current stable on 2026-11-14; the cu132 build needs driver 580 or newer and
  this machine has 581.95, so no driver change is needed.
- **Models are pinned to a commit hash** in `src/aesx/models/registry.py`, and the commit
  actually loaded is written into each run's `run.json`. Reason: reproducibility.
- **Each model's default image preprocessing is left alone** (tiling, resizing, token
  budget). Reason: tuning it per model would be a hidden degree of freedom; the defaults
  are what a user of the model gets.
- **Stimulus sizes:** 512 x 512 (balance), 680 x 430 (two objects, as the source),
  512 x 384 (one object, 4:3 as the source). Reason: source geometry is specified
  relative to the frame, and about 512 px keeps token counts modest on every model.
- **Trial = 2 orders x 2 letter assignments x 2 framings x 2 layouts.** Reason: order and
  letter biases are then separable from preference and cancel in the per-pair mean.
- **Scoring reads the next-token log-probabilities of the two permitted answers**, summing
  over spellings with and without a leading space. "Refusal" for a local model is defined
  as a trial where those answers hold under half the probability (`off_menu`). Reason: a
  forced log-probability readout cannot refuse, so this is the nearest observable thing.
- **E1 balance: pairs are layouts of the same seven elements**, five levels per family,
  all ten pairs compared. Reason: only the arrangement differs within a pair, the dose
  spans the source's range, and a complete design gives each image a scale value so the
  source's statistic (r between balance score and preference) can be computed.
- **E1: high balance scores must come from weight pushed off-centre.** Reason: an
  unconstrained search reached high scores by clumping elements in the middle, which the
  formula penalises but the source's stimuli did not contain (its Figure 3).
- **E2 uses two abstract shapes; E3 uses schematic icons drawn in code.** Reason: both
  sources used pictures of real objects, which cannot be regenerated from a description.
  E3 needs objects with a front, hence icons; E2 is kept abstract as the brief describes,
  with the icon variant offered to the owner at Gate 1.
- **E3 icons are split between dev and test** (no test icon is seen during development).
  Reason: the no-tuning-on-test rule, applied to object identity as well as seeds.
- **Bootstrap resamples clusters** (a family in E1, a unit in E2, an icon in E3).
  Reason: pairs sharing images are not independent stimuli.

- **E4 asks a weight question as well as preference; E5 is kept as an unanchored
  control.** Reason: Locher (2005) measured perceived weight, not preference, on
  adaptations of real paintings, and McManus (1993) scores against the artist's original.
  Neither source effect can be reproduced with generated grids, so each is reduced to the
  part that can be, and labelled. Owner decides at Gate 1 (options in
  `docs/experiments.md`).
- **Figure values are measured by script, not by eye** (`scripts/digitise_figures.py`).
  Reason: "one command per reported number". Check: the two markers at each position of
  Palmer's Figure 5 must sum to 100 and do to within 0.7.
- **Bootstrap computed from per-cluster arrays, 2,000 resamples.** Reason: the first
  version rebuilt data frames per resample and did not finish in ten minutes.
- **Prompt candidate dev-2: append "Answer:" on a new line after the instruction.**
  Reason: with dev-1, Qwen3.5-0.8B put under half the probability on the two letters in
  50% of side-by-side preference trials (it starts a sentence: "Looking at..."). On 80
  dev trials the suffix cut that to 11%, left the two-image layout unchanged, and kept
  per-trial log-odds correlated .91 with dev-1. Two other wordings changed the answers
  themselves (correlation .18 to .62) and were rejected. To be confirmed on all Tier 1
  models on dev before the freeze. Gate 1 tables use dev-1.

- **The reader for Palmer (2008) and whole-picture mirror flips was stopped after two
  hours without a report.** Reason: no jobs are to be left running on the shared machine.
  Palmer's paper I had already read and digitised myself, so E3 is unaffected; the
  whole-picture mirror-flip literature remains unread.
- **Gate 1 checks ran on SmolVLM2-500M and Qwen3.5-0.8B** (15,096 dev trials each, about
  an hour each). Reason: the two smallest candidates, to exercise the pipeline cheaply.

## Gate 1 outcome (2026-11-15)

The owner replied "Approve as recommended" to the Gate 1 package. What that settles:

- **E4 and E5: option A.** E4 runs as a weight question with a direction-only anchor (plus
  an unanchored preference question); E5 runs as an unanchored control; the headline
  rests on E1 to E3.
- **Visibility rule:** the same/different question stays the gate; a reliably non-zero
  preference is reported beside it as a second indicator.
- **Whole-picture mirror flips:** left out; E3's in-place flip is the mirror-flip test.
- **E2 objects: abstract shapes stay.** I gave no recommendation on this one, so the
  approval does not decide it; I am keeping what is built (my call) and it can still be
  switched to schematic icons before the freeze.
- **Unchecked numbers** (Locher 2005, McManus 1993) stay marked as reader-reported; no
  PDFs were supplied.
- **Git identity:** not answered. Commits use a repo-local placeholder
  (`aesthetics-experiment (local) <local@invalid>`) so that work is versioned and the
  freeze can record a commit hash. Reason: no personal data goes into the repo, nothing
  is pushed, and the author can be rewritten later with
  `git config --local user.name/user.email` and an amend or filter.

## 2026-11-15 (session 2: toward Gate 2)

- **Tier 1 candidates: eight models from six families**, all Apache-2.0, ungated, loaded
  with stock transformers classes and pinned by commit: SmolVLM2-500M and -2.2B, Qwen3.5
  0.8B and 4B, MiniCPM-V 4.7 1B, InternVL3.5 2B, North Micro Vision 2.5B, Gemma 4 E2B.
  Reason: spread across labs and across sizes from 0.5B to about 5B, which is what fits
  16 GB without quantisation. SmolVLM2-2.2B was added because the 500M model failed the
  visibility check at Gate 1. All eight load and score on transformers 5.23.0.
- **Readout changed to an assistant-turn prefix (prompt `dev-3`).** The reply is started
  with "Answer:" and the next token is read. Reason: with the first-token readout, Gemma 4
  E2B was off the two letters on 80% of two-image preference trials and InternVL3.5 on
  100% of side-by-side ones; they open with a sentence ("Based on...", "To determine...")
  and then choose. That is a preamble, not a refusal, and the brief's one-fifth rule would
  have discarded them. With the prefix, off-menu is at most 2% on every model and layout
  probed. `dev-2` (the same word at the end of the user turn) fixed Qwen only and is
  dropped. Side effect seen on dev: the prefix also shrinks Qwen3.5-0.8B's second-image
  bias (log-odds -1.5 to -0.3 in the two-image layout).
- **Refusals are counted by a separate free-text probe** (`scripts/refusal_probe.py`):
  60 preference trials per model answered without the prefix, replies classified, and the
  unaided choice compared with the forced readout. Reason: a forced readout cannot refuse,
  and the brief requires refusals to be counted. This adapts the brief's refusal rule for
  local models and is flagged for the owner at Gate 2.
- **Owner approved the adapted refusal rule (2026-11-15, "option A").** Offered the choice
  between (A) the "Answer:" prefix readout with refusals counted from free-text replies,
  and (B) the brief's rule as literally written (first-token readout, drop a model that
  is off the two letters on more than a fifth of trials), the owner chose A. `PLAN.md`
  already states the rule in that form.
- **Pilot = about 40 pairs per experiment, both layouts, prompt `dev-3`**, taken as whole
  families or units (`src/aesx/subsets.py`); E3's pilot is the flip and centre pairs.
  Reason: the brief's pilot size, kept computable for statistics that need a complete
  cluster. 7,160 trials per model.
- **Pilot runs two models at a time** with GPU memory reserved per job
  (`scripts/run_batch.py`). Reason: halves the wall time; small models leave most of the
  GPU idle. The script exits when the last job ends.
- **Gate 2 outcome (2026-11-16): the owner replied "Approve as recommended".** Settled:
  - **Primary layout: two separate images**, plus a side-by-side arm for E1, E4 and E5.
    This departs from the layout rule I wrote in `PLAN.md`, which picked side by side on
    a negligible difference in median position bias (0.42 against 0.46 log-odds); side by
    side, no model could see E2's manipulation and only two of eight could see E3's.
  - **Seven models**: SmolVLM2-500M dropped (it could not see the manipulation in any
    experiment with two images).
  - **E2 keeps the abstract shapes.**
  - **Freeze and run the test split once.**
  - **Tier 2 stays conditional**: Claude Haiku 5.5 and Sonnet 5.5 (about $12.50) only after
    the owner confirms the API credit exists and sets `ANTHROPIC_API_KEY`. Not confirmed
    yet; nothing has been spent and no key has been looked for.
- **Freeze written at commit `41b9cbe`** (`FROZEN.json`, by `scripts/freeze.py`); test
  stimuli generated once afterwards: 1,307 manipulation and 150 identical pairs, all
  hashes verified, no image shared with dev. Test-split commands refuse to run if any file
  in `aesx.freeze.FROZEN_PATHS` differs from that commit. Reason: makes "no tuning on
  test" checkable rather than a promise.
- **Main run started 2026-11-16 16:57** (`scripts/run_batch.py --split test`), with
  `HF_HUB_OFFLINE=1` so the pinned weights load from the local cache and nothing is
  fetched mid-run. 34,432 trials per model (23,012 two-image, 11,420 side-by-side arm).
- **Report figures** (`scripts/report_figures.py`): one forest plot per experiment, each
  model's estimate and 95% interval beside the human band; hollow markers where the model
  fails the visibility rule; plus one dose-response figure. Colours are slots 1-3 of the
  dataviz skill's pre-validated reference palette, with marker shape as a second channel.
  Node is not installed, so the palette validator could not be re-run here.
- **Example page** (`scripts/example_page.py`): six test pairs per experiment with what
  people chose and what each model chose; self-contained HTML with light and dark themes.
- **Commit attribution changed** from Claude Fable 5.2 to Claude Opus 5.5 from this point:
  the owner switched the session's model.
- **Main-run size corrected: about 23,000 trials per model in one layout**, not the 17,700
  written in `reports/gate1.md`. Reason: I had counted one same/different question per
  presentation; there are two (both polarities).

## 2026-11-17

- **Main run rescheduled to one model at a time for the last three models.** At 12:08 four
  models were complete (34,432 trials and the refusal probe each). InternVL3.5 (19,850 done)
  and North Micro (26,050 done) were sharing the GPU and had filled it: 9,470 + 6,548 MiB of
  16,376, with both slowed to 7-28 times their pilot speed since about 03:00 (InternVL about
  17 s a trial, against 0.6 in the pilot). I stopped both and restarted them, and SmolVLM2-2.2B,
  with `run_batch.py --parallel 1`. Reason: the reservations used torch's allocated peak, which
  understates the real footprint by up to 2.2 GB. Results are unaffected: finished trials are
  kept and skipped, both result files ended on a complete line, and each trial is scored
  independently. `run_batch.py` is not a frozen path.
- **NVIDIA driver is now 610.74** (581.95 on 2026-11-14). I did not change it; on this shared
  machine it was updated by someone or by Windows Update. Recorded because a driver update can
  change floating-point results; every trial records its model commit, but not the driver.
- **Owner approved the wording check (2026-11-17, "Wording check").** Design written into
  `PLAN.md` before any of it ran: four wordings of the preference question, the dev pairs of
  E1 to E3, two images, both framings, the seven frozen models; 9,664 trials per model.
  It runs after the main run, not beside it. Reason: sharing the GPU is what stalled the
  main run.
- **Wording check built in a new file (`scripts/wording_check.py`)** that imports the frozen
  trial builder and swaps only the question sentence. Reason: no frozen file changes, so the
  main run's freeze check still passes and the swap is visible in one place. Tested on 48
  real trials and on pilot data copied under all four wordings (spread 0 and pair agreement
  1.00, as they must be). The 48-trial test repeated six pilot trials exactly (difference
  0.0000 log-odds), the first sign that the driver update did not move scores.
- **Prediction scoring written and committed before any test result was opened**
  (`scripts/predictions.py`). Reason: P1 to P6 are stated in `PLAN.md`, but P4 and P6 have
  no numeric criterion and P5 does not name "the smallest models". Fixing those now, blind
  to the results, keeps the verdicts from being chosen after the fact. The criteria choices:
  - P4 parts: paired differences (top minus bottom E1 bin; E3 25% minus 8%; E4 small and
    medium minus large), each supported only if its interval is above zero.
  - P5: the two smallest frozen models.
  - P6: supported only if the interval lies wholly below -.46.
  - P1: compares point estimates, as `PLAN.md` says, over only the experiments the model can
    see.
  Checked on the pilot data, then the pilot outputs were deleted.
- **`gate1_checks.py` read dev manifests for every run tag**; for `--tag test` it would have
  matched no pairs. Fixed: the test tag now uses the test manifests. Found while writing
  the prediction scoring; the pilot tables it writes are unchanged.
- **Main run complete, 2026-11-17 18:40.** Every one of the seven models has 34,432 unique
  trials at prompt `v1`, its pinned commit loaded, and `frozen_commit` 41b9cbe. Refusal
  probes: no model refuses (largest 8.3%, Gemma 4). The wording check started at once,
  from the queue.
- **Bug found in `predictions.py` after the test results were opened.** E2's 90 px pairs
  and E3's flips share a condition label with identical control pairs, and the
  condition-filtered subsets in P1, P3 and P4 (E3) took the identical pairs with them. In
  P4 (E3), with no manipulation, the identical pairs sat in the smallest-eccentricity cell,
  where a pure position bias read as P(inward) = 1.00.
  - Fixed to use changed pairs only, which is what the written criteria say.
  - Comparing all 61 verdict rows before and after the fix, 3 changed: P4 (E3) for InternVL,
    Qwen3.5-4B and Gemma, from "reversed" to "not supported".
  - Reason for fixing after the fact: the criteria text was committed blind. The code did
    not do what that text says, and leaving a known artefact in would be worse than a
    disclosed fix.
- **P1 is reported as committed, plus a post-hoc reading.** The committed P1 averages the
  signed position bias over E1 to E4, so opposite-signed biases cancel. InternVL's are
  -1.6, +0.3, +2.1 and -0.2, which average +0.09. A per-experiment comparison ("P1b") is
  added beside it, labelled post hoc; the committed verdict stands as the P1 result.
- **Wording check complete, 2026-11-18 00:50** (370 minutes, one model at a time, no
  failures).
  - Each of the seven models has 9,664 trials.
  - The 1,056 pilot trials it repeated per model are bit-identical, so the driver update
    moved no score.
  - Applying the rule in `PLAN.md`: E2 is wording-dependent for MiniCPM-V, InternVL and
    Qwen3.5-4B, and consistent for North Micro. E1 is consistent for Qwen3.5-0.8B. No cell
    reversed.
  - Written into `reports/main.md`.
- **Figures: label boxes made opaque** (they were 90% opaque, and the dashed human line
  showed through the E2 label). `report_figures.py`'s docstring named a `--split` option it
  does not have; corrected.
- **Gate 3 approved by the owner, 2026-11-18.** `reports/main.md` is marked approved and is
  otherwise unchanged. Still open: Tier 2 waits on the owner confirming API credit, and
  nothing has been spent. The repo has no remote and nothing has been pushed.
- **NVIDIA addendum chosen by the owner, 2026-11-18** ("NVIDIA free API"), after a survey of
  free tiers. Reasons:
  - Gemini's free tier allows about 500 requests a day and is losing log-probabilities.
  - OpenRouter allows 50 a day without a purchase.
  - GitHub Models has been retired.
  - NVIDIA's free endpoints allow about 40 a minute with no card.
- **Models: Gemma 4 31B and Mistral Large 4, with Nemotron 3.5 Super VL in reserve.**
  - Gemma 4 31B changes size within a family the main run already has.
  - Mistral Large 4 is the largest free endpoint that takes several images.
  - Nemotron is early access and more likely to be withdrawn.
  - The 122B Qwen3.5 would have matched two local models but is not a free endpoint.
- **Readout: sampled replies, three passes at temperature 1.** Neither endpoint documents
  log-probabilities, and `PLAN.md` already fixed samples for API models. Passes, rather than
  three requests in a row, mean an unfinished run still covers every pair once.
- **Client uses the standard library only** (`urllib`). A new dependency would change the
  frozen `uv.lock` and lock out every test command.
- **NVIDIA API Trial Terms read before building.** No clause restricts publishing results.
  Sections 1.2/1.4 (evaluation only), 3.3 (inputs may be used to improve products), 4.2 (do
  not distribute generated content) and 8 (models may change or vanish) are noted in
  `PLAN.md`. The PDF was read through a pypdf environment in the session's scratch folder,
  outside the project.
- **Offline checks passed** against a local mock server, stopped afterwards: 20 reply-parsing
  cases, 429 and 500 retries, resume without duplicates, and the key absent from the
  output. No request has gone to NVIDIA.
- **The key is now asked for at a hidden prompt when `NVIDIA_API_KEY` is not set**, and the
  probe takes both models in one command. Reasons:
  - The owner's terminal blocks PowerShell scripts, so `scripts\env.ps1` cannot run there.
    Commands use `.venv\Scripts\python.exe` directly.
  - A PowerShell line for setting the key was easy to get wrong. On the first try the key
    went into the command line, and so onto the screen and into shell history. The owner was
    asked to revoke it. It never reached a project file, and no request was sent with it.
  - The prompt appears only in a real console. Without one, the script exits rather than
    hanging.
- **Dev probe done; Nemotron replaces Mistral Large 4.** Mistral's endpoint refuses to
  switch reasoning off and returns no answer in 16 tokens. Allowing reasoning would make it
  the only model that thinks before answering. Gemma 4 31B and Nemotron answered all 22 dev
  questions each with a bare letter or Yes/No. Details in `PLAN.md`. Two failed attempts
  before this came from the key paste (once empty, once three copies), not from the models.
  The probe now checks the paste and stops at once if the key is refused.
- **NVIDIA test run started, 2026-11-18 22:26 UTC.** Pass 1 began with Gemma, at the intended
  35 requests a minute. Only request counts have been looked at.
- **Readout mathematics, `reports/readout_math.md` (exploratory, post hoc; owner asked for a
  mathematical analysis).** It uses only the local test runs.
  - One formula, Φ(μ/√(τ² + s²)), fits the three readouts, which differ only in the noise
    `s` each adds.
  - P2's three "supported" verdicts measure consistency across pairs. As choice proportions,
    the form of the human data, those models are .514 to .520, inside the human band.
  - `reports/main.md` is unchanged; whether to add a note there is the owner's call.
- **NVIDIA plan amended before any result was read.** The sampled sign statistic cannot be
  compared with the local one: it would sit near .5 for the same model. `P_cells`, the
  proportion of replies choosing the reference, was added for comparisons. The PLAN text's
  claim that log-probability ties never occur was corrected: they occur rarely, at bfloat16
  precision.
- **Literature review delivered:** `reports/VLM aesthetic preference measurement methods.md`,
  with notes in `research_notes/`. It corroborates the readout curve and adds ten prioritised
  recommendations.
- **Seed fix for the NVIDIA run.** The review spotted from the code that one seed per pass
  could couple all replies in a pass, if the server seeds per request. Each request now gets
  its own SHA-256-derived seed. Plan amended, guard added, re-frozen. The partial old-scheme
  run is set aside unopened, at the cost of about an hour of requests, cheaper than finding out
  after three days. Offline checks: 40 requests got 40 seeds; a folder from the old scheme is
  refused before any request.
- **The old run had gone much further than the hour assumed.** When the owner approved the
  restart, the old-scheme run had finished Gemma's pass 1 (23,012 replies, 12 hours). It had
  also logged 2,782 Nemotron replies before NVIDIA throttled the account. Nemotron dropped to
  about 3.7 a minute after its first hour, with over an hour of rate-limit waiting each hour,
  and the run stopped itself at 19:13 UTC. Setting aside 20 hours of replies was not what the
  owner had approved, so the owner was asked again, and chose to run a seed check first.
- **Seed check on dev (`scripts/seed_check.py`, 2026-11-19, `runs/nvidia-seedcheck/`).**
  - Nemotron honours request seeds beyond doubt. Same-seed repeats never varied (0 of 8),
    different seeds varied on 6 of 8, and two questions reversed completely (AAA against BBB).
  - Gemma shows the same pattern (0 of 8 against 1 of 8), but only one question was
    informative. A follow-up on E3 questions, where Gemma is less certain, was started to
    settle it before 23,012 replies are kept or set aside.
  - The account as a whole is now throttled: Gemma about 10 a minute, against 33 the night
    before.
- **Gemma follow-up confirms it: 0 of 8 against 1 of 8 again (BBBB with a fixed seed, BBAA
  with different seeds).** Over both rounds, the chance of this if seeds were ignored is about
  1 in 25. Together with Nemotron's decisive result, the old run is treated as coupled, as
  the owner approved for that outcome. It was set aside unopened in
  `runs/nvidia-test-seedcoupled/`.
- **The runner alternates models in chunks of 230 presentations.** Reason: at the throttled
  rate the run may be stopped for time, and alternating keeps both models on the same random
  pairs. Offline: 9 switches over 460 requests as expected, distinct seeds, a clean resume.
  `PLAN.md` third amendment; re-frozen.
- **A runner bug cost 60 hours, found 2026-11-24.** The v2 run stopped on 2026-11-21 at 14:14
  UTC, 35% into pass 1. One timed-out request was skipped, and any skip ended the run. Nobody
  was watching, so nothing ran until the owner asked whether the project was stuck.
- **Fixed.** Skips are retried by later sweeps, and rate limits or outages pause for 15
  minutes instead of exiting. The run is one pass with a stop time fixed in advance
  (2026-11-28 00:00 UTC).
  - Reason for one pass: at 3 to 4 requests a minute per model, a second pass cannot finish.
  - Reason for the stop time: when the run stops must not depend on the data.
  - Offline: skipped requests filled by the next sweep (60/60); a 200-request outage ridden
    out; a passed deadline sends nothing; a fatal 400 exits.
  - `PLAN.md` fourth amendment; re-frozen.
- **Public copy prepared, 2026-11-24 (owner: "Yes, prepare it"); not pushed.**
  - `public_release/`, ignored by this repo, is a git-filter-repo copy of the full history:
    same commits and dates, every `runs/nvidia-*` path removed, and the Windows user name
    replaced by `USER`.
  - Reasons: NVIDIA's trial terms (4.2) forbid redistributing generated replies, and the
    user name is personal. Keeping the history preserves the evidence that the plan came
    before the results.
  - Licences added here too: MIT for code, CC BY 4.0 for documents and data.
  - Checked over all 37 commits: no NVIDIA reply files, no user name, no key-like strings,
    no email addresses, one placeholder identity.
  - The only other match for the name pattern is a SHA-256 hash in the E2 manifest that
    contains "ab119b".
  - The push is the owner's to make.
- **Published, 2026-11-24.** The owner created a public GitHub repository and pushed
  `public_release/` (38 commits, 21 MB). Later updates rebuild the copy the same way and push
  normally; the filter is deterministic, so existing commits keep their hashes. The NVIDIA
  run was stopped by a stray Ctrl+C during the push and restarted from 8,050 of 23,012.
- **NVIDIA retired Gemma 4 31B on 2026-11-24 at 09:00 UTC (HTTP 410), found 2026-11-25.**
  - The restarted run ended on that error. Gemma stops at 8,079 replies (35.1%) and is
    reported as incomplete, as pre-registered.
  - Nemotron is still offered and continues alone to the fixed stop time. Without Gemma's
    slow blocks between its own, it should get much further.
  - `PLAN.md` fifth amendment, written before any result was opened. It fixes the analysis:
    each model on all its complete pairs, cross-model comparisons on shared pairs.
  - `FROZEN_API.json` now lists Nemotron alone and records the withdrawal. No code changed.
- **An app restart killed the Nemotron run on 2026-11-25 at 19:41 UTC** (8,376 replies). Runs
  in the app's terminal panel die with the app. The owner restarted it in a Windows PowerShell
  window outside the app on 2026-11-26 at 00:40 UTC.
- **Addendum analysis script written before any test reply was read: `scripts/api_report.py`.**
  - It reuses `predictions.py`'s functions and criteria through an adapter that turns
    sampled replies into the same per-pair tables.
  - It adds P_cells, complete pairs, the NVIDIA cross-model comparison on shared pairs, and
    Gemma 31B against the local Gemma E2B, paired.
  - The self-test on simulated replies caught a crash: P6 needs complete E1 families. P6 now
    uses complete families only and is "not estimable" without them.
  - Three seeds of full simulated passes show P_cells is unbiased.
  - `--final` refuses to read the test replies while the run looks active.
- **Finishing the addendum is automated (owner, 2026-11-26: "can you perform 2 and 3
  automatically?").**
  - `scripts/public_release.py` rebuilds the filtered public copy and runs the privacy
    checks. It merges any commits made on GitHub and pushes only as a fast-forward, with no
    force and no sign-in prompt.
  - The owner had added `.zenodo.json` on GitHub on 2026-11-24, so a plain push would have
    been refused. The file is now also in this repo, byte-identical.
  - A dry run on 2026-11-26 passed every check, merged that commit cleanly, and confirmed
    stored credentials. Nothing was sent.
  - One-time scheduled task "aesthetics-nvidia-addendum-finish", 2026-11-28 00:30 UTC, saved
    in Auto mode: check the run has stopped, run `api_report.py --final`, write
    `reports/nvidia_addendum_summary.md` from the report's numbers only, commit, then
    `public_release.py --push`.
  - The filter settings and the filter tool moved from the session scratchpad into
    `.tools/` (git-ignored), so they survive.

## 2026-11-28 (scheduled finishing task, NVIDIA addendum)

- **The run had stopped.** At 00:30 UTC no process with `run_api.py` in its command line was
  running. The last line of Nemotron's `results.jsonl` was stamped 2026-11-27 22:40 UTC.
  Only the process list and that timestamp were checked before the report ran.
- **Nemotron finished pass 1 before the stop time:** 23,012 replies, 1,457 of 1,457 pairs.
  Gemma 4 31B stays at 8,079 replies (511 pairs, 35.1%).
- **`scripts/api_report.py --final` ran without error** and wrote
  `reports/nvidia_addendum.md` and `reports/nvidia_addendum.csv`. Both models passed the
  refusal rule (off-menu 0.0% and 1.9%) and the visibility rule in all five experiments.
- **`reports/nvidia_addendum_summary.md` written:** one page, findings first. Every number is
  copied from the report, with no new statistics. The prediction verdicts are labelled as
  being on the sign statistic.
  - I wrote "same family, different size" and gave no size ratio, because the reports give
    no parameter counts.
- **README:** the status line said the addendum "is running" with "four amendments". I
  corrected it to "finished" and "five", since it was stale. I added the pointer line to the
  summary.
- **Committed `runs/nvidia-test/`** (4 files, about 29 MB) with the reports. It stays local;
  the public copy removes `runs/nvidia-*`.
