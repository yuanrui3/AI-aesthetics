# Do vision-language models share people's compositional preferences?

**Status: draft.** The methods and limitations below were written on 2026-11-17, while the
main run was still going and before any test result had been opened. The findings and
figures will be added from the test run at Gate 3.

## Findings

*To be written from the test results.* This section will come first and fit on one page:
- for each experiment, the human effect and each model's effect, in plain words;
- predictions P1 to P6, each marked supported, not supported or not testable
  (`reports/predictions_test.md`);
- what the controls say about how far each number can be trusted (position bias,
  visibility, refusals, wording).

## One figure per experiment

*To be added:* `reports/figures/test/` (E1 balance, E2 two objects, E3 one object, E4
colour, E5 proportion, dose response). Each shows the human figure as a band or line, and
each model's estimate with its 95% interval. A hollow marker means the model cannot see the
manipulation. Example pairs, with what people and each model chose, are in
`reports/examples/index.html`.

---

## Methods

### Design in one paragraph

Five published experiments on picture composition were re-run on seven open-weight
vision-language models as two-alternative forced choices:
- **Stimuli:** each trial shows a code-generated composition and a controlled variant of it,
  and the model is asked which it finds more pleasing.
- **Counterbalancing:** each pair is shown four times: both orders crossed with both
  assignments of the answer letters.
- **Readout:** the model's choice is read from the log-probabilities of the two letters.
- **Score:** each model's effect, with an interval over stimuli, set beside the published
  human effect.

Predictions were written into `PLAN.md` first. The code, prompt and models were then frozen,
and the test stimuli were generated for the first time and run once.

### The five experiments

Full designs, human numbers and their provenance are in `docs/experiments.md`.

| | Source | What changes within a pair | Human anchor | Model statistic |
|---|---|---|---|---|
| E1 | Wilson & Chatterjee (2005), Assessment of Preference for Balance | Placement of seven black elements: five balance levels of the same elements | r(balance score, liking) = -.85 to -.88 over images. Individual raters average -.28 to -.46 (Hübner & Fillinger 2016) | r between balance score and preference scale value; P(more balanced chosen) by score difference |
| E2 | Leyssen et al. (2012), Exp. 5, two objects | The two-object group shifted 90 px off-centre | P(balanced chosen) about .53, not above chance (the contested null) | P(balanced chosen) at 90 px; also 45 and 135 px |
| E3 | Palmer, Gardner & Wickens (2008), one object | In-place mirror flip; shift of position | Inward-facing view chosen about .74; centre preferred | P(inward-facing chosen); centre against quarter line |
| E4 | Locher, Overbeeke & Stappers (2005), colour in grid compositions | Colours swapped between the largest area and a small one | Direction only: red rated heavier than yellow (a weight judgement, not preference) | P(red named heavier), asked as a weight question; preference asked too, no anchor |
| E5 | McManus, Cheema & Stoker (1993), proportions | Grid lines moved by a small or large amount | None for generated grids | P(less-altered chosen): a control |

E1 to E3 carry the human comparison. E4 and E5 are reduced forms approved at Gate 1:
- E4 keeps only the direction of a weight judgement.
- E5 has no human anchor. The source compares altered paintings with the artist's original,
  which the code-only rule excludes.

### Stimuli

Every image is drawn by code from a seed (`src/aesx/experiments/`); none reproduces an
artwork or a real design.
- **Dev and test:** separate random streams. In E3 the icon sets are separate too, so no
  test icon was seen during development.
- **Test split:** 1,307 changed pairs and 150 identical pairs.

| | Changed pairs | Identical pairs |
|---|---|---|
| E1 | 200 | 40 |
| E2 | 300 | 30 |
| E3 | 390 | 39 |
| E4 | 216 | 18 |
| E5 | 201 | 23 |

- **Generation and checks:** `scripts/make_stimuli.py`, which refuses to write the test
  split unless the code matches the freeze. Every image's SHA-256 is in its manifest.
- **E1 balance score:** reproduces the paper's printed value for its Figure 2 image (8.61
  against 8.58).

### Models

Seven Tier 1 models, all Apache-2.0, run locally in bfloat16. Each is pinned to a Hugging
Face commit (`src/aesx/models/registry.py`), and the commit actually loaded is recorded in
each run's `run.json`.

| Model | Parameters | Family |
|---|---|---|
| Qwen3.5-0.8B | 0.9B | Qwen (Alibaba) |
| MiniCPM-V 4.7 1B | 1.6B | MiniCPM-V (OpenBMB) |
| SmolVLM2-2.2B | 2.3B | SmolVLM (Hugging Face) |
| InternVL3.5-2B | 2.3B | InternVL (OpenGVLab) |
| North Micro Vision | 2.5B | North (Cohere) |
| Qwen3.5-4B | 4.7B | Qwen (Alibaba) |
| Gemma 4 E2B | 5.1B | Gemma (Google) |

Software: transformers 5.23.0, PyTorch 2.15.0 with CUDA 13.2, on one 16 GB RTX 4090 Laptop
GPU. Each model's default image preprocessing (resizing, tiling) is left as shipped. No
API model was run (Tier 2 waits on the owner confirming API credit).

### Presentation and prompt (frozen as `v1`)

**Two-image layout (primary).** The user turn is:
- "Image A:", then the first image;
- "Image B:", then the second image;
- the question, then "Answer with one letter only: A or B."

**Side-by-side arm (E1, E4, E5).** One picture holds both images, with a sentence saying
which side carries which letter.

**Questions.**
- "you" framing: "Which of these two images do you find more pleasing to look at?"
- "most people" framing: "Which of these two images would most people find more pleasing to
  look at?"
- E4 also asks: "In which of these two images does the largest coloured rectangle look
  visually heavier?"

**Trials.** Each pair is shown in both orders, crossed with both letter assignments, under
both framings. That gives 34,432 trials per model: 23,012 with two images and 11,420 in the
side-by-side arm.

### Readout

- **Single trials.** The model's reply is started with "Answer:", and the log-probabilities
  of the two permitted letters are read from the next token. Spellings with and without a
  leading space are summed.
- **A pair's preference** is the mean, over its four counterbalanced presentations, of the
  log-odds for the reference image. Position and letter biases cancel in this mean.
- **A pair's choice** is 1 if that mean is positive.
- **What is reported:** only these bias-cancelled pair-level numbers. Single trials are
  dominated by position and letter bias.

### Controls

- **Position bias.** Measured on identical pairs, where there is nothing to prefer: the
  log-odds of naming the first image.
- **Visibility.** On every pair the model is also asked "Are these two images exactly
  identical?" and "Is there any difference between these two images?", so that a yes-bias
  cancels. The area under the ROC curve then separates changed pairs from identical ones.
  - A model's preference in an experiment is reported only if this AUC is at least .75
    and the lower end of its interval is above .50.
  - Otherwise the model is listed as unable to see the manipulation.
- **Refusals.** A forced readout cannot refuse, so refusals are counted separately (the rule
  the owner approved at Gate 2).
  - Each model answers 60 test preference trials freely: no reply prefix, up to 160 tokens.
  - Each reply is classed as direct, commits, refuses or unclear.
  - A model refusing on more than a fifth would be reported as refusing, not scored.
  - The same sample gives how often the forced answer agrees with the model's unaided one.
- **Off-menu.** The share of trials on which the two letters hold under half of the
  next-token probability.
- **Dose response.** E1 by balance-score difference; E2 at 45, 90 and 135 px; E3 by distance
  from the centre; E4 by area.

### Statistics

- **Model intervals:** 95% bootstrap intervals over stimuli, 2,000 resamples. Pairs that
  share images are resampled together: a family in E1, a unit in E2, an icon in E3, a
  layout in E4 and E5.
- **Visibility AUC intervals:** resample pairs.
- **No significance test between a model and people.** The two intervals describe different
  things: variation over stimuli for one model, and variation over people where a paper
  reports it at all. So overlap is described, not tested.
- **Predictions P1 to P6:** scored by `scripts/predictions.py`, whose criteria were
  committed before the test results were opened (commit `a149465`).

### Freeze, run and reproduction

**The freeze.**
- `FROZEN.json` records commit `41b9cbe`, prompt `v1`, the seven models and the layouts.
- Every test-split command refuses to run if any file that decides a stimulus, a trial or a
  score differs from that commit.
- The test stimuli were generated once, after the freeze, and run once.

**The main run.**
- Started 2026-11-16 16:57.
- On 2026-11-17 two models sharing the GPU had filled its memory and slowed sharply. The
  last three models were then resumed one at a time.
- Finished trials were kept, and each trial is scored independently, so no number depends
  on this (`LOG.md`).

**One command per reported number:**

```
uv run python scripts/gate1_checks.py --tag test
uv run python scripts/effects_table.py --split test --tag test --quiet
uv run python scripts/predictions.py --split test --tag test
uv run python scripts/report_figures.py --tag test --split test
uv run python scripts/example_page.py --split test --tag test
uv run python scripts/wording_check.py report
```

### Wording check (exploratory)

Added on 2026-11-17 with the owner's approval and written into `PLAN.md` before it ran.
- **Design:** the seven models answered every dev pair of E1 to E3 under four wordings of
  the question ("more pleasing to look at", "like more", "more beautiful", "prefer"), with
  two images, under both framings.
- **What it can do:** only qualify a main result, never strengthen it. A model's result is
  called wording-dependent where the direction is reversed or mixed across wordings.
- **Repeatability:** the same run repeats the pilot's trials exactly, which shows whether the
  driver update between the pilot and the main run moved any score.

## Departures from the brief, all approved at a gate

1. **Readout.** The reply is started with "Answer:" (Gate 2, "option A"). Reading the very
   first token misjudged models that open with a sentence before choosing. Refusals are
   counted from free replies instead.
2. **E4 and E5 run in reduced forms** (Gate 1).
3. **Primary layout: two images** (Gate 2). This departs from the selection rule in
   `PLAN.md`, which picked side by side on a negligible difference in position bias. Side by
   side, no model could see E2's manipulation.
4. **SmolVLM2-500M dropped** (Gate 2). It could not see the manipulation in any experiment
   with two images.
5. **E2 uses abstract shapes**, not photographs of related and unrelated objects (Gate 2).
6. **Whole-picture mirror flips left out** (Gate 1). E3's in-place flip is the mirror-flip
   test.

## Limitations known before the results

- **Small models only.** Every model is 5B parameters or smaller, because that is what fits
  the GPU. Claims about models that "know the textbook" would need larger ones; no API model
  was run.
- **Different tasks on each side.**
  - E1's human effect is a correlation of ratings over images. The model's is a correlation
    of scale values derived from pairwise choices.
  - E4's human effect is a weight judgement on adaptations of real paintings.
  - E5 has no human effect at all.
  - The comparisons are of direction and rough size, not of identical measurements.
- **One model is one observer.** Most human anchors are aggregates over raters, which are
  stronger and steadier than any one rater. Where a paper gives individual effects (E1), both
  are shown.
- **Human numbers vary in quality.**
  - Some are printed; others are digitised from figures (error about one percentage point).
  - Locher (2005) and McManus (1993) are reader-reported and unchecked, so they are never
    used as anchors.
  - E3 rests on 9 and 17 participants.
- **Substitute stimuli.** E2 and E3 used photographs or renderings of real objects; here they
  are abstract shapes (E2) and schematic icons (E3). An effect people show for real objects
  need not carry over.
- **What the readout measures.** It records which letter the model favours when made to
  commit after "Answer:". In the pilot, the forced answer agreed with the model's unaided
  answer on 60 to 88% of single trials. Only bias-cancelled pair-level numbers are reported,
  but they are still choices under one particular prompt.
- **Layout dependence.** In the pilot, E1's direction reversed between the two layouts. The
  side-by-side arm measures this for E1, E4 and E5, but a preference that depends on the
  presentation is not a stable preference.
- **Wording.** The test split uses one frozen wording. The wording check covers E1 to E3 on
  the smaller dev split only.
- **Position bias.** Some models' position bias is several times any preference.
  Counterbalancing removes it from the mean but not from the noise. P1 tests whether it
  dominates.
- **Preprocessing differs between models.** Each model's own resizing and tiling means the
  models do not see the images at the same resolution.
- **Intervals cover stimuli only.** They do not cover prompts, layouts, the generator's
  design choices or model versions.
- **Environment.** The NVIDIA driver changed from 581.95 to 610.74 between the pilot and the
  main run. This was outside this project's control, and the wording check's repeatability
  test measures its effect.
- **Out of scope.** Nothing here ranks models by taste. A model that matches people more
  closely in one experiment has not been shown to judge pictures better.
