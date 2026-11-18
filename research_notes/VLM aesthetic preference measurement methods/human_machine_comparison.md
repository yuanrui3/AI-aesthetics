# Comparing a model's effect with a published human effect: psychometric and statistical methods

Labels used below: **[PR]** peer-reviewed; **[PP]** preprint or working paper; **[classic]** a standard formula from the classic literature, cited to the original or a reference page. "Fetched" means the content was read in this session; "not re-fetched" means it was cited from the standard published source without being re-read here. Worked numbers that use the project's human values (.43-.56, .70/.82, r = -.28 to -.46) are my arithmetic and are marked as inferences.

Notation: Φ = standard normal CDF, Φ⁻¹ = probit, σ(x) = 1/(1+e^-x) = logistic, logit(p) = ln(p/(1-p)). For a pair i, L_i = model log-odds of choosing the target (balanced, inward-facing) image, averaged over the two presentation orders.

---

## 1. What recent "machine psychology" methods papers recommend, and the pitfalls they list

### Takeaway
The 2023-2025 methods literature agrees on the design pitfalls (contamination, prompt sensitivity, order and label biases, need for control conditions, run humans on the same items, report settings), but it is almost silent on *how to put a model effect and a human effect on one scale*. The empirical replication literature adds the key quantitative warning: LLM effects are typically the right sign but too large and too low-variance (effect sizes about 2-3x human in Fisher z; near-zero between-run variance), which is what a noise-free, aggregate-like "rater" should produce.

### Cited Findings

**Methods and guideline papers**
- Hagendorff, Dasgupta, Binz, Chan, Lampinen, Wang, Akata & Schulz, "Machine Psychology" (arXiv 2303.13988, v6, Aug 2024) **[PP]** (fetched). Lists six methodological requirements: avoid task contamination, build suitable task samples, control for input-processing biases, choose prompt prefixes/suffixes, set model parameters, evaluate outputs. — [arXiv v6](https://arxiv.org/html/2303.13988v6)
  - Temperature: "If exact reproducibility is required, studies should use temperature 0 or assign a seed"; also "The effect of temperature on capabilities is not established." — [arXiv v6](https://arxiv.org/html/2303.13988v6)
  - Sampling: test "multiple versions of one task" and "create representative samples, meaning batteries of varied prompts"; criticises "small sample sizes or convenience samples". — [arXiv v6](https://arxiv.org/html/2303.13988v6)
  - Contamination: researchers "must ensure that LLMs have never seen the tests before"; keep task structure but change wording, agents, orders; "some experiments may be procedurally generated", which makes them "inherently less susceptible to data contamination". — [arXiv v6](https://arxiv.org/html/2303.13988v6)
  - Biases listed: recency bias, common-token bias, majority-label bias; for multiple choice, shuffle answer order across runs to cover all combinations; "different expressions of the same concept compete for probability". — [arXiv v6](https://arxiv.org/html/2303.13988v6)
  - Scoring: "multiple scoring methods should be compared" where possible. On statistics it says only that "a statistical analysis can be carried out"; it does not specify tests or discuss effect sizes. — [arXiv v6](https://arxiv.org/html/2303.13988v6)
  - Self-report results "should be taken contextually (e.g. as a property of a specific system prompt on a model)". — [arXiv v6](https://arxiv.org/html/2303.13988v6)
- Ivanova, "How to evaluate the cognitive abilities of LLMs", *Nature Human Behaviour* 9(2):230-233 (Feb 2025) **[PR]**; earlier arXiv 2312.01276 ("Running cognitive evaluations on large language models: the do's and the don'ts"; v2 29 Oct 2024) **[PP]** (v2 fetched). 14 considerations. — [Nat Hum Behav record](https://ideas.repec.org/a/nat/nathum/v9y2025i2d10.1038_s41562-024-02096-z.html); [arXiv v2](https://arxiv.org/html/2312.01276v2)
  - Design: determine what the model may have learned about the test; consider shortcut strategies; "DO incorporate careful control conditions" (e.g. "Will the model show the same preference for answer a over b even when the question is omitted?"); do not rely on well-known or minimally changed items; do not overly trust auto-generated items; "DO evaluate models under conditions similar to humans"; examine culture-specific prompt features. — [arXiv v2](https://arxiv.org/html/2312.01276v2)
  - Interpretation: "DO compare model and human performance" (if the exact items have not been tested on humans, they should be); report settings, dates, materials; do not overly trust LLM scoring; "DO NOT assume that model responses reflect 'universal' human behavior" (name the reference population); do not assume the same mechanism (compare error patterns); check generalisation beyond one test; "DO NOT jump to conclusions". — [arXiv v2](https://arxiv.org/html/2312.01276v2)
  - The paper does not cover temperature, log-probabilities vs generated text, statistical tests, or the one-participant vs population question. — [arXiv v2](https://arxiv.org/html/2312.01276v2)
- Löhn et al., "Is Machine Psychology here? On requirements for using human psychological tests on LLMs", INLG 2024 **[PR, conference]**: the field still lacks a general methodology and many studies are hard to reproduce. — [ACL Anthology](https://aclanthology.org/2024.inlg-main.19.pdf)
- Dillion, Tandon, Gu & Gray, "Can AI language models replace human participants?", *Trends in Cognitive Sciences* 27(7):597-600 (2023) **[PR]**: GPT-3.5 vs human ratings across 464 moral scenarios correlated r = .95; the authors call it one anecdote. Note this is a correlation with *human mean* ratings (an aggregate-level comparison). — [PDF](https://kurtgray-lab.squarespace.com/s/can-AI-language-models-replace-human-participants.pdf)

**Empirical evidence on effect-size inflation and low variance**
- Park, Schoenegger & Zhu, "Diminished diversity-of-thought in a standard large language model", *Behavior Research Methods* 56:5754-5770 (2024) **[PR]**: re-ran 14 Many Labs 2 studies on text-davinci-003; of 8 analysable studies, 37.5% replicated the original results; 6 could not be analysed because of a "correct answer" effect, where different runs gave zero or near-zero variation, largely unchanged by demographic prompt details or answer-order changes. — [MIT DSpace](https://dspace.mit.edu/handle/1721.1/153319); [LSE record](https://researchonline.lse.ac.uk/id/eprint/121403)
- Cui, Li & Zhou, arXiv 2409.00128 **[PP]** (abstract-level only, not full text). v2 (GPT-4, 154 experiments): 76.0% of main effects and 47.0% of interactions replicated; 71.6% significant where originals were null. v3 (June 2025; GPT-4, Claude 3.5 Sonnet, DeepSeek v3; 156 experiments): main-effect replication 73-81%, interactions 46-63%; LLM effect sizes "approximately 2-3 times higher" than human in Fisher z; significant results for 68-83% of original nulls. — [arXiv v3](https://arxiv.org/abs/2409.00128v3); [EconPapers](https://econpapers.repec.org/paper/arxpapers/2409.00128.htm)
- Hewitt, Ashokkumar, Ghezae & Willer, "Predicting results of social science experiments using large language models" (working paper) **[PP]** (abstract-level): GPT-4-simulated samples predicted treatment effects with r = 0.85 (r = 0.90 on studies unpublished before the training cutoff), but "predictions systematically overestimated effect sizes". Dataset described as 476 effects / 105,165 participants in one version and 70 experiments in another. — [Stanford GSB](https://www.gsb.stanford.edu/faculty-research/publications/large-language-models-can-predict-results-social-science-experiments); [project page](https://ai4pb.stanford.edu/projects/predicting-results-of-social-science-experiments-using-large-language-models)
- Schröder, Morgenroth, Kuhl, Vaquet & Paaßen, "Large Language Models Do Not Simulate Human Psychology", arXiv 2508.06950 v3 (Aug 2025) **[PP]** (fetched). 30 Dillion et al. moral scenarios plus minimally reworded, meaning-changing versions; N = 374 humans; each LLM query repeated 10 times. On original items human vs GPT-4 r = .99. Correlation between original and reworded ratings: humans .54, GPT-3.5 .89, GPT-4 .99, Llama-3.1-70B .80, CENTAUR .83. Mean absolute shift from rewording: humans 2.20 (SD 1.08) vs GPT-4 0.42 (SD 0.56). Recommends validating against human data "for every new application", deliberate prompt variation, multiple LLMs. Does not discuss temperature. — [arXiv v3](https://arxiv.org/html/2508.06950v3)

**Older foundational AI-participant papers (not re-fetched; cited for existence and design only)**
- Binz & Schulz, "Using cognitive psychology to understand GPT-3", *PNAS* 120(6):e2218523120 (2023) **[PR]**: ran canonical vignette- and task-based cognitive experiments on GPT-3 and set results beside human data; treated the model as a single participant. — [PNAS](https://doi.org/10.1073/pnas.2218523120)
- Frank, "Baby steps in evaluating the capacities of large language models", *Nature Reviews Psychology* 2:451-452 (2023) **[PR]**. — [Nat Rev Psychol](https://doi.org/10.1038/s44159-023-00211-x)
- Demszky et al., "Using large language models in psychology", *Nature Reviews Psychology* 2:688-701 (2023) **[PR]**. — [Nat Rev Psychol](https://doi.org/10.1038/s44159-023-00241-5)

### Inferences
- The two quantitative regularities in this literature (model effects in the right direction but inflated; near-zero run-to-run variance) are exactly what a noise-free, population-mean-like rater produces when its statistics are compared with human statistics that contain response noise and rater heterogeneity (the mechanism is derived in Section 3). None of the papers above makes this derivation; Cui et al. and Hewitt et al. report the inflation without a measurement model for it.
- Schröder et al.'s r = .99 on original items with only .54 human original-vs-reworded consistency shows that a near-perfect aggregate correlation does not imply the model tracks the same stimulus properties. For this project, it supports a control condition in which the target property is removed or reversed (Ivanova's "omit the question" control), so that a model "effect" cannot come from a surface feature.
- Procedurally generated stimuli (the project's approach) are the contamination remedy Hagendorff et al. name explicitly; a published human effect, however, could still be "known" to the model as a fact, so prompts should not name the effect.
- "One participant vs a population": the literature recommends varied prompt batteries, but no paper found gives an inferential framework. The consistent position is that a single model is one (idiosyncratic) rater whose sampling noise is set by temperature, not a population; populations would have to come from varied models or prompts, and Park et al. show prompt personas do not reliably produce human-like variance.

### Gaps
- I could not fetch the full texts of Frank 2023, Demszky et al. 2023, Binz & Schulz 2023, Abdurahman et al. 2024 (PNAS Nexus, "Perils and opportunities in using large language models in psychological research"), Bisbee et al. 2024 (Political Analysis, "Synthetic replacements for human survey data?") or Wang, Morgenstern & Dickerson 2025 (Nature Machine Intelligence, "LLMs that replace human participants can harmfully misportray and flatten identity groups"); their specific recommendations are not reported here.
- No methods paper found gives a recommended statistic for "model effect vs human effect"; the closest are Trott's NNB (Section 3) and Cui et al.'s CI-overlap criterion (only 19.44% of GPT-4 CIs contained the original effect, reported second-hand in a summary of v2; not verified).

---

## 2. Thurstone / Bradley-Terry-Luce / logistic models: one latent scale for human proportions and model log-odds; temperature; d' and AUC

### Takeaway
A choice proportion identifies only the latent difference divided by the noise scale (Δ/σ), never Δ itself. A model's log-odds L is that model's own Δ/σ at temperature 1, and temperature T rescales it exactly to L/T. Raw comparisons of a human proportion with a model log-odds (or with a model "choice" derived from L) therefore mix two unknown noise scales. Scale-free comparisons are the sign, ratios of effects across conditions, and rank or correlation statistics; anything else needs an explicit assumption about the noise scale.

### Cited Findings
- **Thurstone Case V [classic]**: each option j has a discriminal value v_j ~ N(μ_j, σ²), independent and equal variance. Then P(i chosen over j) = Φ((μ_i − μ_j)/(σ√2)). — [Thurstone 1927, Psychological Review](https://doi.org/10.1037/h0070288) (not re-fetched)
- **Bradley-Terry-Luce [classic]**: P(i over j) = π_i/(π_i + π_j) = σ(θ_i − θ_j), θ = ln π; equivalently Luce's choice axiom. — [Bradley & Terry 1952, Biometrika](https://doi.org/10.2307/2334029) (not re-fetched)
- **Random-utility equivalence and scale non-identification [classic]**: BTL equals a random-utility model with iid extreme-value (Gumbel) errors (difference logistic); Thurstone equals iid normal errors. In random-utility models only coefficients divided by the error scale are identified (β/σ); the absolute utility scale is not. — [Train, *Discrete Choice Methods with Simulation*, Ch. 2-3](https://eml.berkeley.edu/books/choice2.html) (not re-fetched)
- **Logit vs probit units [classic]**: the standard logistic has SD π/√3 ≈ 1.81; σ(1.702·x) approximates Φ(x) to within 0.01 everywhere, so logit units ≈ 1.7 × probit units. — [Camilli 1994, J. Educational and Behavioral Statistics](https://doi.org/10.3102/10769986019003293) (not re-fetched)
- **d', 2AFC and AUC [classic]**: for equal-variance Gaussian signal detection, the area under the yes/no ROC equals 2AFC proportion correct: AUC = PC_2AFC = Φ(d'/√2), so d' = √2·Φ⁻¹(PC). — [Sensitivity index (reference page)](https://en.wikipedia.org/wiki/Sensitivity_index)
- **AUC to Cohen's d [classic]**: probability of superiority A = Φ(d/√2), d = √2·Φ⁻¹(A). — [Ruscio 2008, Psychological Methods](https://doi.org/10.1037/1082-989X.13.1.19) (not re-fetched)
- **Temperature = noise scale (exact, from the softmax definition)**: with answer-token logits z_A, z_B and temperature T, renormalised over the two answer tokens, P_T(A) = e^{z_A/T}/(e^{z_A/T} + e^{z_B/T}) = σ((z_A − z_B)/T) = σ(L/T). This is the BTL model with scale parameter T. Miller notes that lowering temperature to cut variance shifts variance into the between-question term or adds bias ("don't lower the sampling temperature ... unless you're studying that temperature"). — [Miller 2024, arXiv 2411.00640](https://arxiv.org/abs/2411.00640) **[PP]** (fetched)

### Inferences
**(a) Putting both on one latent scale.** In Thurstone Case V the human proportion p gives the standardized latent difference

  d'_h = Δ_h/σ_h = √2·Φ⁻¹(p)  (per-option noise units), or Δ_h/(σ_h√2) = Φ⁻¹(p)  (difference-noise units),

and in logit units logit(p). The model at temperature T gives L/T on the logit scale. Project numbers (my arithmetic):

| human p | logit(p) | Φ⁻¹(p) | d' = √2·Φ⁻¹(p) |
|---|---|---|---|
| .43 (balance, low end) | −0.282 | −0.176 | −0.249 |
| .56 (balance, high end) | +0.241 | +0.151 | +0.214 |
| .70 (inward, offset 1) | +0.847 | +0.524 | +0.742 |
| .82 (inward, offset 2) | +1.516 | +0.915 | +1.295 |

A model with mean L = 1.5 is "as strong as" the .82 condition only under the assumption that the model's noise scale at T = 1 equals the human noise scale. That assumption is not testable from choices alone.

**(b) Scale-free comparisons that need no noise assumption.** If noise is constant across conditions within each "rater", the ratio of latent effects is identified:
  human inward ratio = logit(.82)/logit(.70) = 1.516/0.847 = 1.79 (probit ratio 0.915/0.524 = 1.75);
  model ratio = mean L(offset 2)/mean L(offset 1), invariant to T.
Comparing these ratios (and signs, and condition orderings) is the fairest test of "same pattern". It assumes the total human noise (response + rater + item) is equal across the two offsets; Section 3 shows why the item and rater components matter.

**(c) Temperature.** A deterministic log-probability readout is the T → 0 limit only for choices (argmax = sign of L); the log-odds L themselves are the T = 1 quantities. A sampled model at T = 1 has choice probability σ(L_i) on pair i, so its sampled choice rate estimates E_i[σ(L_i)]; a deterministic per-pair "choice" is the sign of L_i, i.e. the majority vote of infinitely many T = 1 samples. Raising T lowers the sampled effect toward .5 without changing its sign; so any match to human magnitude achieved by tuning T is a fitted noise parameter, not a finding, unless T is fixed in advance.

**(d) Same/different vs 2AFC.** The Φ(d'/√2) relation holds for 2AFC (and yes/no AUC) under equal-variance Gaussian assumptions; it does not transfer to same/different designs, which need their own decision models (independent-observation vs differencing). The project's tasks are 2AFC, so the 2AFC relation applies.

### Gaps
- I did not retrieve a 2023-2026 paper that explicitly maps LLM log-odds onto a Thurstone/BTL scale alongside human proportions; the treatment above is derived from the classic models.
- Same/different d' formulas (Macmillan & Creelman, *Detection Theory: A User's Guide*) were not retrieved this session.

---

## 3. Aggregation: proportions vs per-item majorities, Spearman-Brown, attenuation, and where a deterministic model sits

### Takeaway
Per-item sign or majority statistics are amplified relative to mean choice proportions, by an exactly computable factor under a probit-normal model; individual-rater correlations are attenuated relative to aggregate correlations by √ρ (Spearman-Brown/Spearman). A deterministic model is noise-free with respect to its own sampling but still carries its own idiosyncratic item-level deviation, so its fair benchmark is usually the aggregate (or a k-rater crowd) for correlations, and the human mean proportion compared with the model's mean choice *probability*, not its sign fraction. Trott (2024) gives direct empirical evidence: one temperature-0 GPT-4 rating correlates with norms as well as the mean of 2-11 humans.

### Cited Findings
- **Trott, "Large Language Models and the Wisdom of Small Crowds", *Open Mind* 8:723-738 (2024)** **[PR]** (fetched via Europe PMC):
  - "Number needed to beat" (NNB) = "how many humans are needed for a sample's quality to rival the quality achieved by GPT-4". For each sample size k, up to 500 random k-person samples; each sample mean is correlated with the published norm (the gold standard); NNB is the smallest k at which a one-tailed t-test shows the sample beats GPT-4 (by difference or ratio). No closed-form formula. — [PMC11142632](https://pmc.ncbi.nlm.nih.gov/articles/PMC11142632/)
  - NNB for GPT-4: concreteness 3; relatedness 2 (Pearson 1); valence 11 (Spearman; with Pearson "there was no sample size whose performance exceeded GPT-4's"); iconicity 5-8 (Spearman), 7 (Pearson). — [PMC11142632](https://pmc.ncbi.nlm.nih.gov/articles/PMC11142632/)
  - Mean Spearman ρ with norms, GPT-4 vs individual humans: concreteness .80 vs .67 (SD .20); relatedness .80 vs .78 (.10); valence .75 vs .55 (.23); iconicity .595 vs .37 (.13). GPT-4 exceeded about 70% of individual participants on concreteness and about 79.6% on valence. — [PMC11142632](https://pmc.ncbi.nlm.nih.gov/articles/PMC11142632/)
  - GPT-4 (gpt-4-0613) at temperature 0; footnote notes temperature 0 is reportedly not fully deterministic. Rationale: "the central tendency of a sample collapses across the variation in that sample"; LLMs "may be poorly suited to questions about individual variation"; NNB varies by task, so "unwise to rely on the NNB obtained for one task"; recommends using the lower NNB of Pearson/Spearman to avoid overstating LLM quality. The paper does not use Spearman-Brown, noise ceilings or attenuation correction. — [PMC11142632](https://pmc.ncbi.nlm.nih.gov/articles/PMC11142632/)
- **Condorcet jury theorem [classic]**: if n independent voters each choose the correct option with probability p > .5, the probability that the majority is correct increases with n and tends to 1. — [Condorcet's jury theorem (reference page)](https://en.wikipedia.org/wiki/Condorcet%27s_jury_theorem)
- **Gaussian integral identity [classic]**: ∫Φ(a + b·x)φ(x)dx = Φ(a/√(1 + b²)). — [List of integrals of Gaussian functions](https://en.wikipedia.org/wiki/List_of_integrals_of_Gaussian_functions)
- **Spearman-Brown [classic]**: reliability of the mean of k parallel raters, ρ_k = kρ/(1 + (k − 1)ρ), with ρ the single-rater reliability (mean inter-rater correlation). — [Spearman-Brown prediction formula](https://en.wikipedia.org/wiki/Spearman%E2%80%93Brown_prediction_formula); originals Spearman 1910 and Brown 1910, *British Journal of Psychology* (not re-fetched)
- **Correction for attenuation [classic]**: r(T_x, T_y) = r_xy/√(ρ_xx ρ_yy). — [Spearman 1904, American Journal of Psychology](https://doi.org/10.2307/1412159) (not re-fetched)
- **Noise ceiling [classic, neuroscience]**: the best possible correlation of any model with a group-mean is bounded above by the average correlation of each subject with the group mean including that subject, and below by the leave-one-subject-out version. — [Nili et al. 2014, PLoS Computational Biology](https://doi.org/10.1371/journal.pcbi.1003553) (not re-fetched)
- **Aesthetic agreement is domain-dependent**: Vessel, Maurer, Denker & Starr, *Cognition* 179:121-131 (2018) **[PR]**: faces showed the most shared taste, then natural landscapes; "very little shared taste for architecture or artworks"; within-subjects, agreement was higher for landscapes than exterior architecture with no difference in reliability. — [MPG PuRe](https://pure.mpg.de/pubman/item/item_2604469_2); [MPIEA news](https://www.aesthetics.mpg.de/en/newsroom/news/news-article/article/beautiful-nature-controversial-art.html)
- **Generalized linear mixed model marginal vs conditional effects [classic]**: with a random intercept of variance σ_u² on the logit scale, the population-averaged (marginal) coefficient ≈ β_conditional/√(1 + c²σ_u²), c = 16√3/(15π) ≈ 0.588 (c² ≈ 0.346); for the probit link the relation is exact, β_M = β_C/√(1 + σ_u²). — [Zeger, Liang & Albert 1988, Biometrics](https://doi.org/10.2307/2531734) (not re-fetched)

### Inferences
**(a) Majority/sign amplification, exact under a probit-normal model.** Let pair i have population-mean latent preference μ_i ~ N(m, τ²) across stimulus pairs (τ = between-item spread). A human rater r responds to pair i with latent μ_i + b_ri + e (rater-by-item heterogeneity b with variance τ_r², response noise e with variance σ_e²; s² = τ_r² + σ_e²). Then:
- Human mean choice proportion: p̄ = E_i Φ(μ_i/s) = Φ(m/√(s² + τ²)) (by the Gaussian identity).
- Per-item majority of many raters, or the sign of a noise-free item mean: f = P(μ_i > 0) = Φ(m/τ).
- Amplification on the probit scale: Φ⁻¹(f)/Φ⁻¹(p̄) = √(1 + s²/τ²) ≥ 1, always, with the same sign.

Worked numbers (my arithmetic): if humans show p̄ = .56 and individual noise equals the item spread (s = τ), a noise-free per-item statistic would be Φ(0.151·√2) = .585; if s = 2τ, Φ(0.151·√5) = .632. For p̄ = .70: s = τ gives .771; s = 2τ gives .880. So a model whose per-pair sign matches the human population-mean preference exactly would report "fraction of pairs favouring balanced" of .58-.63 against a human .56, and .77-.88 against a human .70, with no difference in underlying preference. The logistic version is the same with the Zeger-Liang-Albert factor √(1 + c²·var).

Consequences for the project's statistic (a): "fraction of pairs whose mean log-odds favours the balanced image" is f-type; the human .43-.56 values are p̄-type. Fair pairings are (i) model mean choice probability p̄_m = mean_i σ(L_i) (or the T = 1 sampled choice rate) vs human p̄, with the caveat from Section 2 that the noise scales still differ; (ii) model sign fraction vs a human per-item majority fraction, if item-level human data exist; (iii) directional and ratio comparisons. Pairing f_model with p̄_human is biased away from .5 by the factor above.

**(b) Individual vs aggregate correlations.** Classical test theory with parallel raters y_ri = t_i + e_ri, single-rater reliability ρ, and an error-free predictor x (a computed balance score):
- individual rater: r(x, y_r) = r(x, t)·√ρ
- mean of k raters: r(x, ȳ_k) = r(x, t)·√(kρ/(1 + (k − 1)ρ))
- ratio aggregate/individual: √(k/(1 + (k − 1)ρ)); limit k → ∞ gives r(x, t) = r_ind/√ρ.

Worked example (my arithmetic; ρ = .30 is an assumed value, not a published one): with mean individual r = −.37 (midpoint of −.28 to −.46), r(x, t) = −.37/√.30 = −.675; for k = 20 raters, ρ_20 = .896 and r_agg = −.639. Fraction of the asymptote reached, √ρ_k, for ρ = .30: k = 1 → .55, 3 → .75, 5 → .83, 10 → .90, 20 → .95, 50 → .98. If ρ = .15 (low shared taste, plausible for artworks given Vessel et al.), r(x, t) = −.37/√.15 = −.955, which is near the ceiling, so the parallel-raters model would already be strained; this is a sign that real raters differ in slope, not just noise.

**(c) Where a deterministic model sits.** Write the model's item score m_i = a·t_i + d_i, where d_i is the model's own idiosyncratic item-level deviation (systematic, so not removed by deterministic readout or by averaging samples). If d is unrelated to x, r(x, m) = r(x, t)·√ρ_m, where ρ_m = corr(m, t)². The model is therefore "one rater with reliability ρ_m against the human true score"; deterministic readout removes only sampling noise, and its effective crowd size (the analytic analogue of Trott's NNB) is
  k_eff = ρ_m(1 − ρ)/(ρ(1 − ρ_m)), from inverting Spearman-Brown.
Practical reading: compare the model's r (i) to the distribution of individual-rater r's (report its percentile, as Trott does: "exceeded 70% of participants"), and (ii) to the aggregate r and to the noise ceiling. A model r beyond the individual mean but below the aggregate is what an aggregate-like rater of moderate fidelity produces; calling it "stronger than people" against the individual mean alone is the attenuation artefact. A model r beyond the human aggregate r on the same items is substantively notable (it predicts the balance score more strongly than the human consensus does).

**(d) Heterogeneity is not noise.** The reported individual SD ≈ .35 should be compared with the sampling SD of r for n items, ≈ (1 − r²)/√(n − 1). For example, with n = 60 items and r = −.37, sampling SD ≈ .11 (my arithmetic; n = 60 is illustrative). If the observed SD greatly exceeds this, raters genuinely differ (some prefer imbalance), and the "aggregate" r describes a mixture; a single deterministic model cannot represent that distribution, consistent with Trott's caveat that LLMs "may be poorly suited to questions about individual variation".

**(e) Correlations compared on the Fisher-z scale.** z = atanh(r), SE ≈ 1/√(n − 3); individual human r = −.28 and −.46 correspond to z = −0.288 and −0.497.

### Gaps
- I could not verify the agreement metric used by Vessel et al. 2018 (often described as "mean-minus-one" correlation) or obtain their numeric agreement values; the ρ = .30 and .15 above are assumptions, not published values.
- No 2023-2026 paper found applies Spearman-Brown or disattenuation explicitly to LLM-vs-human-rater comparisons; Trott's NNB is the closest empirical analogue.
- The amplification formula assumes Gaussian item and rater effects; with skewed item distributions the factor differs (direction unchanged).

---

## 4. Equivalence and non-inferiority testing for "the model matches people"; human effects published as a range or a direction

### Takeaway
"Matches people" must be a pre-specified interval claim: equivalence (TOST, HDI-within-ROPE, or interval Bayes factor) against a margin chosen before seeing model data, on the scale fixed in Sections 2-3. When the human effect is published only as a range or a direction, the honest tests are (i) "inside a pre-registered region built from the human range plus human sampling uncertainty", (ii) a one-sided direction test, or (iii) a minimum-effect test; and the published human uncertainty, not just the model bootstrap interval, has to enter the comparison.

### Cited Findings
- **TOST [classic]**: declare equivalence within (Δ_L, Δ_U) if both one-sided tests H01: θ ≤ Δ_L and H02: θ ≥ Δ_U are rejected at α; equivalently the (1 − 2α) CI (90% for α = .05) lies inside the bounds. — [Lakens 2017, Social Psychological and Personality Science](https://doi.org/10.1177/1948550617697177) (not re-fetched)
- **Choosing the margin (smallest effect size of interest) [classic]**: tutorial on setting equivalence bounds from theory, benchmarks or resources. — [Lakens, Scheel & Isager 2018, AMPPS](https://doi.org/10.1177/2515245918770963) (not re-fetched)
- **Small telescopes [classic]**: a benchmark effect d33, the effect size the original study had 33% power to detect, for judging whether a replication is consistent with a detectable effect. — [Simonsohn 2015, Psychological Science](https://doi.org/10.1177/0956797614567341) (not re-fetched)
- **HDI + ROPE [classic]**: accept the null value for practical purposes if the 95% HDI lies inside the region of practical equivalence, reject if entirely outside, otherwise undecided. — [Kruschke 2018, AMPPS](https://doi.org/10.1177/2515245918771304) (not re-fetched)
- **TOST vs HDI-ROPE vs interval Bayes factor**: Linde, Tendeiro, Selker, Wagenmakers & van Ravenzwaaij, *Psychological Methods* 28(3):740-755 (2023) **[PR]**: the interval Bayes factor had better power, especially at small n; TOST and HDI-ROPE generally needed more than 250 cases per condition with margins of about .2-.3. — [UvA DARE](https://dare.uva.nl/id/403cf67e-6e84-4540-83f3-3f88f7d2c66c)
  - Contested: Campbell & Gustafson show the three can be "reverse engineered -- almost exactly -- from one another" once calibrated to the same type-I error, which removes most of the Bayes factor's advantage **[PP]**. — [arXiv 2104.07834](https://arxiv.org/pdf/2104.07834)
  - Göppert, Meyen & Franz (TeaP 2023 abstract): with a three-outcome scheme, the interval Bayes factor's indecisive outcomes were more likely under inequivalence, biasing it toward equivalence; HDI+ROPE or a CI analogue separated the cases better **[conference abstract]**. — [TeaP 2023](https://coms.events/teap-2023-trier/data/abstracts/en/abstract_0451.html)
- **Prediction interval for a replication [classic-recent]**: the replication estimate should fall within θ̂_orig ± 1.96·√(SE_orig² + SE_rep²), which accounts for sampling error in both studies. — [Patil, Peng & Leek 2016, Perspectives on Psychological Science](https://doi.org/10.1177/1745691616646366) (not re-fetched)

### Inferences
**(a) The test statistic.** On a scale chosen in advance (probit of mean proportion, or Fisher z for correlations), δ̂ = θ̂_model − θ̂_human, SE_δ = √(SE_model² + SE_human²) when the two are independent samples of stimuli and raters. SE_model comes from the cluster bootstrap over stimuli; SE_human comes from the paper (rater and stimulus sampling). Equivalence holds if the 90% CI of δ lies within (−M, M). Testing whether the model's own CI sits inside the human range treats the human value as known and is liberal.

**(b) Human effect published as a range across conditions (balance .43-.56).** A range across conditions is not a sampling interval. Options, in order of strength:
1. If condition-level human values and SEs exist, test condition by condition (or test the model's pattern across conditions, e.g. correlation or ordering of condition effects).
2. Otherwise pre-register an equivalence region equal to the human range widened by the typical human SE: on the probit scale (−0.176 − 1.96·SE_h, 0.151 + 1.96·SE_h), and run TOST of the model's mean-probability statistic against it.
3. Note that the human range straddles .5 here, so "the model shows no strong balance preference" is the relevant equivalence claim; a model sign fraction of, say, .70 must first be converted to a p̄-type statistic (Section 3) before it is called "outside the human range".

**(c) Human effect published only as a direction (or p < .05).** Use a one-sided test that the model effect exceeds 0 (direction match), or a minimum-effect test that it exceeds a smallest effect of interest such as Simonsohn's d33 computed from the original study's N. Do not claim magnitude equivalence.

**(d) Margins worth pre-specifying.** For proportions, a margin of ±.05 to ±.10 in choice probability near .5 corresponds to ±0.13 to ±0.25 on the probit scale (since Φ⁻¹(.55) = 0.126, Φ⁻¹(.60) = 0.253; my arithmetic). For the inward-facing task, a ratio-based equivalence (model ratio of effects at the two offsets vs human 1.79) is scale-free and more defensible than a magnitude margin.

**(e) Small numbers of stimuli.** Linde et al.'s >250-per-condition figure means most stimulus-level equivalence claims with tens of pairs will be "undecided"; the honest report is the interval and the word "undecided", not "matches".

### Gaps
- I found no 2023-2026 paper that applies TOST or ROPE specifically to LLM-vs-human effect comparisons.
- I did not retrieve the exact interval Bayes factor formulation in Linde et al. (prior choices), so it is not specified here.

---

## 5. Mixed-effects logistic models with crossed random effects vs the cluster bootstrap; practice for few-model comparisons

### Takeaway
Stimuli are a random factor and must be treated as such, either by crossed random effects in a GLMM or by resampling stimuli; a one-way bootstrap over stimuli is fine when stimuli are the only crossed factor, but underestimates variance when prompts, seeds or conditions are also sampled, and no exact bootstrap exists for crossed designs (pigeonhole or product-weight bootstraps are mildly conservative alternatives). GLMM fixed effects are conditional (item-specific) log-odds, which are larger than population-averaged ones, so a GLMM coefficient must not be compared with a published marginal proportion without conversion. With a handful of models, treat each model as a fixed effect and compare models by paired, item-level differences with clustered SEs.

### Cited Findings
- **Stimuli as random [classic]**: treating stimuli as fixed inflates type-I error for generalisation to new stimuli; models should include crossed random effects for participants and stimuli. — [Judd, Westfall & Kenny 2012, JPSP](https://doi.org/10.1037/a0028347); [Baayen, Davidson & Bates 2008, J. Memory and Language](https://doi.org/10.1016/j.jml.2007.12.005); maximal random-effects structure justified by design: [Barr, Levy, Scheepers & Tily 2013, JML](https://doi.org/10.1016/j.jml.2012.11.001) (all not re-fetched)
- **Few grouping levels**: random-effect variances are poorly estimated with few levels; common advice is to treat a factor with fewer than about 5-6 levels as fixed. — [Bolker, GLMM FAQ](https://bbolker.github.io/mixedmodels-misc/glmmFAQ.html) (not re-fetched)
- **Crossed bootstrap**: Owen 2007, "The pigeonhole bootstrap", *Annals of Applied Statistics* 1(2) **[PR]**: the naive bootstrap ignores row and column similarity and under-estimates variance; the pigeonhole bootstrap resamples rows and columns independently, is mean-consistent in heteroscedastic, unbalanced crossed random-effects models, and overestimates variance (by twice the naive amount in the crossed setting); McCullagh (2000) showed no exact bootstrap exists for crossed random effects. — [arXiv 0712.1111](https://arxiv.org/pdf/0712.1111); [Project Euclid](https://projecteuclid.org/journals/annals-of-applied-statistics/volume-1/issue-2/The-pigeonhole-bootstrap/10.1214/07-AOAS122.pdf)
  - Owen & Eckles 2012, *Annals of Applied Statistics* **[PR]**: independent bootstrap reweighting of each factor's levels (product weights) is "mildly conservative". — [doi 10.1214/12-AOAS547](https://dx.doi.org/10.1214/12-aoas547)
  - Applied example (probit, crossed items x customers, arXiv 2308.15681 **[PP]**): naive SEs underestimated variances by factors of 3 to 954. — [arXiv 2308.15681](https://arxiv.org/pdf/2308.15681)
- **Miller 2024, "Adding Error Bars to Evals" (Anthropic), arXiv 2411.00640** **[PP]** (fetched):
  - SE of mean score = √(Var(s)/n); clustered SE = √(SE_CLT² + (1/n²)·Σ_c Σ_i Σ_{j≠i}(s_ic − s̄)(s_jc − s̄)); on DROP the clustered SE was 1.34 vs 0.44 naive (3.05x). — [arXiv](https://arxiv.org/abs/2411.00640)
  - Resampling K answers per question: Var(s_i) = σ_i²/K; in the uniform-difficulty binary example, Var(μ̂ | K) = Var(μ̂ | K = 1)·(1 + 2/K)/3 (limit 2/3); do not pool SEs over K·N answers as if independent. — [arXiv](https://arxiv.org/abs/2411.00640)
  - Next-token probabilities: if the answer is the first token, conditional variance is zero and Var(μ̂) = Var(p)/n; use per-question expected scores where available. — [arXiv](https://arxiv.org/abs/2411.00640)
  - Paired comparisons: SE_paired = √(Var(s_A − s_B)/n) = √(SE_A² + SE_B² − 2·SE_A·SE_B·Corr(s_A, s_B)); with score correlation .5, variance falls from 1/6 to 1/9; report pairwise differences, SEs and correlations. — [arXiv](https://arxiv.org/abs/2411.00640)
  - Power: n = (z_{α/2} + z_β)²(ω² + σ_A²/K_A + σ_B²/K_B)/δ², ω² = Var(x_A) + Var(x_B) − 2Cov(x_A, x_B); example n ≈ 969 for δ = .03 with ω² = 1/9; with n = 198, raising K from 1 to 10 cut the MDE from 13.2% to 7.5%. — [arXiv](https://arxiv.org/abs/2411.00640)

### Inferences
**(a) A GLMM for the project's 2AFC data.** For model M, stimulus pair s, condition c, presentation order o:
  logit P(y_{M,s,c,o} = target) = β_0 + β_c + β_o + u_s + v_{s,c}, u_s ~ N(0, σ_u²), v_{s,c} ~ N(0, σ_v²),
with order (position) as a fixed nuisance term from counterbalancing and pair-level random intercepts and random condition slopes. For a deterministic log-probability readout, fit a linear mixed model to L_{s,c} directly (it is already a log-odds) rather than a binomial GLMM on one deterministic "choice" per cell; for sampled data, fit the binomial GLMM to the K samples per cell. Prompt variants, if several, enter as a second crossed random factor.

**(b) Conditional vs marginal.** β_c from (a) is item-specific; the human published proportion is marginal over items and raters. Convert with β_M ≈ β_C/√(1 + 0.346·σ_u²) (logit) before comparing magnitudes; for example σ_u² = 1 gives a factor 0.862 and σ_u² = 3 gives 0.700 (my arithmetic). This is the same aggregation effect as Section 3(a), seen from the model side: model per-pair log-odds are conditional quantities; human mean proportions are marginal.

**(c) Bootstrap vs GLMM.** The cluster bootstrap over stimuli (resample pairs, keep all conditions and both orders for a resampled pair together) is valid when stimuli are the only random factor; it makes no distributional assumption and works for any statistic (sign fractions, correlations, ratios). If prompt wordings or seeds are also varied and the claim is meant to generalise over them, use a two-way (pigeonhole or product-weight) bootstrap over stimuli x prompts, accepting mild conservatism. GLMM and bootstrap answers should agree to within simulation error; a large disagreement usually signals a mis-specified random-effects structure.

**(d) Few models.** With 2-6 models, there is no population of models to generalise to and too few levels for a model random effect; treat model as fixed, report each model's estimate with its stimulus-cluster CI, and compare models by paired item-level differences (Miller's paired SE, or bootstrap of the difference with the same resampled pairs for both models). Statements about "VLMs in general" are not supported by this design.

**(e) The two model readouts.** The deterministic log-probability readout has zero within-item variance (Miller's ε_i = 0), so its SE is pure stimulus-sampling variance; the temperature-1 sampled rater adds within-item variance σ_i²/K that shrinks with K. Their *means* differ by construction (E σ(L) vs sign(L), Section 3), so the two readouts should not be pooled or treated as replicates.

### Gaps
- I did not retrieve 2023-2026 work fitting crossed-random-effects GLMMs to LLM behavioural-experiment data specifically.
- A 2025 position paper arguing against CLT-based intervals in LLM evals with fewer than a few hundred items (arXiv 2503.01747, appeared in search results) was not fetched; its recommendations are not reported here.
- The pigeonhole bootstrap's behaviour with very few levels of the second factor (e.g. 2-4 prompt variants) was not established from the sources read.
