# Plan and predictions

**Status: draft, written before any test stimulus exists.** It becomes binding when it is
frozen: a `FROZEN.json` file is written at the project root recording the git commit and
the prompt version, and only then will `scripts/make_stimuli.py --split test` and
`scripts/run_model.py --split test` run. Nothing below may change after the freeze.

## Predictions (from the brief, with the test that decides each)

| # | Prediction | Decided by |
|---|---|---|
| P1 | For small models, position bias is larger than any aesthetic effect. | For each model under 3B parameters: the absolute position bias on identical pairs (log-odds) against the largest absolute mean preference over the anchored conditions of E1 to E4. Supported for a model if the bias is larger. |
| P2 | In the contested two-object design, models show a stronger balance preference than people did. | E2, 90 px pairs: supported for a model if the lower end of its interval for P(balanced chosen) is above .561, the highest of the eight human bars. "Matches people" if the whole interval lies within .43 to .57. |
| P3 | Mirror-flip preferences are near zero under the "you" framing and larger under the "most people" framing. | E3 flip pairs: the distance of P(inward-facing chosen) from .50 under each framing. Supported if it is larger under "most people", with a paired bootstrap interval over icons that excludes zero. |
| P4 | Where people show a dose response, model effects also grow with the size of the manipulation. | E1: P(more balanced chosen) rises across the four score-difference bins. E3: P(inward) is higher 25% from centre than 8% from centre (people: .82 against .70). E4 weight: the red-over-yellow effect is larger at the two smaller sizes than at the largest (people: present, then absent). |

Predictions I add, since the controls allow them:

| # | Prediction | Decided by |
|---|---|---|
| P5 | The smallest models fail the visibility check on the subtlest manipulations (E2's 45 px shift, E1 pairs under 12 points apart). | Visibility AUC by dose. |
| P6 | Models reproduce E1's aggregate correlation more strongly than individual people do. | Model r against the individual-rater range (mean -.28 to -.46, SD about .35). |

## What is reported for each experiment

The primary statistic for each experiment is fixed in `docs/experiments.md` under "Model
counterpart" and computed by one function in `src/aesx/effects.py`. For every model and
experiment the report shows:

1. the model's statistic with its bootstrap interval over stimuli;
2. the human figure with its interval, or the nearest thing the paper allows, labelled
   for what it is (a confidence interval, a range over conditions, or direction only);
3. the model's position bias from identical pairs, beside the effect;
4. the dose-response curve where the manipulation has a size.

No significance test is run between a model and people. The two intervals describe
different things (variation over stimuli for one model; variation over people, where it
is known at all), so overlap is described, not tested.

## Rules fixed in advance

- **Choice and preference.** A pair's choice is the sign of its mean log-odds over the
  four counterbalanced presentations. Raw per-trial choices are also tabulated, because
  with a strong position bias they sit at 50/50 however clear the preference.
- **Primary layout.** One layout for all models, chosen on dev: the one with the smaller
  median absolute position bias across the Tier 1 models, among layouts in which at least
  half the models are usable. A model is usable in a layout if it stays on the two
  permitted answers (off-menu on at most a fifth of preference trials) and passes the
  visibility rule in at least three of the five experiments. The test split is run in
  that layout only.
  **Departure, approved at Gate 2 (2026-11-16):** the rule picked side by side, on a
  negligible difference (median absolute position bias 0.42 against 0.46 log-odds). But
  side by side no model could see E2's manipulation and only two of eight could see E3's,
  so the contested null could not have been tested. The primary layout is therefore two
  separate images, and side by side is run as a second arm for E1, E4 and E5, where most
  models see the manipulation in both layouts. The pilot also showed E1's direction
  changing with the layout; the arm measures that.
- **Visibility rule.** A model's preference in an experiment is reported only if its
  same/different AUC on that experiment's test pairs is at least .75 and the lower end of
  its interval is above .50. Otherwise the model is listed under "cannot see the
  manipulation" for that experiment.
- **Readout for local models.** The reply is started with "Answer:" and the next-token
  log-probabilities of the two permitted answers are read (summed over spellings with and
  without a leading space). This reads the choice where the model commits to one. Reading
  the very first reply token instead was tried on dev and dropped: several models open
  with a sentence before choosing, which that readout mistakes for a refusal.
- **Refusal rule.** A forced readout cannot refuse, so refusals are counted separately:
  on a random sample of preference trials each model answers freely (no reply prefix, up
  to 160 tokens) and each reply is classed as *direct* (opens with a letter), *commits*
  (names a letter as its choice later), *refuses* (no choice, and wording that declines)
  or *unclear*. A model classed as refusing on more than a fifth of the sample is
  reported as refusing, not scored. The same sample gives the agreement between the
  forced readout and the model's own unaided choice, which is reported for every model.
  Trials where the two permitted answers hold under half the probability *after* the
  prefix are also counted ("off-menu") and reported.
  For API models: more than a fifth of replies that are not one of the two labels.
- **Framings.** Both "you" and "most people" are always reported; "you" is primary.
- **Seeds.** Dev and test use disjoint random streams and, in E3, disjoint icons.
- **One run.** The test split is run once per model. A crashed run is resumed, never
  restarted with changes.

## The main run, as frozen

- **Models (seven):** Qwen3.5-0.8B, MiniCPM-V 4.7 1B, SmolVLM2-2.2B, InternVL3.5-2B, North
  Micro Vision, Qwen3.5-4B, Gemma 4 E2B; commits pinned in `src/aesx/models/registry.py`.
- **Stimuli:** the test split, generated once after the freeze: 1,307 manipulation pairs
  and 150 identical pairs (E1 200, E2 300, E3 390, E4 216, E5 201).
- **Layouts:** two images for every experiment; side by side additionally for E1, E4, E5.
- **Prompt `v1`:** identical wording and readout to the pilot's `dev-3`.
- **Refusal probe:** 60 preference trials per model drawn from the test trials.
- **Tier 2** (Claude Haiku 5.5 on the full design, Claude Sonnet 5.5 on the anchored
  experiments) only if the owner confirms the API credit; it would use the same frozen
  stimuli and wording, with repeated samples in place of log-probabilities.

`FROZEN.json` records the commit. Every test-split command checks that no file that
determines a stimulus, a trial or a score (`src/aesx/freeze.py`, `FROZEN_PATHS`) differs
from that commit, and refuses to run if one does.

## Freeze checklist

- [x] Owner has approved the experiment set (Gate 1, 2026-11-15) and the model list
  (Gate 2, 2026-11-16).
- [x] Prompt wording fixed; `PROMPT_VERSION` bumped from `dev-3` to `v1`.
- [x] Primary layout chosen from dev results and written here (two images; see above).
- [x] All code committed; `FROZEN.json` written with the commit hash.
