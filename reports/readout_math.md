# How the readout shapes model–human comparisons

**Status: exploratory and post hoc, 2026-11-18, after Gate 3.** It uses only the local
models' test runs, which were opened at Gate 3, and no NVIDIA result. Every number comes
from one command, which writes `reports/readout_math.csv`:

```bash
uv run python scripts/readout_math.py
```

It changes no pre-registered number or verdict in `reports/main.md`.

## Findings

1. **Directions are robust; strengths are not.** Whether a model leans toward or away from
   the human direction is the same under every statistic below. How *strong* the lean
   looks depends almost entirely on the statistic.
2. **The local models' preferences are tiny in absolute terms.** Across pairs, the mean
   log-odds of a model's preference is under 0.15 in every headline cell except Gemma's E1
   (−0.74). A log-odds of 0.07 is a 51.8% choice. The pre-registered statistic, the share of
   pairs on each side, turns a small but consistent lean into a large number.
3. **P2's "stronger than people" rests on that amplification.** Three models are reported
   above the human ceiling on E2: MiniCPM-V .65, Qwen3.5-4B .63, North Micro .77. Measured
   as a proportion of choices, the form of the human data, they are .520, .520 and .514.
   That is inside the human range of .43 to .57, which `PLAN.md` itself defines as "matches
   people".
4. **One formula covers every readout.** With pair log-odds of mean μ and spread τ, each
   statistic is Φ(μ / √(τ² + s²)), where s is the noise the readout adds. The formula
   reproduces the simulated proportion-of-choices readouts within .001 on average, the
   sampled readouts within .007, and the share of pairs within .018.
5. **The NVIDIA run's pre-registered statistic is not comparable with the local models'.**
   Simulating the sampled readout on the local models' own probabilities, for the four
   models with an E2 lean, gives .52 to .57 where their sign statistic gave .58 to .77. The share of pairs on each side cannot be
   recovered from a few samples. A random-effects fit returns 0 or 1 because τ is not
   identifiable. The proportion of choices can be estimated from either readout.
   `PLAN.md` was amended on this point before any NVIDIA result was read.
6. **The bias is not purely additive, and much of the pair-to-pair spread is readout noise.**
   The fourth contrast of the 2 × 2 design must be 0 under any bias that depends only on
   order and letters, and it is not for any model. Its spread is a noise floor.
   - **SmolVLM2:** the floor equals the whole spread of its pair preferences, so its pairs
     differ by noise alone.
   - **North Micro (E2) and Gemma 4 E2B (E2):** most of the spread is noise.
   - **Qwen3.5-0.8B (E1):** the spread is more than twice the floor. Its balance correlation
     reflects real pair-to-pair differences.
7. **P6 cannot separate "more textbook than people" from "no response noise".** A model read
   by log-probabilities is a rater without trial-to-trial noise. Any human-like rater
   without that noise would beat the individual-rater benchmark. The discriminating test is
   a model correlation beyond the *aggregate* human correlation (about −.87).

## 1. The model of one presentation

A pair *i* is shown in four cells *j*: order × letters. The log-odds that the model names
the reference is modelled as

  ℓᵢⱼ = dᵢ + b·oᵢⱼ + a·gᵢⱼ

where:
- oᵢⱼ = ±1 says whether the reference is shown first, and gᵢⱼ = ±1 whether it is labelled A;
- b is the position bias and a the letter bias;
- dᵢ is the pair's bias-free preference.

The 2 × 2 design is balanced, so the mean over the four cells is exactly dᵢ: the
pre-registered `pref`. This holds in log-odds only. In probability, the bias does not
cancel. It *attenuates* the preference: the mean probability over cells is
¼ Σ σ(dᵢ ± b ± a), and its slope at dᵢ = 0 is ¼ Σ σ′(±b ± a), less than σ′(0) = ¼.

Gemma's median absolute position bias over its E2 pairs is 3.45 log-odds. At that size the
local slope is σ′(3.45)/σ′(0) ≈ 0.12 of the bias-free slope. In the data, Gemma's E2 proportion of choices with bias removed
is .532, against .521 with bias included.

### Is the bias additive? A noise floor from the fourth contrast

The four cells of a pair split into four orthogonal contrasts: preference dᵢ (mean), order
(× oᵢⱼ), letter (× gᵢⱼ), and order × letter (× oᵢⱼgᵢⱼ). If bias depends only on order and
letters, the order and letter contrasts are the same for every pair and the interaction is
exactly 0. This check was suggested by the position-bias literature notes in
`research_notes/`.

If each cell instead carries independent non-additive noise of SD σ, every contrast carries
noise of SD σ/2. The interaction's spread then estimates the noise in dᵢ, and the true spread
across pairs is τ_true² ≈ τ² − sd_inter².

| Model, subset | Spread of dᵢ (τ) | Interaction spread (noise floor) | τ_true |
|---|---|---|---|
| SmolVLM2-2.2B, E2 | 0.030 | 0.035 | ≈ 0 |
| North Micro, E2 | 0.096 | 0.079 | 0.054 |
| Gemma 4 E2B, E2 | 0.756 | 0.715 | 0.24 |
| MiniCPM-V, E1 | 0.694 | 0.333 | 0.61 |
| Qwen3.5-0.8B, E1 | 0.133 | 0.058 | 0.12 |

All 21 cells are in `readout_math.csv` (columns `sd_order`, `sd_letter`, `sd_inter`).

Two consequences:

1. **What P_sign measures.** P_sign = Φ(μ/τ) is the mean lean divided by a spread that is
   partly readout noise. With the noise removed, North Micro's E2 value would be
   Φ(0.073/0.054) ≈ .91. Its small lean really is consistent across pairs. For SmolVLM2,
   there is no pair-level signal at all: its E2 P_sign of .63 is a mean of 0.006 log-odds
   set against noise.
2. **The 2 × 2 average still removes the format-only part of the bias.** What remains is
   noise of known size per model, not a systematic error. The asymmetric content-dependent
   bias that would be confused with preference ("this image gains only when shown first")
   cannot be detected from these four cells.

## 2. Three statistics for "P(reference chosen)"

| Name | Definition | What it measures |
|---|---|---|
| P_sign (pre-registered) | (1/n) Σ 1[dᵢ > 0] | how consistently the lean points one way across pairs |
| P_soft | (1/n) Σ σ(dᵢ) | proportion of choices with position and letter bias removed |
| P_cells | (1/4n) Σᵢⱼ σ(ℓᵢⱼ) | proportion of choices over counterbalanced presentations, bias included |

If pairs vary as dᵢ ~ N(μ, τ²), then P_sign = Φ(μ/τ). Using σ(x) ≈ Φ(x/κ) with κ = 1.702,
P_soft ≈ Φ(μ/√(τ² + κ²)). The ratio of their probit effect sizes is √(1 + κ²/τ²): how much
the sign statistic magnifies a lean relative to the choice proportion. For North Micro on
E2 (μ = 0.073, τ = 0.096) that factor is 17.8. The formula gives P_sign .777 and P_soft .517;
the data give .767 and .518.

## 3. Which statistic matches the human numbers

The human E2 and E3 anchors are proportions of choices: people × counterbalanced trials, so
P_cells for a human sample. P_sign has no published human counterpart. It would need each
pair's majority across raters, which the papers do not report. So:

- **Direction** can be compared with any statistic.
- **Strength** ("stronger than people", "matches people") can be compared only on
  P_cells. One caveat remains: a model's sampling noise at temperature 1 comes from its
  training, not from psychology. "Matches" means "chooses as often as people do when
  answering at its native temperature".

E2, 90 px pairs, two images, "you" framing (human bars: .43 to .56; `PLAN.md` band for
"matches people": .43 to .57):

| Model | P_sign (reported) | P_soft | P_cells | Mean pair log-odds (μ) | Spread (τ) |
|---|---|---|---|---|---|
| Qwen3.5-0.8B | .392 | .496 | .496 | −0.017 | 0.099 |
| MiniCPM-V 4.7 1B | .650 | .530 | .520 | 0.124 | 0.365 |
| SmolVLM2-2.2B | .633 | .502 | .502 | 0.006 | 0.030 |
| InternVL3.5-2B | .500 | .502 | .502 | 0.009 | 0.085 |
| North Micro Vision | .767 | .518 | .514 | 0.073 | 0.096 |
| Qwen3.5-4B | .633 | .523 | .520 | 0.092 | 0.247 |
| Gemma 4 E2B | .583 | .532 | .521 | 0.149 | 0.756 |

On P_cells every model is inside the human band. The main report's "stronger than people"
for three models is a statement about consistency across pairs, not about how often they
would choose the balanced arrangement.

*Ties.* The P_sign column is as reported, with a pair whose mean log-odds is exactly 0
counted as not chosen (the pre-registered rule). The CSV's `P_sign` counts such ties as ½,
so it is .0125 to .025 higher for Qwen3.5-0.8B, MiniCPM-V and InternVL, which have 3, 3 and
6 tied E2 pairs. Ties come from identical letter log-probabilities at bfloat16 precision:
0.1 to 0.6% of trials for five models. No P2 verdict depends on them.

For E3, people chose the inward-facing version .70 and .82 of the time. Every model's
P_cells is .495 to .504, so the conclusion "no inward bias" holds on every scale.

## 4. Sampled readouts (the NVIDIA addendum)

A hosted model gives cᵢⱼ ~ Bin(k, σ(ℓᵢⱼ)) answers per cell. The pre-registered statistic
takes the sign of the mean smoothed log-odds, log((c + ½)/(k − c + ½)), with ties counting
½.

A pair's estimate is built from 4k answers near p = ½, so its sampling variance is about
4/(4k) = 1/k. That puts the sampled sign statistic on the same curve with s = 1/√k:

  P_samp(k) ≈ Φ(μ / √(τ² + 1/k))

Simulation on the local models' own probabilities agrees, within .007 on average:

| Model (E2) | P_sign (log-probabilities, reported) | Sampled, k = 1 | Sampled, k = 3 | P_cells |
|---|---|---|---|---|
| MiniCPM-V | .650 | .536 | .558 | .520 |
| North Micro | .767 | .523 | .543 | .514 |
| Qwen3.5-4B | .633 | .529 | .550 | .520 |
| Gemma 4 E2B | .583 | .543 | .572 | .521 |

**Identifiability.** From samples, only μ/√(τ² + 1/k) is estimable. When τ² is much smaller
than 1/k (here τ ≈ 0.1 against 1/k = 0.33), τ, and with it Φ(μ/τ), cannot be recovered. The
random-intercept logistic fit in the script confirms it: on simulated k = 3 data it returns
0.000 or 1.000 for several models. Estimating P_sign from samples would need 1/k well below
τ², that is k in the hundreds per pair.

**Precision of P_cells in the addendum.** At p near ½, SE ≈ √(0.25 / (4kn)): .013 for E2
(n = 120) with k = 3, and .023 with k = 1. A model's P_cells must exceed about .59 for its
interval to clear the human ceiling of .561.

## 5. Correlations: E1 and P6

Write a rater's scale values as a shared component plus individual variation and noise.
Then r_individual = r_true·√R₁ and r_aggregate = r_true·√Rₙ, where R is the reliability of
one rater or of n raters (Spearman–Brown). The published figures (r_ind ≈ −.44 against
r_agg ≈ −.87; Exp 3: −.28 against −.74) imply single-rater reliability R₁ ≈ .26 (.14), if the
aggregate is close to r_true.

A log-probability readout has no trial-to-trial noise, so its r estimates the model's own
r_true. A human-like rater with the noise removed would land between r_ind/√R_retest and
r_agg. That band includes Qwen3.5-0.8B's −.58 (−.69 to −.79 on dev under four wordings).
P6's threshold of −.46 therefore cannot show that a model is more "textbook" than people. A
model correlation beyond the aggregate, below about −.87, could.

## 6. The visibility rule in signal-detection terms

With equal-variance Gaussian evidence, AUC = Φ(d′/√2). The rule's AUC of .75 corresponds to
d′ ≈ 0.95. Gemma's E2 (.65) is d′ ≈ 0.54, and its E5 (.72) is d′ ≈ 0.82.

## What this suggests

- **For `reports/main.md`** (approved; any change is the owner's call): a post hoc note that
  P2's three "supported" verdicts describe consistency across pairs. As choice proportions,
  those models fall inside the human band.
- **For the NVIDIA addendum:** done. P_cells was added in `PLAN.md` before any result was
  read.
- **For any later study:** report μ, τ and P_cells for every model. Treat P_sign as a
  consistency measure, and compare strength with people only on a choice-proportion scale.
