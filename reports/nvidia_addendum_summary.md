# NVIDIA addendum: one-page summary

**Status: exploratory addendum, written 2026-11-28 from `reports/nvidia_addendum.md` and
`.csv`** (`.\.venv\Scripts\python.exe scripts/api_report.py --final`). Every number below is
copied from those two files. No new statistic is computed here. Nothing here changes a number
or verdict in `reports/main.md`. The rules were fixed in `PLAN.md` (the NVIDIA addendum and its
five amendments) before any test reply was read.

Unless stated, figures are P_cells: the share of replies naming the reference image over all
counterbalanced presentations. Brackets are 95% cluster-bootstrap intervals over stimuli.
P_cells has the same form as the published human choice proportions. It is also on the same
scale as the local models' P_cells range given in the addendum, which is not the same as the
sign statistic quoted in `reports/main.md`.

## Findings

1. **Both large models can see every manipulation.** Visibility AUCs are 0.95 to 1.00 in all
   five experiments, with lower ends far above .50. Among the local models, Gemma 4 E2B could
   not see E2's shift (AUC .65); Gemma 4 31B sees it at 0.98 [0.96, 1.00].
2. **Inward bias (E3) is still absent.** People choose the inward-facing view .74 of the time.
   Gemma 4 31B is at 0.496 [0.441, 0.548] and Nemotron at 0.531 [0.493, 0.570]; both intervals
   include .5 and lie far below the human value. Close to the centre (8%), Gemma 4 31B leans
   *outward*: 0.375 [0.281, 0.457], whose whole interval is below .5. Nemotron leans inward
   there, 0.568 [0.521, 0.615], but well short of people's .704.
3. **E2 balance: Gemma 4 31B chooses the balanced picture more often than people do;
   Nemotron does not.** Gemma 4 31B: 0.647 [0.577, 0.714] (n = 46 pairs). Its whole interval
   is above the human bars (.48 to .56) and above the `PLAN.md` "matches people" band (.43 to
   .57). Nemotron: 0.540 [0.507, 0.573], an interval that includes the human value .528. The
   local models' range is 0.496 to 0.521.
4. **The simpler effects are present and, in P_cells, larger than in any local model.**
   - **Centre over quarter line (E3):** Gemma 4 31B 1.000 [1.000, 1.000] (only 11 pairs),
     Nemotron 0.847 [0.792, 0.903]. Local range: 0.499 to 0.739. People prefer the centre
     (direction only).
   - **Red named heavier (E4, small and medium):** Gemma 4 31B 0.767 [0.641, 0.875],
     Nemotron 0.646 [0.594, 0.693]. Local range: 0.498 to 0.625. Nemotron's interval reaches
     into that range. People also judge red heavier (direction only).
5. **E1 and E5 show a modest lean toward the more balanced or less altered grid.**
   - **E1:** Gemma 4 31B 0.587 [0.514, 0.657], Nemotron 0.562 [0.523, 0.600]. Local range:
     0.451 to 0.535. There is no human choice proportion here; the human result is a
     correlation over images.
   - **E5:** Gemma 4 31B 0.558 [0.486, 0.635] (interval includes .5), Nemotron 0.584
     [0.544, 0.624]. Local range: 0.492 to 0.532. There is no human anchor for these
     generated grids.
6. **No pre-registered prediction is supported for both models** (sign statistic; see below).

## What was collected

| Model | Replies | Complete pairs | Share of the design | Off-menu | Refusal rule |
|---|---|---|---|---|---|
| Gemma 4 31B | 8,079 | 511 of 1,457 | 35.1% | 0.0% | scored |
| Nemotron 3.5 Super VL | 23,012 | 1,457 of 1,457 | 100.0% | 1.9% | scored |

- **Gemma 4 31B is incomplete.** NVIDIA withdrew it on 2026-11-24 (HTTP 410, "end of life")
  after 35.1% of the single pass. Its pairs are a random subset of the design, because pairs
  ran in one fixed random order.
- **Nemotron finished the whole pass** before the fixed stop time: its last reply was at
  2026-11-27 22:40 UTC.
- **Position bias** on identical pairs (.5 = none) is small for both models:
  - Gemma 4 31B: 0.510 [0.500, 0.530];
  - Nemotron: 0.554 [0.498, 0.613], an interval that includes .5.

## Gemma 4 31B against the local Gemma 4 E2B (same family, different size)

The comparison is paired by pair, on Gemma 4 31B's complete pairs. Figures are differences
in P_cells (31B minus E2B).

- **Higher in the larger model:**
  - E1: 0.106 [0.034, 0.179];
  - E2: 0.125 [0.062, 0.192];
  - centre over quarter line: 0.453 [0.404, 0.498];
  - E5: 0.082 [0.010, 0.155].
- **Lower in the larger model:** E3 inward at 8%, −0.086 [−0.170, −0.005].
- **Intervals include 0:**
  - E3 off-centre flips: 0.004 [−0.048, 0.058];
  - E3 at 25%: 0.022 [−0.068, 0.131];
  - E4: 0.147 [−0.010, 0.272].

Size within the family strengthens the balance, centre and grid effects. It does not produce
the inward bias.

## Gemma 4 31B against Nemotron, on pairs both completed

Figures are differences in P_cells (Gemma minus Nemotron).

- **Gemma higher:**
  - E2: 0.109 [0.038, 0.176];
  - centre: 0.136 [0.025, 0.250];
  - E4: 0.167 [0.014, 0.312].
- **Gemma lower:** E3 at 8%, −0.250 [−0.383, −0.136].
- **Intervals include 0:**
  - E1: 0.008 [−0.093, 0.094];
  - E3 flips: −0.048 [−0.097, 0.012];
  - E3 at 25%: 0.036 [−0.063, 0.154];
  - E5: −0.013 [−0.111, 0.078].

The shared pairs number 11 to 69 per effect, so these comparisons are imprecise.

## Pre-registered predictions

These verdicts are on the pre-registered **sign statistic**. With one sampled reply per
presentation it sits much closer to .5 than the local models' log-probability version
(`reports/readout_math.md`). So these verdicts are **not comparable with the main report's**.
P1 and P5 concern small models and do not apply.

| Prediction | Gemma 4 31B | Nemotron 3.5 Super VL |
|---|---|---|
| P2: E2 balance stronger than people | supported, 0.685 [0.576, 0.791] | inconclusive, 0.550 [0.487, 0.608] |
| P3: inward bias stronger under "most people" | not supported, 0.040 [−0.025, 0.108] | not supported, −0.038 [−0.083, 0.042] |
| P4, E1: grows with balance difference | not supported (bins not monotonic) | not supported (bins not monotonic) |
| P4, E3: stronger at 25% than 8% | supported, 0.248 [0.105, 0.435] | not supported, −0.083 [−0.271, 0.083] |
| P4, E4: colour effect fades at the largest area | not supported, −0.167 [−0.367, 0.000] | reversed, −0.219 [−0.317, −0.116] |
| P6: E1 correlation stronger than individual people | not estimable (no complete E1 family) | inconclusive, r = −0.322 [−0.533, −0.071] |

Two of these need a caveat.

- **Gemma 4 31B's P4 on E3** is "supported" only as a rise from an *outward* lean at 8%
  (0.306 on this statistic) to near .5 at 25% (0.554). It is not a rise in inward
  preference like people's (.70 to .82).
- **Nemotron's P6:** its interval lies within the individual raters' range (−.28 to −.46) and
  far from the aggregate over images (−.85 to −.88). The data are 20 complete families.

## Limitations

- **One sampled reply per presentation.**
  - The NVIDIA models' figures carry sampling noise that the local models' probability
    readout does not.
  - Their sign statistic cannot be set beside the local models' sign statistic. Strength is
    compared only on P_cells.
- **Gemma 4 31B was withdrawn after 35.1% of the design.**
  - Some of its cells rest on few pairs (11 for centre over quarter line, 15 for E4, 18 for
    E3 at 8%).
  - It is reported as incomplete, and nothing substitutes for it.
- **Hosted models cannot be pinned.** The served model name and dates are recorded with each
  reply. NVIDIA may change or withdraw a model at any time, so a rerun may not reproduce
  these figures.
- **P6 needs complete E1 families** of 10 pairs. A part-done pass in random order completed
  none for Gemma 4 31B, so its P6 is not estimable.
- **Each model is a single observer**, and the intervals are over stimuli. Nothing here says
  which model has better taste.
- **Under NVIDIA's trial terms the raw replies are not distributed.** They stay in the local
  repository, and the public copy carries only these aggregates.
