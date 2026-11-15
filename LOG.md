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
- **Main-run size corrected: about 23,000 trials per model in one layout**, not the 17,700
  written in `reports/gate1.md`. Reason: I had counted one same/different question per
  presentation; there are two (both polarities).
