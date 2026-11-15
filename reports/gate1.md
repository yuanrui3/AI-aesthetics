# Gate 1

15 November 2026. Everything here uses **dev stimuli only**. No test stimulus exists yet.

## What to look at

| Item | Where |
|---|---|
| Source experiments, human effect sizes, model counterparts | `docs/experiments.md` |
| How this differs from existing benchmarks | `docs/related.md` |
| Contact sheets, one per experiment | `stimuli/<experiment>/dev/contact_<experiment>.png` |
| Position bias and visibility on two local models | `reports/gate1_checks.md` |
| Model effects beside human effects (dev preview) | `reports/effects_dev.csv` |
| Predictions and rules fixed before the main run (draft) | `PLAN.md` |
| Every decision and its reason | `LOG.md` |

## The experiments

| | Source | Manipulation | Human anchor | Meets the brief's four criteria? |
|---|---|---|---|---|
| E1 | Wilson & Chatterjee 2005 | Shift of visual weight, five dose levels | r = -.85 to -.88 over images; individuals average about -.44 | Yes (ratings converted to forced choice) |
| E2 | Leyssen et al. 2012, Exp 5 | Object pair shifted 90 px off-centre | P(balanced) about .53, not above chance, N = 20 | Yes, except the objects: photographs replaced by abstract shapes |
| E3 | Palmer, Gardner & Wickens 2008 | In-place mirror flip; position shift | Inward-facing chosen 74%, N = 17 | Yes, except the objects: renderings replaced by schematic icons |
| E4 | Locher et al. 2005 | Colour swap in a grid | Direction only: red rated heavier than yellow | **No.** Real paintings adapted; no preference task |
| E5 | McManus et al. 1993 | Grid lines moved | None for generated grids | **No.** Effect is defined against the artist's original |

## Checks on two local models

Models: SmolVLM2-500M and Qwen3.5-0.8B, both Apache-2.0, pinned by commit. 15,096 trials
each: every dev pair, both layouts, both framings, both orders, both letter assignments,
plus the same/different question. Prompt wording `dev-1`.

**Position bias (identical pairs).**
- Two-image layout: both models favour the *second* image. Qwen names the first image on
  0 to 16% of identical-pair trials (log-odds -0.7 to -1.4); SmolVLM on 0 to 20% (-0.4 to
  -0.6).
- Side-by-side layout: Qwen's bias is larger still (log-odds -1.7 to -3.1). SmolVLM shows
  little position bias (-0.03 to +0.39) but answers by letter instead: it leans to "A"
  whichever image carries it (log-odds +0.4 to +0.7).
- The bias dwarfs the preference signal in the two-image layout. The spread of
  bias-cancelled preferences across pairs is 0.04 to 0.06 log-odds for SmolVLM (bias
  eight to fourteen times larger) and 0.16 to 0.29 for Qwen (two to eight times larger).
  Raw choices are therefore almost pure bias; only the counterbalanced per-pair mean
  carries information.

**Visibility (same/different AUC; 0.5 = cannot tell).**
- Qwen, two images: 0.95 to 1.00 in all five experiments. Side by side: 0.55 to 0.97,
  failing E2 and E3.
- SmolVLM: 0.38 to 0.69 everywhere except E1 side by side (0.91). By the brief's rule its
  preferences would be listed as "cannot see the manipulation".
- **A caveat on the rule itself.** SmolVLM fails the same/different question on E1 in the
  two-image layout (AUC 0.43) yet its bias-cancelled preferences track the balance score
  (r = -.58, interval -.73 to -.43). It evidently registers the difference without being
  able to *say* the images differ. The same/different question tests the ability to
  report a difference, which is stricter than seeing one.

**Staying on the permitted answers.**
- Two-image layout: both models put nearly all probability on the two letters.
- Side by side: Qwen starts a sentence instead of answering on 58% of preference trials
  (up to 98% in E1), which the brief's one-fifth rule would call refusing. Appending
  "Answer:" to the instruction cut this to 11% on an 80-trial dev sample without changing
  the answers (see `LOG.md`); two stronger rewordings changed the answers and were
  rejected.

**Layout.** On this evidence the two-image layout is the candidate primary: less position
bias for Qwen, better visibility, and no off-menu replies. To be confirmed across all
Tier 1 models before the freeze.

## Dev preview of effects (not results)

Two-image layout, "you" framing, bias-cancelled choices. Small samples and two very small
models; shown only to demonstrate that the pipeline produces the paper's statistic.

| | Human | Qwen3.5-0.8B | SmolVLM2-500M |
|---|---|---|---|
| E1 r(balance score, preference), 40 images | -.87 aggregate; -.44 individuals | -.50 [-.74, -.19] | -.58 [-.73, -.43] |
| E1 P(more balanced chosen), 80 pairs | not reported | .73 [.61, .83] | .60 [.55, .66] |
| E2 P(balanced chosen), 32 pairs | .53 (range .48 to .56) | .63 [.47, .78] | .53 [.41, .66] |
| E3 P(inward-facing chosen), 24 pairs | .74 | .46 [.25, .67] | .50 [.33, .71] |
| E4 P(red named heavier than yellow), 16 pairs | direction: above .50 | .75 [.50, .94] | .75 [.50, .94] |
| E5 P(less altered chosen), 72 pairs | no anchor | .58 [.47, .69] | .46 [.33, .58] |

## Decisions needed

1. **E4 and E5.** Options A to D at the end of `docs/experiments.md`. Recommended: A (keep
   E4 as a weight question with a direction-only anchor; keep E5 as an unanchored
   control; rest the headline on E1 to E3).
2. **E2 objects.** Abstract shapes (built) or schematic icons in related and unrelated
   pairs (restores "meaningful objects" and the source's positive control)?
3. **Visibility rule.** Keep the same/different question as the only gate, or also accept
   a reliably non-zero preference as evidence that a model sees the manipulation?
   Recommended: keep the brief's rule as the gate and report the second indicator beside it.
4. **Unchecked numbers.** The Locher (2005) and McManus (1993) figures come from a
   reader's report of page scans; I confirmed only Locher's abstract. If you can supply
   the two PDFs I will check them. They anchor nothing in E1 to E3.
5. **Whole-picture mirror flips.** E3 tests the object flipped in place, which is what
   Palmer's inward bias is. Reflecting the whole picture is a different manipulation with
   its own literature (left-to-right directionality, for example Chokron & De Agostini
   2000). The reader assigned to that literature did not finish and was stopped, so none
   of it is verified. Add it as a sixth experiment after a second literature pass, or
   leave mirror flips covered by E3 alone? Recommended: leave it, unless whole-picture
   flips matter to you.
6. **Git identity.** No git user is configured on this machine, so nothing is committed.

## Next, toward Gate 2

1. Confirm the `dev-2` wording on every Tier 1 model on dev; choose the primary layout.
2. Pilot all Tier 1 models on 40 dev pairs per experiment; table of model against human.
3. Estimate for the main run from dev timings: about 17,700 trials per model in one
   layout; 0.25 to 0.45 s per trial for the two small models (1.2 to 2.2 hours each),
   more for the larger ones. A firmer figure comes with the pilot.
   *Correction made after Gate 1: the right count is about 23,000 trials per model (two
   same/different questions per presentation, not one). See `LOG.md`.*
