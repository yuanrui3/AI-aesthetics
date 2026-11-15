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

## Freeze checklist

- [ ] Owner has approved the experiment set (Gate 1) and the model list (Gate 2).
- [ ] Prompt wording fixed; `PROMPT_VERSION` bumped from `dev-N` to `v1`.
- [ ] Primary layout chosen from dev results and written here.
- [ ] All code committed; `FROZEN.json` written with the commit hash.
