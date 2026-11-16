# Gate 2

15 November 2026. Pilot on **dev stimuli only**; no test stimulus exists yet. Full tables
with intervals: `reports/gate2_tables.md` (one command: `uv run python scripts/gate2_tables.py`).

## What ran

Eight open-weight models from six families, all Apache-2.0, ungated, pinned by commit, on
about 40 dev pairs per experiment in both layouts: 7,160 trials per model, 4.3 hours of
wall-clock time with two models sharing the GPU. Prompt `dev-3`: the reply is started
with "Answer:" and the next token is read (the readout you approved as option A).

## Model against human (two-image layout, "you" framing)

Bias-cancelled choices. † = the model fails the visibility rule for that experiment.
Intervals are in `gate2_tables.md`, table 3a; with 16 to 40 pairs per cell they are wide
(typically ±.15 to ±.25), so read this as a pipeline check, not as results.

| | Human | SmolVLM2 500M | Qwen3.5 0.8B | MiniCPM-V 1B | SmolVLM2 2.2B | InternVL3.5 2B | North Micro 2.5B | Qwen3.5 4B | Gemma 4 E2B |
|---|---|---|---|---|---|---|---|---|---|
| E1 r(balance score, preference) | -.87 aggregate; -.44 individuals | -.34 † | **-.84** | -.18 | .08 | .18 | -.28 | .26 | .33 |
| E1 P(more balanced chosen) | not reported | .72 † | **.82** | .65 | .53 | .50 | .68 | .42 | .42 |
| E2 P(balanced chosen), 90 px | .53, not above chance | .56 † | .62 | .75 | .69 | .56 | **.94** | .56 | .69 † |
| E3 P(inward-facing chosen) | .74 | .38 † | .33 | .33 | .54 † | .42 | .33 | .46 | .54 |
| E3 P(centre chosen), symmetrical | above .50 | .38 † | .75 | 1.00 | .50 † | .88 | .75 | 1.00 | .88 |
| E4 P(red named heavier than yellow) | above .50 | .62 † | .75 | 1.00 | .38 | .75 | .88 | 1.00 | .75 |
| E5 P(less altered chosen) | no anchor | .54 † | .51 | .67 | .54 | .59 | .62 | .62 | .59 |

What the pilot suggests, for what a pilot is worth:

- **E1 balance.** One model (Qwen3.5-0.8B) shows a clear balance preference of human size;
  three lean that way; four are at chance.
- **E2, the contested null.** Every model is at or above the human .53. Two are clearly
  above it (North Micro .94, interval .81 to 1.00; MiniCPM-V .75, interval .56 to .94).
  This is the direction the brief predicted.
- **E3 inward bias.** No model shows it. Three models choose the *outward*-facing view
  two times in three (for two of them the interval lies wholly below .50). The centre
  bias for symmetrical objects is present in most.
- **E4 weight.** Seven of eight are above .50, the human direction (the exception is
  SmolVLM2-2.2B at .38). With eight anchored pairs per model most intervals still
  include .50.
- **E5 control.** .51 to .67; most intervals include .50.
- **"Most people" framing** (table 4a) changes little: the mirror-flip preferences are
  much the same under it (.29 to .58 against .33 to .54).

## Three things you should know before deciding

**1. E1's direction depends on the layout.** Side by side, the balance preference
disappears or reverses: every model's correlation is positive, and P(more balanced
chosen) is .15 to .50 (Qwen3.5-0.8B falls from .82 to .50; Gemma 4 is at .15, interval
.10 to .20). Same pairs, same question, same counterbalancing. So for models of this
size "the model's preference" is partly a property of how the two images are shown. That
is a finding, and the main run should measure it rather than hide it.

**2. The layout rule picks the worse layout by a hair.** Median position bias across
models is 0.46 log-odds with two images and 0.42 side by side, a difference far smaller
than the spread between models (0.06 to 3.7). The rule in `PLAN.md` therefore picks side
by side. But visibility is very different:

| Models (of 8) that can see the manipulation | E1 | E2 | E3 | E4 | E5 |
|---|---|---|---|---|---|
| Two images | 7 | 6 | 6 | 7 | 7 |
| Side by side | 7 | **0** | **2** | 6 | 7 |

Side by side, no model can tell E2's shifted picture from the original, so the contested
null could not be tested at all.

**3. How far the forced readout can be trusted.**
- No model refuses: at most 3% of free-text replies decline to choose.
- For Qwen3.5-0.8B, the one capable model run both ways on the same pairs, pair-level
  preferences under the old first-token readout and the new one correlate .89 to .90
  (two images), and the new readout removes its position bias (-1.0 to 0.0 log-odds).
- At the level of single trials the forced answer matches the model's unaided answer 60
  to 88% of the time. Single trials are dominated by position and letter bias, which the
  readout changes, so this is expected, but it means only bias-cancelled pair-level
  numbers should be reported, which is already the plan.
- Gemma 4 E2B is the outlier: position bias of +2.3 (two images) and -3.7 (side by side)
  log-odds, and 16% of two-image preference trials still off the two letters.

## GPU time for the main run

One layout is 23,012 trials per model (1,307 pairs plus 150 identical-pair controls).
Hours are summed over models; run two at a time, as in the pilot, the wall-clock time is
about half.

| Plan | Models | Summed GPU hours | Wall clock |
|---|---|---|---|
| A. Two images only | 7 | 20 | about 10 h |
| **B. Two images, plus side by side for E1, E4, E5 (recommended)** | 7 | 28 | about 14 h |
| C. Both layouts in full | 7 | 37 | about 19 h |
| Side by side only (what the rule as written picks) | 7 | 16 | about 8 h |

Seven models because I recommend dropping SmolVLM2-500M: it cannot see the manipulation
in any experiment with two images and in one of five side by side. Keeping it adds 4.3
hours (two images) for a row that would be reported as "cannot see".

## Tier 2: is an API model worth adding?

**Yes, if the credit exists.** Every Tier 1 model is 5B parameters or smaller, because
that is what fits 16 GB. The brief's most interesting prediction, that models repeat the
textbook where people do not, is a claim about models that know the textbook. The pilot
shows small models that are fragile across layouts and show no inward bias at all. A
frontier model is the missing end of the range.

Estimated cost, from the current price list (Haiku 5.5 $0.10, Sonnet 5.5 $2, Opus 5.5 $4
per million input tokens; batch requests at half price) and roughly 700 input tokens per
two-image call (about one token per 28 x 28 pixels; to be confirmed with the free
token-counting endpoint before anything is spent):

| Model and scope | Calls | Cost |
|---|---|---|
| Claude Haiku 5.5, full design, 3 samples per presentation, batch | 69,000 | about $2.50 |
| Claude Sonnet 5.5, anchored experiments only (E1, E2 at 90 px, E3 flips and centre), 2 samples, batch | 14,100 | about $10 |
| **Both** | | **about $12.50, under the $15 cap** |
| Claude Opus 5.5, anchored experiments, 1 sample, batch | 7,100 | about $17 (thinking cannot be switched off and is billed) : over the cap |

What I need from you for this: confirmation that your plan really carries API credit (a
chat subscription and API billing are usually separate), and the key placed in the
`ANTHROPIC_API_KEY` environment variable. I will not read, print or store it.

Not recommended: Tier 3 (paid beyond the cap). Other vendors' free tiers: I have not
checked their current limits; at 7,000 or more image calls per model they are likely to
take days of rate-limited waiting. I can look them up if you want one.

A free alternative at the top end: Gemma 4 12B in 4-bit, the largest model that fits this
GPU. Untested here; 4-bit loading on Windows is unverified.

## Decisions needed

1. **Layout.** Recommended: two images as the primary layout, departing from the rule as
   I wrote it, because the position-bias difference is negligible and side by side makes
   E2 untestable; plus side by side for E1, E4 and E5 as a robustness arm (plan B).
2. **Models.** Recommended: the seven above (drop SmolVLM2-500M).
3. **Tier 2.** Recommended: Haiku 5.5 on the full design and Sonnet 5.5 on the anchored
   experiments, about $12.50, if you confirm the credit and set the key. Otherwise Tier 1
   stands alone.
4. **E2 objects** (open since Gate 1): abstract shapes, as built, or schematic objects.
   This must be settled before the freeze.
5. **Go-ahead to freeze and run.** On approval I fix the prompt as `v1`, write
   `FROZEN.json`, generate the test stimuli for the first time, and run them once.
