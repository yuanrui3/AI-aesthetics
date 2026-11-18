# Position, order and label bias in LLM/VLM pairwise and multiple-choice judgements: models, measurement and removal (2023-2026)

Notation used throughout (my own, chosen to match the project's design). For a pair (R = reference, X = alternative) shown in presentation cell c, the per-presentation log-odds in favour of R is
ℓ_c = log P(choose R | c) − log P(choose X | c),
with the probabilities renormalised over the two answer tokens. Δ is the content preference (the target). σ(z) = 1/(1+e^(−z)) is the logistic function and logit = σ⁻¹.

Source status tags: [PR] = peer-reviewed venue confirmed in a fetched page or index entry; [PR*] = venue from my background knowledge, not shown on the arXiv page I fetched (verify before citing); [preprint] = arXiv only as of the fetched version.

---

## 1. Proposed models of position, label and order bias, with their equations

### Takeaway
Almost every 2023-2026 debiasing method assumes the bias is a content-independent prior over option slots or IDs that multiplies the probabilities. That is the same as an additive shift in log-odds, and it is the Bradley-Terry "order effect" model from 1977. The methods differ mainly in where the prior is estimated: a content-free input (CC), random in-domain text (DC), the batch mean (BC), or permutations of a few test items (PriDe). Since 2024, the more flexible proposals (CalibraEval) drop the additive or multiplicative form in favour of a learned monotone map, and they treat the position-swap and ID-swap counterfactuals as the identifying constraints. Those counterfactuals are exactly the project's 2x2 cells.

### Cited Findings

**PriDe: prior over option IDs [PR*: ICLR 2024]**
- Selection bias is defined as "the model's behavioral tendency to select specific option IDs (such as 'A') as answers." The observed distribution under option permutation I is decomposed as P_observed(d_i | q, x^I) = Z⁻¹_{q,x^I} · P_prior(d_i | q, x^I) · P_debiased(o_{f_I(i)} | q, x^I). The working version assumes the prior depends only on the question and the debiased term is permutation-invariant: P_observed(d_i | q, x^I) = Z⁻¹ · P_prior(d_i | q) · P_debiased(o_{f_I(i)} | q, x) — [Zheng et al., arXiv 2309.03882](https://arxiv.org/abs/2309.03882)
- Two estimators appear in the same paper. (a) The "Cyclic Permutation" debiased estimate is an arithmetic mean in probability space: P̃_debiased(o_i | q, x) = (1/|I|) Σ_I P_observed(d_{g_I(i)} | q, x^I). It uses the n cyclic permutations, so cost is ×n instead of n!. (b) The prior is estimated as a log-space (geometric) mean: P_prior(d_i | q) = softmax( (1/|I|) Σ_I log P_observed(d_i | q, x^I) ). PriDe estimates per-sample priors on K = α|D| test samples (α = 5% in the example) and averages them into a global prior P̃_prior. All remaining samples are then debiased from a single presentation by P̃_debiased(o_i | q, x) ∝ P_observed(d_i | q, x) / P̃_prior(d_i) — [Zheng et al.](https://arxiv.org/abs/2309.03882)
- Reported costs on MMLU: PriDe(5%) ×1.15, PriDe(40%) ×2.2, PriDe(80%) ×3.4, against ×4 for full cyclic permutation. The estimated priors were "stable from 2% to 20% of samples" — [Zheng et al.](https://arxiv.org/abs/2309.03882)
- The bias metric is RStd, the standard deviation of per-option-ID recall. It is chosen because it is less sensitive to label imbalance than counting predictions — [Zheng et al.](https://arxiv.org/abs/2309.03882)
- Scope: 20 LLMs, MMLU / ARC-Challenge / CSQA, 2 to 5 options. With balanced gold answers on 1,000 MMLU items, llama-30B chose A/B/C/D 34.6 / 27.3 / 22.3 / 15.8% and gpt-3.5-turbo chose 22.5 / 25.6 / 32.3 / 19.6% (χ² p ≪ 10⁻⁴). Moving every gold answer to D cut gpt-3.5-turbo 0-shot MMLU from 67.2 to 60.9; moving every gold answer to A raised llama-30B from 53.1 to 68.2 — [Zheng et al.](https://arxiv.org/abs/2309.03882)
- Label (token) bias versus position bias: the authors conclude token bias is "one primary intrinsic cause." Removing the option IDs cut RStd sharply (MMLU 5.5 → 1.0; ARC 3.3 → 0.6). The remaining position bias is "quite irregular, largely depending on models and tasks." Switching to a/b/c/d or 1/2/3/4 gave no notable reduction (RStd 6.8 and 3.8 against 5.5). Debiasing instructions and chain-of-thought also did not help (6.1 and 4.5 against 5.5) — [Zheng et al.](https://arxiv.org/abs/2309.03882)
- Results for gpt-3.5-turbo, MMLU 0-shot: default RStd 5.5 / accuracy 67.2; PriDe(5%) 2.8 / 68.0; cyclic permutation 1.1 / 69.8. Average over models (0-shot): cyclic permutation RStd −8.7, accuracy +4.9; PriDe(5%) RStd −7.6, accuracy +1.2 — [Zheng et al.](https://arxiv.org/abs/2309.03882)

**Contextual, domain-context, prototypical and batch calibration (as written in the BC paper) [BC: PR*, ICLR 2024]**
- Contextual calibration (Zhao et al. 2021): p̂_cf = p(y | "[N/A]", C), W = diag(p̂_cf)⁻¹, output W·p(y | x, C). This is division in probability space. The BC paper describes the resulting boundary as "a rotation of the ICL's linear decision boundary around the origin": p₀ − p₁·(p̂₀/p̂₁) = 0 — [Zhou et al., arXiv 2309.17249](https://arxiv.org/abs/2309.17249)
- Domain-context calibration (Fei et al. 2023): p̂_random = (1/T) Σ_t p(y | [Random in-domain text]_t, C), corrected by "dividing the estimated prior prediction, or equivalently in logits space" subtracting it. The boundary is a shift: p₀ − p₁ = p̂₀ − p̂₁. The BC paper is ambiguous about whether p here means probabilities or logits — [Zhou et al.](https://arxiv.org/abs/2309.17249)
- Prototypical calibration fits a GMM, P_GMM(p) = Σ_j α_j N(p | μ_j, Σ_j), to the output vectors. Its boundary is non-linear — [Zhou et al.](https://arxiv.org/abs/2309.17249)
- Batch Calibration: p̂(y_j | C) = E_x[p(y = y_j | x, C)] ≈ (1/M) Σ_i p(y_j | x⁽ⁱ⁾, C), and ŷ_i = argmax_y [p(y | x_i, C) − p̂(y | C)]. The paper says this is "equivalently" a shift of the log-probability by the class mean. It also gives a running estimate, p_r^(n+1) = (n/(n+1))·p_r^n + (1/(n+1))·p̂^(n+1). BCL adds a strength parameter: p_BCL = p − γ·p̂, with γ = 0 uncalibrated, γ = 1 BC, and γ tuned on labelled data over [−5, 5]. BC's only stated requirement is "a batch of inputs to estimate the contextual bias," which implicitly needs the batch to represent P(x) — [Zhou et al.](https://arxiv.org/abs/2309.17249)
- BC results: PaLM 2-S 1-shot average 66.20 → 74.41 (CC 62.39, PC 67.65). PaLM 2-L 75.16 → 81.09 (CC 77.83, DC 76.89). CLIP ViT-B/16 zero-shot, six-task average 36.7 → 41.5 (SVHN 18.0 → 35.0) — [Zhou et al.](https://arxiv.org/abs/2309.17249)

**LLM-judge-specific formulations**
- Balanced Position Calibration: CS_R = Σ_{i=1..k} (S_R^i + S_R'^i) / (2k), the mean of a response's scores over k samples in each position. Multiple Evidence Calibration samples k explanation-then-score judgements. Human-in-the-loop routing uses BPDE = Σ_{er ∈ {win, tie, lose}} −p_er log p_er, with p_er = [Σ_i 1(ER_i = er) + 1(ER'_i = er)] / (2k) — [Wang et al., arXiv 2305.17926](https://arxiv.org/abs/2305.17926) [PR*: ACL 2024]
- Judging the Judges defines three metrics:
  - Repetition stability: RS = (1/N) Σ_j (1/n_j) max_k |C_k^j|.
  - Position consistency: PC = (1/n) Σ_j 1{same winner across all permutations}.
  - Preference fairness: PF_raw = rcn·irr − pcn·ipr, the recency count × recency rate among inconsistent pairs minus the primacy count × primacy rate. It is min-max normalised to [−1, 1], where 0 is fair, < 0 primacy and > 0 recency.
  - Answer-quality gap: δ_q = |owr − 1/p|, with owr = (1/n)[C_w + (1/p)(C_t + C_I)].
  - Source: [Shi et al., arXiv 2406.07791](https://arxiv.org/abs/2406.07791) [preprint, v9 Nov 2025]
- PORTIA defines position bias as dependence between the answer permutation Π and the verdict V. Consistency means LLM({q, r₁, r₂}) = LLM({q, r₂, r₁}). The method splits each answer into k = 3 segments, aligns them by length and then by token-overlap similarity, and interleaves them into one prompt — [Li et al., arXiv 2310.01432](https://arxiv.org/abs/2310.01432) [preprint]
- CalibraEval generalises PriDe to P_observed(t_i | I, X₀) = f(P_prior, P_debiased) with f unspecified, because the interaction "may not be simply multiplicative or additive." It learns a monotone map P_debiased = g(P_observed) from the four orderings of a pair:
  - X₀ = [(t₁, o₁); (t₂, o₂)]
  - X₁ = [(t₂, o₂); (t₁, o₁)] (positions swapped)
  - X₂ = [(t₁, o₂); (t₂, o₁)] (IDs swapped)
  - X₃ = [(t₂, o₁); (t₁, o₂)]

  The ideal constraints are P(t₁ | X₀) = P(t₁ | X₁) = P(t₂ | X₂) and P(t₂ | X₂) = P(t₂ | X₃). The objective is min_g Σ_i [g(s₀ⁱ) + g(s₂ⁱ) − 1]² + [g(s₀ⁱ) − g(s₁ⁱ)]² − λ[g(s₀ⁱ) − g(s₂ⁱ)]², with λ = 0.5. g is parameterised as a cumulative softmax over sorted observed scores, so it is monotone, and is smoothed with PAVA — [Li et al., arXiv 2410.15393](https://arxiv.org/abs/2410.15393) [PR: ACL 2025, [anthology](https://aclanthology.org/2025.acl-long.808/)]
- CalibraEval reports average Kappa / ICC(2,k) (default → PriDe → CalibraEval):
  - Llama-3-8B: 31.14 / 71.14 → 37.35 / 76.83 → 39.16 / 83.38.
  - GPT-4o: 78.14 → 77.54 → 78.53 (Kappa). PriDe slightly hurt the strongest judge here.
  - Reference-based RStd on RewardBench for ChatGPT: default 16.79 → PriDe 8.54 → CalibraEval 5.51.
  - DC (domain-context calibration) was often worse than doing nothing.
  - Source: [Li et al.](https://arxiv.org/abs/2410.15393)

**Classical paired-comparison order effect (the statistical ancestor)**
- Davidson and Beaver (1977, *Biometrics* 33:693-702) extended Bradley-Terry to within-pair order effects — [record](https://scilit.com/publications/94078d32740ff4e1fc2839085db1ed84). In log-scale form: P(i beats j) = exp(λ_i) / (exp(λ_i) + exp(λ_j + γ)), with γ = 0 meaning no order advantage — [bpcs paper, arXiv 2101.11227](https://arxiv.org/abs/2101.11227). Multiplicative on the odds, this is additive on the log-odds. Later work combines ties with order effects (David 1988 reduces to Davidson-Beaver) — [arXiv 2505.24783](https://arxiv.org/abs/2505.24783)
- 2AFC-LMMs aggregates VLM pairwise choices with Thurstone Case V MAP: argmax_q Σ_ij C_ij log Φ(q_i − q_j) − Σ_i q_i²/2, subject to Σ q_i = 0 — [Zhu et al., arXiv 2402.01162](https://arxiv.org/abs/2402.01162) [PR per search index: IEEE TCSVT 2024]

### Inferences
- **One model behind most methods.** For two options, PriDe's multiplicative prior, CC's diag(p_cf)⁻¹, DC, BC's log-space reading and Davidson-Beaver's γ are all the same model: ℓ_c = Δ + β(c), a content-independent additive log-odds offset that depends only on the presentation format. They differ only in the reference input used to estimate β:
  - CC: an "[N/A]" input.
  - DC: random in-domain text.
  - BC: the mean over real test inputs.
  - PriDe: the order-averaged log-odds of a few real items.
  - The project: identical image pairs (X, X).
  
  Identical pairs are the cleanest content-free input in this family. They are in-domain and have known Δ = 0, which avoids the BC paper's criticism that "[N/A]" inputs carry their own bias.
- **PriDe on two options reduces to the project's estimator.** With n = 2 there are only two cyclic permutations, and PriDe's per-sample prior log-odds of the first ID is ½[λ(order 1) + λ(order 2)]. That is exactly the project's "mean log-odds for first" estimate, computed on real pairs instead of identical ones. Since the project already runs every order, PriDe adds nothing except cost savings. Its main 2-option use would be to save hosted-model calls by running one order on most pairs, and that is a poor trade when only sampled choices are available (see Q4).
- **Internal inconsistency in PriDe and BPC.** PriDe's cyclic-permutation baseline averages in probability space, but its own multiplicative model implies exact removal only for the geometric (log-space) mean. Wang et al.'s BPC averages raw 1-10 scores, which assumes additivity on the score scale.
- **CalibraEval's design is the project's design.** Its X₀-X₃ are exactly the 2x2 order × label cells. Its constraints are the same symmetry conditions the 4-cell average relies on, but it enforces them through a monotone map pooled over items rather than by per-item averaging.
- **The direction of evidence (2023-2026):** labels/IDs matter at least as much as slots (PriDe; MT-Bench's "rename" prompt, Q4). The additive-prior assumption appears to work well for weaker models and to be unnecessary or slightly harmful for the strongest ones (CalibraEval on GPT-4o).

### Gaps
- I did not retrieve the original Zhao et al. (2021) or Fei et al. (2023) papers. Their equations above are as restated by the BC paper, which itself flags an ambiguity between probabilities and logits for DC.
- The venues for PriDe, BC, Wang et al. and MT-Bench come from my background knowledge, not from fetched pages.
- PINE ("Eliminating position bias of language models: a mechanistic approach") and other attention-level methods for text LLMs were not retrieved. SoFA, the VLM analogue, is covered in Q3.

---

## 2. When averaging over permutations removes bias exactly (log-odds vs probability space), and what happens when bias interacts with content

### Takeaway
Averaging per-cell log-odds over a balanced order × label design removes any bias that is a fixed function of the presentation format, whatever its size and including any position × label interaction. This is exact under the additive-logit (multiplicative-prior) model that PriDe, CC, BC and Bradley-Terry with an order effect all assume. Averaging probabilities keeps the sign of the preference but shrinks its magnitude, by a factor that collapses as the bias grows. Content-dependent bias cancels only when it is symmetric in the ordered pair. The asymmetric part is algebraically indistinguishable from preference. The literature consistently finds that bias is content-dependent: it is largest when the two options are close in quality.

### Cited Findings
- **Bias grows as the quality gap shrinks (MT-Bench).** Position bias "is more noticeable for models with close performance" and "can almost disappear when the performance of the two models differs a lot." GPT-3.5 vs LLaMA-13B gave 98.8% consistency; GPT-3.5 vs Claude-v1 gave 67.5% — [Zheng et al., arXiv 2306.05685](https://arxiv.org/abs/2306.05685) [PR*: NeurIPS 2023 Datasets & Benchmarks]
- **Conflict rate falls as the score gap rises.** For GPT-4, results are "significantly affected" by position when the score gap is ≤ 1 and relatively stable when it is ≥ 3. This explains why GPT-4's conflict rate was 4/80 (5.0%) for Vicuna-13B vs Alpaca-13B but 37/80 (46.3%) for Vicuna-13B vs ChatGPT — [Wang et al.](https://arxiv.org/abs/2305.17926)
- **A formal test of which factors drive bias.** Judging the Judges used bidirectional stepwise regression (AIC) to predict PC and PF from judge, candidate, task, quality gap and length.
  - Judge, task and quality gap stayed significant for both PC and PF; candidate identity was significant for PC.
  - PC rises with the quality gap in a "parabolic" pattern.
  - PF depends on the gap more weakly, and GPT models stay near PF = 0 regardless of the gap.
  - Length variables barely changed AIC.
  - Source: [Shi et al.](https://arxiv.org/abs/2406.07791)
- **Testing non-additivity by relaxing the functional form.** CalibraEval argues the prior-content interaction "may not be simply multiplicative or additive" and fits an arbitrary monotone map instead. It outperformed PriDe's multiplicative correction on all five judges in its Table 1 — [Li et al.](https://arxiv.org/abs/2410.15393)
- **Testing whether the prior is stable across items.** PriDe tests the constant-prior assumption indirectly: priors estimated from 2% to 20% of samples were stable — [Zheng et al.](https://arxiv.org/abs/2309.03882)
- **The psychophysics analogue: a guessing mixture.** García-Pérez and Alcalá-Quintana show that interval (order) bias in 2AFC is "strong and common" and contradicts the standard difference model. They model it with indecision: the observer is sometimes undecided and then guesses with a bias toward one response. This mixture model fits as well as alternatives but gives different sensory parameter estimates — [UCM repository record, *Atten. Percept. Psychophys.* 2011](https://docta.ucm.es/entities/publication/ab29d99b-ee36-4c49-9d3c-0efa968489e2/full)

### Inferences
- **Exact cancellation in the 2x2 design (derivation).** Let F/S mean the reference is shown first/second, and AB/BA be the label order. Write a format-only bias with a slot term P and a letter term L, so the raw A-vs-B log-odds bias is β(AB) = L + P and β(BA) = L − P. Converting to reference log-odds gives the four cells:
  - c₁ (F, AB) = Δ + L + P
  - c₂ (F, BA) = Δ − L + P
  - c₃ (S, AB) = Δ − L − P
  - c₄ (S, BA) = Δ + L − P

  Then:
  - Mean of the four cells = Δ exactly, for any β(AB) and β(BA). Any position × label interaction is absorbed because there are only two formats.
  - Position bias: P̂ = (c₁ + c₂ − c₃ − c₄)/4.
  - Label bias: L̂ = (c₁ + c₄ − c₂ − c₃)/4.
  - Built-in non-additivity test: (c₁ − c₂ + c₃ − c₄)/4. This is identically 0 under any format-only bias, and it measures a content × format interaction.

  With deterministic log-probabilities there is no sampling noise. The spread of this contrast across pairs, relative to the spread of Δ̂, therefore directly measures non-additivity. A few hundredths of a logit can still come from GPU nondeterminism.
- **Content-dependent bias: what cancels and what does not.** Let b(x, y) be the log-odds bias toward the first slot when x is first and y is second. Then ℓ_F = Δ + b(R, X) and ℓ_S = Δ − b(X, R), so
  mean = Δ + [b(R, X) − b(X, R)]/2.
  - The symmetric part, b(x, y) = b(y, x), cancels exactly however strongly it depends on content. This covers "bias is larger when the pair is close in quality" (a function of |Δ|) and the classic level-dependent time-order error. In a weighting model ℓ = κ₁u_first − κ₂u_second, the bias term (κ₁ − κ₂)(u_R + u_X)/2 is symmetric, and averaging leaves ((κ₁ + κ₂)/2)(u_R − u_X): correct in sign, rescaled.
  - The antisymmetric part, for example "image R gets an extra boost only when it is first," is aliased with Δ and cannot be identified from order counterbalancing alone. In practice the counterbalanced design therefore defines preference as the order-averaged quantity.
- **Probability-space averaging under the additive model.** With p_F = σ(Δ + b) and p_S = σ(Δ − b), the average p̄ = ½[σ(Δ + b) + σ(Δ − b)] is increasing in Δ and equals ½ at Δ = 0, so the sign is preserved.
  - Its slope at 0, in logit units, is A(b) = 4σ(b)σ(−b) = sech²(b/2). That is about 0.79 at b = 1, 0.42 at b = 2, 0.18 at b = 3 and 0.07 at b = 4 logits.
  - So logit(p̄) ≈ A(b)·Δ for small Δ. Probability averaging attenuates the preference, and a strong position bias can make real preferences look near zero.
  - In probability terms, b = 2 corresponds to the model choosing the first image 88% of the time on identical pairs; b = 3 to 95%.
- **Sign agreement of the two averages.** For any two cells, the sign of ½[logit p₁ + logit p₂] equals the sign of p₁ + p₂ − 1, since p₁p₂ > (1 − p₁)(1 − p₂) if and only if p₁ + p₂ > 1. Log-odds and probability averaging therefore never disagree in direction for a single order swap. They disagree only in magnitude, and potentially in sign across four cells when the contrasts are non-additive.
- **Which space is "exact" depends on the generative model of the bias.**
  - Additive-logit bias (BT order effect, PriDe, CC, BC): averaging log-odds is exact.
  - Guessing-mixture bias (García-Pérez's indecision model), P(choose first) = (1 − u)·σ(Δ) + u·g with guess rate u and first-slot guess bias g: averaging probabilities cancels the bias exactly, giving (1 − u)σ(Δ) + u/2 (linear attenuation by 1 − u), while averaging log-odds does not.
  - The literature's "bias vanishes for large gaps" pattern (MT-Bench, Wang et al., Judging the Judges) is what the mixture predicts when u falls as |Δ| grows.
- **A practical test between the two models.** Plot the per-pair position effect P̂_pair = ¼(c₁ + c₂ − c₃ − c₄) against Δ̂_pair.
  - Additive model: flat.
  - Gap-dependent bias: shrinks with |Δ̂|.
  - Mixture model: the cells saturate in different ways, and the per-pair log-odds gap changes systematically with |Δ̂|.
  
  Pass/fail consistency rates cannot tell the models apart, because under a deterministic additive model a pair is consistent exactly when |Δ| > |b|. Consistency therefore also rises with the gap under the additive model.
- **What the identical-pair estimate represents.** Identical pairs are the zero-gap extreme, where the literature finds bias largest. The identical-pair b is likely an upper-range value for the bias on near-tied real pairs and may overstate the bias on clearly different pairs. A BC-style estimate from real pairs is mean_pairs (c₁ + c₂ − c₃ − c₄)/4. Comparing the two estimates is a cheap test of gap dependence. A model may also treat literally identical images as a special case, for example by wanting to answer "same," which is a further distribution shift.

### Gaps
- I found no 2023-2026 LLM/VLM paper that explicitly derives the attenuation factor sech²(b/2) or contrasts geometric and arithmetic averaging over permutations. The derivations above are mine and should be checked.
- I found no paper that fits the per-pair contrast (c₁ − c₂ + c₃ − c₄) as a non-additivity diagnostic. CalibraEval's constraints imply it, but the paper does not report it per item.

---

## 3. Size of position bias in VLMs with multi-image inputs, scaling, and two-image vs side-by-side presentation

### Takeaway
VLM position bias in two-image comparisons is large for open-source models. In image-quality 2AFC, some pick the same slot 70-80% of the time and keep their answer under an order swap on only 19-45% of pairs, against 82% for GPT-4V. For many-image inputs, open-source VLMs favour later images (recency) while GPT-4o shows a U-shape. The CVPR 2025 analysis attributes this to inter-image causal attention. Larger and stronger models are generally more order-consistent, but no paper shows monotonic scaling, and I found no direct comparison of two separate images against one side-by-side composite.

### Cited Findings
- **2AFC image-quality judging (closest analogue to the project).**
  - Presentation: two separate image inputs with the prompt "This is the first image: <x> This is the second image: <y> Which image has better visual quality?"
  - Consistency κ = (1/|P|) Σ 1[f((x, y)) + f((y, x)) = 1] on binary outputs.
  - Accuracy is computed only on the consistent subset.
  - Coarse-grained κ: IDEFICS-Instruct 0.286, mPLUG-Owl 0.377, XComposer-VL 0.188, Q-Instruct 0.432, GPT-4V 0.823.
  - Slot preferences: IDEFICS-Instruct and mPLUG-Owl choose the "second" image more than 70% of the time; XComposer-VL picks the "first" about 80% of the time.
  - The paper does not say whether answers were read from logits or sampled.
  - Source: [Zhu et al., arXiv 2402.01162](https://arxiv.org/abs/2402.01162)
- **Position-wise QA over 5-20 interleaved images (VQAv2-derived, each set shuffled 4 times).**
  - OpenFlamingo, 10 images: accuracy 51.84% for the leftmost image vs 59.71% for the rightmost. At 20 images: 36.79% vs 50.17%, with early positions near the 34.49% random baseline.
  - Open-source models show recency bias; GPT-4o shows a "typical U-shaped curve," weakest in the middle.
  - Bias grows with the number of images.
  - Shuffling the image order changed predictions about 30% of the time for most open-source models and about 25% for GPT-4o (BLINK).
  - The paper does not analyse model size.
  - Source: [Tian et al., arXiv 2503.13792](https://arxiv.org/abs/2503.13792) [PR: CVPR 2025, [CVF](https://openaccess.thecvf.com/content/CVPR2025/html/Tian_Identifying_and_Mitigating_Position_Bias_of_Multi-image_Vision-Language_Models_CVPR_2025_paper.html)]
- **Mechanism and SoFA mitigation (Tian et al.).**
  - "Inter-image causal attention is the primary source of position bias": later images attend to earlier ones but not the reverse. Isolated or bidirectional masks reduced the bias.
  - SoFA (training-free) interpolates the attention mask, M_soft = (1 − σ)·1_causal + σ·1_bidirectional, applied to inter-image attention every second layer, with σ tuned on a 32-shot validation set.
  - It improved average accuracy by about 2-3%.
  - Source: [Tian et al.](https://arxiv.org/abs/2503.13792)
- **MLLM-as-a-Judge (11 MLLMs, pair comparison).** LLaVA and CogVLM consistently favour answers in a particular position. GPT-4V aligned best with human pairwise preferences. These details come from search-index summaries of the paper, not the full text — [Chen et al., arXiv 2402.04788](https://arxiv.org/abs/2402.04788) [PR: ICML 2024]
- **Scale evidence from text LLMs (no VLM equivalent found).**
  - PriDe RStd: llama 7B/13B/30B/65B = 18.5 / 17.4 / 8.5 / 8.3; llama-2 7B/13B/70B = 23.0 / 7.5 / 4.1. The authors say bias "varies with model families and sizes" with no consistent within-family pattern — [Zheng et al.](https://arxiv.org/abs/2309.03882)
  - CalibraEval default Kappa: Qwen-14B 28.72 vs Qwen-72B 77.47. RewardBench RStd: ChatGPT 16.79 vs Qwen-72B 4.01 — [Li et al.](https://arxiv.org/abs/2410.15393)
  - Judging the Judges (MTBench pairwise PC): GPT-4 0.82, Claude-3.5-Sonnet 0.82, Gemini-1.5-pro 0.62, Gemini-1.0-pro 0.57, Llama-3.1-8B 0.69. Weaker models lose more consistency in list-wise settings — [Shi et al.](https://arxiv.org/abs/2406.07791)
  - Order-sensitivity performance gap of roughly 13% to 85% across benchmarks when MCQ options are reordered (13-75% in arXiv v1) — [Pezeshkpour & Hruschka, Findings NAACL 2024](https://aclanthology.org/2024.findings-naacl.130) [PR]

### Inferences
- **The project's "bias larger than any aesthetic effect" is typical.** It is what the IQA 2AFC literature found for open-source LMMs: 70-80% slot preference corresponds to b ≈ 0.85-1.4 logits on average over pairs, and more on near-tied pairs. GPT-4-class models are the exception.
- **Scale helps only as a tendency.** Within families, larger models are usually more consistent (llama-2 RStd 23.0 → 4.1; Qwen 14B → 72B Kappa 28.7 → 77.5). But the PriDe authors explicitly decline to claim a scaling law, and no VLM study isolates size. Small open VLMs should be assumed to need full counterbalancing.
- **Side-by-side composites (untested reasoning).** Tian et al.'s mechanism suggests a single composite should change the bias rather than remove it. Within one image, patches are encoded together (often by a bidirectional vision encoder), but in the LLM the patch tokens are still serialised in raster order, so left and right halves interleave row by row. That could convert a first/second-image bias into a left/right or label bias of different size. It is untested here and would need its own counterbalancing (left/right × label).
- **Few images, but still causal.** The project's two-image case is the least biased condition in Tian et al.'s count-dependence result, but the causal-attention asymmetry still applies to two images.

### Gaps
- I found no study that directly compares two separate image inputs against one concatenated side-by-side image for pairwise VLM judgements.
- I found no systematic scaling study of VLM position bias within a model family.
- Exact per-model numbers for MLLM-as-a-Judge's position bias were not verified from the paper text. An "88.2%" figure circulating in secondary summaries is unverified and should not be cited.

---

## 4. Reporting preference when bias dominates; information loss and attenuation with sampled binary choices

### Takeaway
The judge literature mostly reports thresholded consistency statistics. Common reports are:
- swap consistency, and the share of pairs biased toward the first or second slot (MT-Bench);
- position consistency and preference fairness (Judging the Judges);
- conflict rate (Wang et al.);
- κ-consistency plus accuracy on consistent pairs only (2AFC-LMMs);
- RStd (PriDe).

The usual decision rules are "win only if consistent in both orders, else tie" (MT-Bench) or "average the scores over both positions" (BPC). I found no 2023-2026 paper with a formal result on how much information is lost when only sampled binary choices are available. Under the additive-logit model, the derivation below shows that both the attenuation of naive frequency averages and the Fisher-information loss scale as sech²(b/2) for weak preferences. At b ≈ 3 logits this means about 5.5 times as many samples for the same precision. Thresholded consistency rules discard all information when |Δ| < |b|.

### Cited Findings
- **MT-Bench position-bias table (consistency / biased toward first / biased toward second):**
  - Claude-v1, default prompt: 23.8 / 75.0 / 0.0%. Rename prompt: 56.2 / 11.2 / 28.7%.
  - GPT-3.5: 46.2 / 50.0 / 1.2%.
  - GPT-4: 65.0 / 30.0 / 5.0%.
  - Few-shot prompting raised consistency for GPT-4 65.0 → 77.5%, Claude-v1 23.8 → 63.7% and GPT-3.5 46.2 → 55.0%.
  - Recommended "conservative approach": swap positions and "only declare a win when an answer is preferred in both orders," otherwise a tie.
  - Source: [Zheng et al.](https://arxiv.org/abs/2306.05685)
- **Wang et al. on calibration and human review.**
  - Under ChatGPT as judge, Vicuna-13B's win rate against ChatGPT was 2.5% when listed first vs 82.5% when listed second. The conflict rate was 66/80 (82.5%).
  - MEC(k = 3) + BPC raised human agreement from 52.7% to 62.5% (κ 0.24 → 0.37) for GPT-4 and from 44.4% to 58.7% (κ 0.06 → 0.31) for ChatGPT.
  - Routing the 20% highest-BPDE items to humans gave 73.8% (GPT-4) against a human-average 71.7%.
  - Source: [Wang et al.](https://arxiv.org/abs/2305.17926)
- **2AFC-LMMs: accuracy only on the consistent subset.** It reports accuracy α only on pairs whose two orders give opposite binary answers (a "conditional preference"). Example: GPT-4V κ 0.823 with α 0.646; XComposer-VL κ 0.188 with α 0.094 — [Zhu et al.](https://arxiv.org/abs/2402.01162)
- **PORTIA consistency gains (relation-based format, original → after PORTIA).** Claude2 28.28 → 83.28%; GPT-3.5 78.12 → 88.59%; GPT-4 93.44 → 97.03%. On average it fixed 62.31% of inconsistent cases. This approach rewrites the content (splitting text answers) and has no direct image analogue — [Li et al., PORTIA](https://arxiv.org/abs/2310.01432)
- **Judging the Judges reports a fixed metric set.** It reports RS (repetition stability over repeated samples) separately from PC and PF. Capable judges have RS > 0.95; Llama-3.1-8B has RS 0.75 ± 0.32. Separating sampling noise from order bias is useful when only sampled replies are available — [Shi et al.](https://arxiv.org/abs/2406.07791)

### Inferences
- **Attenuation of the naive estimator (derivation).** Assume T = 1 sampling from the model's answer distribution, so a reply's frequency estimates the same p that log-probabilities would give exactly, plus binomial noise. The naive estimator logit(mean frequency over orders) converges to logit ½[σ(Δ + b) + σ(Δ − b)] ≈ sech²(b/2)·Δ. It is biased toward 0, and the bias is multiplicative and model-specific. Comparisons of preference strength across models with different b are therefore invalid unless b is modelled.
- **The consistent estimator and its noise.** Δ̂ = ¼ Σ_c logit(p̂_c), with each per-cell frequency transformed before averaging. This is the per-order analysis that Ulrich and Vorberg recommend in psychophysics (Q5). Use an empirical-logit correction such as logit((k + ½)/(n + 1)) so that 0/n and n/n cells stay finite.
- **Fisher information.** Under p = σ(Δ ± b), one binary sample carries information p(1 − p) about Δ. At |Δ| ≪ |b| that is σ(b)σ(−b) instead of ¼ — the same ratio sech²(b/2). The required sample size inflates by cosh²(b/2):
  - ×1.27 at b = 1
  - ×2.4 at b = 2
  - ×5.5 at b = 3
  - ×14.2 at b = 4
  - ×37.6 at b = 5
  
  Information is not lost at every Δ. When |Δ| ≈ |b|, one order sits near p = ½, where information peaks, and the bias acts like a pedestal. The loss is therefore concentrated in exactly the regime the project is in: aesthetic effects much smaller than the bias.
- **Saturation.** With n samples per cell at p = σ(b), the probability that every sample picks the favoured slot is σ(b)ⁿ. For n = 10 that is ≈ 0.28 at b = 2, 0.62 at b = 3 and 0.83 at b = 4. Most per-pair cells then saturate, and per-pair Δ is unidentified without pooling. The remedy is a pooled model:
  logit P(choose R) = Δ_pair + s_pos·β_P + s_lab·β_L,
  with β shared across pairs (per model) and Δ_pair as random effects or shrunk. This is exactly Davidson-Beaver Bradley-Terry with an order effect, plus a label term. In Thurstone form for aggregation over items, Φ(q_i − q_j + β·s) extends the 2AFC-LMMs MAP objective.
- **How to report.** Log-odds Δ̂ with intervals should be the primary estimate. Alongside it:
  - b̂_position and b̂_label, in logits and as P(first | identical pair);
  - swap consistency or flip rate (the fraction of pairs whose argmax changes with order);
  - the non-additivity contrast from Q2.
- **Problems with threshold summaries.**
  - Under a deterministic additive model a pair is consistent if and only if |Δ| > |b|. The consistency rate is then just P(|Δ| > |b|) — a function of the bias, not of preference.
  - The MT-Bench rule (inconsistent → tie) turns every pair with |Δ| < |b| into a tie, so it carries zero information in the bias-dominated regime.
  - "Conditional preference" on the consistent subset (2AFC-LMMs' α) is selection on |Δ| > |b|. It overstates the typical preference magnitude and depends on b.
  - These metrics are useful as diagnostics, not as the preference estimate.

### Gaps
- I found no 2023-2026 paper giving a formal efficiency or attenuation result for sampled binary LLM choices under position bias. The sech²(b/2) and cosh²(b/2) results above are my derivation under the additive-logit model and should be checked by the report writer or a statistician.
- The project's brief assigns logprob-vs-sampling estimation theory to another researcher, so I did not search that literature.

---

## 5. Human 2AFC order effects (time-order error, interval and position bias) and the corrections LLM work borrows

### Takeaway
Psychophysics has long shown that 2AFC is not bias-free. Interval and time-order effects are strong and common. The standard corrections are:
- counterbalance the order;
- fit a separate psychometric function per order instead of pooling proportions (Ulrich & Vorberg 2009);
- model order as an additive parameter on the latent difference scale (the Bradley-Terry/Thurstone order effect, Davidson & Beaver 1977);
- in some accounts, model bias as guessing under indecision and allow a "can't tell" response (García-Pérez & Alcalá-Quintana).

LLM debiasing has rediscovered the first and third without citing them.

### Cited Findings
- **Bias in two-interval forced choice.** Yeshurun, Carrasco and Maloney (2008) tested four common claims about 2-IFC. They found "little support" that 2-IFC is unbiased or that its structure leaves sensitivity unchanged, and rejected the claimed √2 sensitivity advantage over yes-no under the difference model. An addendum appeared in 2012 (*Vision Research* 70) — [Haifa CRIS record, *Vision Research* 48:1837-1851](https://cris.haifa.ac.il/en/publications/bias-and-sensitivity-in-two-interval-forced-choice-procedures-tes/)
- **Per-order fitting.** Ulrich and Vorberg (2009) fit separate psychometric functions for each order of standard and test stimuli, which removes order effects from difference-limen estimates. They also argued for constraining the 2AFC function's 50% point to the standard — [doi 10.3758/APP.71.6.1219](https://doi.org/10.3758/APP.71.6.1219). Alcalá-Quintana and García-Pérez (2011) contest that this constraint holds for all 2AFC tasks and propose a generalisation — [Frontiers in Psychology 2011](https://www.frontiersin.org/articles/10.3389/fpsyg.2011.00096/pdf). These summaries come from citing papers and abstracts, not the 2009 full text.
- **Interval bias and the indecision model.** Interval bias in 2AFC detection is strong and common, and it contradicts the standard difference model. A "difference model with indecision/guessing" fits as well as alternatives but yields different sensory estimates. The authors recommend a response format that lets observers express indecision — [UCM record of García-Pérez & Alcalá-Quintana 2011, *Atten. Percept. Psychophys.*](https://docta.ucm.es/entities/publication/ab29d99b-ee36-4c49-9d3c-0efa968489e2/full)
- **A formal model of the time-order error.** Alcalá-Quintana and García-Pérez (2011, *Quarterly Journal of Experimental Psychology*) derive a time-order-error model for contrast discrimination. In it, sensory factors (temporary desensitisation) and procedural factors (short inter-stimulus or inter-trial intervals, response bias) make performance depend on presentation order despite a single underlying mechanism — [UCM repository](https://docta.ucm.es/entities/publication/ab29d99b-ee36-4c49-9d3c-0efa968489e2/full) (abstract-level)
- **The paired-comparison order effect.** Davidson-Beaver order effect: P(i beats j) = exp(λ_i) / (exp(λ_i) + exp(λ_j + γ)), multiplicative on odds and additive on log-odds — [Davidson & Beaver 1977 record](https://scilit.com/publications/94078d32740ff4e1fc2839085db1ed84); [arXiv 2101.11227](https://arxiv.org/abs/2101.11227); [arXiv 2505.24783](https://arxiv.org/abs/2505.24783)

### Inferences
- **The mapping from psychophysics to LLM practice:**
  - Order counterbalancing → swap or cyclic permutation (MT-Bench, PriDe, BPC).
  - Davidson-Beaver γ → PriDe, CC and BC priors (additive log-odds).
  - Per-order psychometric fits (Ulrich & Vorberg) → averaging logits per cell rather than pooling choice proportions.
  - The indecision/guessing model → the empirical "bias vanishes when the gap is large" finding, and to tie options in judge prompts (MT-Bench [[C]], PORTIA).
- **The signal-detection analogue of probability-averaging attenuation.** This is a standard textbook relation, not retrieved in this session. With an unbiased difference rule, proportion correct is Φ(d′/√2). With a criterion shift c it becomes ½[Φ(d′/√2 − c) + Φ(d′/√2 + c)] < Φ(d′/√2). Pooling proportions over orders understates sensitivity, while z-transforming per order and then averaging recovers d′. That is the probit counterpart of the logit result in Q4.
- **Allowing a "can't tell / same" response.** The García-Pérez recommendation would, for a VLM, separate guessing-driven slot bias from real preference. It changes the estimand, though, and is not a drop-in replacement for forced choice.

### Gaps
- I did not retrieve Hellström's time-order-error reviews (e.g., the 1985 *Psychological Bulletin* review, and the sensation-weighting model) or Macmillan & Creelman's SDT treatment. The level-dependent TOE and SDT formulas above are from background knowledge and are labelled as inferences.
- I did not retrieve consumer or sensory-science work on left/right position preference in human 2AFC (e.g., sensory evaluation panels). Its effect sizes are therefore not reported here.
- I found no LLM/VLM paper that explicitly cites Davidson-Beaver, Ulrich-Vorberg or García-Pérez when proposing a position-debiasing method. The borrowing is conceptual, not documented.
