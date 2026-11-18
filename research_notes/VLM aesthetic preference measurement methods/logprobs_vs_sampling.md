# Log-probability vs sampled-answer readouts of LLM/VLM forced choices

Scope: how first-token log-probabilities of answer letters relate to sampled or free-text answers; what temperature-1 sampling estimates on hosted APIs; calibration of instruction-tuned models; small-sample estimation from k = 1-3 Bernoulli replies; and ways to recover graded preferences comparable to human choice proportions. Position-bias debiasing, aesthetics benchmarks and psychometric frameworks are out of scope here.

Notation used throughout. For one presentation j of a pair, the local readout gives letter log-probs l_A, l_B after the prefilled "Answer:". The two-way normalised probability is p_j = exp(l_X) / (exp(l_A) + exp(l_B)) for the option X mapped to a fixed stimulus, and its log-odds is z_j = l_X - l_Y. The hosted readout gives c_j of k_j sampled replies choosing X. The project's smoothed log-prob log((c+1/2)/(k+1)) is the log posterior mean under a Jeffreys Beta(1/2, 1/2) prior. The implied per-presentation log-odds is L_j = log((c+1/2)/(k-c+1/2)), the Haldane-Anscombe "empirical logit". Pair score = mean over the 4 counterbalanced presentations; choice = sign, with ties counted as 1/2.

Peer-review status is marked [PR] for peer-reviewed, [preprint], [tech report / blog] or [docs].

## Q1. Do first-token log-probabilities of answer letters match the distribution of sampled or free-text answers?

### Takeaway
Not reliably for instruction-tuned/chat models. Between the answer picked by first-token probability and the answer actually written in the text, mismatch rates range from about 9% to over 60%. They are worst for small, heavily safety-tuned chat models and for opinion-type questions (no correct answer), which is the regime of aesthetic preference. Constraining the format ("start with a single letter", an "Answer:" prefix) reduces the mismatch but does not remove it. When mismatch is high, the text answers are the more robust readout.

### Cited Findings
- [PR, Findings of ACL 2024] Wang et al., "My Answer is C". They define the mismatch rate as "the ratio of cases where the answer chosen by the first-token evaluation differs from the choice in the text output", averaged over 10 option-order shuffles, across six instruction-tuned models (Llama2-Chat 7/13/70B, Mistral-7B-Instruct v0.1/v0.2, Mixtral-8x7B-Instruct). The abstract reports first-token and text evaluation "severely misaligned on all dimensions, reaching mismatch rates over 60%" — [arXiv 2402.14499](https://arxiv.org/abs/2402.14499); [ACL Anthology](https://preview.aclanthology.org/setup/2024.findings-acl.441)
- Same paper, concrete numbers. On OpinionQA (opinion questions with no correct answer), the mismatch is 66.2% for Llama2-7b-Chat and 13.3% for Llama2-70b-Chat. On MMLU (zero-shot, middle constraint) it is: Mistral-7B v0.1 15.1%, v0.2 10.2%, Mixtral 9.0%, Llama2-7B 51.4%, Llama2-13B 35.3%, Llama2-70B 13.2% — [arXiv HTML v2](https://arxiv.org/html/2402.14499v2)
- Same paper, prompt constraint. Mismatch "decreases as we increase the constraint level from Low to High for all models except Mistral-7b-Instruct-v0.2". "High" asks the model to "start your answer with a single letter". An in-prompt example ending in "Answer: C" increased mismatch in 5 of 6 models: Llama2-70b-Chat's first token picked "C" ~85% of the time, versus 32.1% under the High constraint — [arXiv HTML v2](https://arxiv.org/html/2402.14499v2)
- Same paper, causes. Refusals are "an important factor", but "there is still a considerable amount of mismatch due to non-safety reasons". Llama2-7b-Chat refused 51.4% of the time, and Llama2 refusals fell from >50% to <10% from 7B to 70B. The authors "caution against relying solely on first-token evaluation" and recommend inspecting text outputs — [arXiv HTML v2](https://arxiv.org/html/2402.14499v2)
- [PR, COLM 2024] Wang, Hu, Ma, Röttger, Plank, "Look at the Text". When first-token and text answers mismatch, "the text answers are more robust to question perturbations than the first token probabilities", and the advantage grows with the mismatch rate. Above 50% mismatch, text answers are more robust to option-order changes than first-token probabilities debiased with PriDe — [arXiv 2404.08382](https://arxiv.org/abs/2404.08382)
- [PR, EMNLP 2023] Hu & Levy, "Prompting is not a substitute for probability measurements in large language models". Metalinguistic/prompted judgments were less accurate than quantities read directly from model probabilities, and agreement between the two worsened as the prompt departed from a direct next-word measurement. Not re-fetched in this pass — [arXiv 2305.13264](https://arxiv.org/abs/2305.13264)
- [preprint] Lyu, Wu & Aji (2024), "Beyond Probabilities: Unveiling the Misalignment in Evaluating LLMs". Probability-based MCQ evaluation is misaligned with generation-based predictions. Not re-fetched in this pass — [arXiv 2402.13887](https://arxiv.org/abs/2402.13887)
- [PR, NeurIPS 2024] Dominguez-Olmedo, Hardt & Mendler-Dünner evaluated 43 models on American Community Survey items with standard prompting. Responses "are governed by ordering and labeling biases, for example, towards survey responses labeled with the letter 'A'". A-bias shrinks slowly with size. Response entropy "tends to increase log-linearly with model size, independent of the question asked". After adjusting for the biases, models trend toward uniformly random answers, with "consistently higher entropy than any human population" — [arXiv 2306.07951](https://arxiv.org/abs/2306.07951); [NeurIPS proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/515c62809e0a29729d7eec26e2916fc0-Abstract.html)

### Inferences
- The local readout (assistant turn prefilled with "Answer:", read letter log-probs) is roughly the "High constraint / forced start" condition of Wang et al. The hosted readout (free reply up to 16 tokens, parsed) is the "text answer" condition. The literature shows these two can differ systematically for the same model, so local vs hosted differences confound model with readout. Aesthetic 2AFC has no correct answer, which makes it closest to OpinionQA, where the measured mismatch was largest (13-66%).
- For T = 1 sampling, the parsed-answer distribution equals the first-token letter distribution only if the reply's first generated token is the letter. With free replies ("Image A", "**A**", "I prefer…") the sampled distribution is a marginal over whole sequences, not the letter softmax at a fixed position.
- The gap can be measured directly on the local models. For a subset of presentations, draw n ≈ 20-50 free T = 1 replies using the exact hosted prompt (no "Answer:" prefill), and compare the parsed proportion with p_j from log-probs. This is the only way to know the gap for these particular VLMs; nothing in the literature transfers a number to Gemma 4 or Nemotron.
- Dominguez-Olmedo et al. found that counterbalanced, bias-adjusted LLM answers drift toward uniform. This suggests that weak aesthetic preferences averaged over 4 counterbalanced presentations may sit near 0.5 for reasons unrelated to the stimuli. Any comparison to human proportions should check for this "entropy" artefact.

### Gaps
- No study found that measures first-token vs text-answer mismatch for VLMs with image pairs, or specifically for 2AFC preference prompts. All figures above are text-only LLMs, mostly the Llama2/Mistral generation (2023-24).
- No published mismatch numbers for Gemma 4 or Nemotron-family models were found.

## Q2. What does temperature-1 sampling estimate, and what do top_p, top_k, seeds and server-side defaults change? How deterministic are hosted APIs?

### Takeaway
At T = 1 with no truncation, independent samples are draws from the server's actual next-token distribution. The parsed proportion is then an unbiased estimate of the model's text-answer probability: the same quantity a log-prob readout would give at the same position, plus Bernoulli noise. That holds only if the server really applies T = 1, top_p = 1 and no top_k or penalties. Hosting stacks have model-specific defaults (Gemma 4 on NVIDIA: temperature 1.0, top_p 0.95, top_k 64 "recommended"), and inference backends differ even under greedy decoding. Hosted inference is not bit-deterministic even at T = 0. Seeds are at best "best effort".

### Cited Findings
- Standard sampling algebra (no single paper needed). Sampling at temperature T draws from softmax(z/T). For a two-token choice, logit_T = (z_A - z_B)/T, so the log-odds scale by 1/T and T = 1 reproduces the log-prob readout's probabilities. Meister et al. read log-probs "at temperature 1.0" and also report temperature-scaled log-probs, with τ chosen per dataset by minimising TV distance to the human ground truth (oracle) — [Meister et al., arXiv 2411.05403](https://arxiv.org/html/2411.05403v1)
- [docs] For Gemma 4 31B IT, NVIDIA's API reference recommends using "the partner-recommended sampling configuration of `temperature=1.0`, `top_p=0.95`, and `top_k=64` across use cases". The page does not document request defaults, seed behaviour, or logprob support — [NVIDIA API reference, Gemma 4 31B IT](https://docs.api.nvidia.com/nim/reference/google-gemma-4-31b-it). Unsloth's guide also recommends Google's default Gemma 4 parameters, with the same values — [Unsloth Gemma 4 docs](https://unsloth.ai/docs/models/gemma-4)
- [docs] NVIDIA NIM for LLMs 1.14.0 added `top_k` as a top-level request field and deprecated the `nvext` copy — [NIM 1.14.0 release notes](https://docs.nvidia.com/nim/large-language-models/1.14.0/release-notes.html). In the NIM 3.0.0 API reference, the Dynamo frontend coerces `n=null` and `top_k=0` to defaults rather than rejecting them. `top_logprobs=n` "can return n+1 alternatives", which it calls "inherited vLLM behaviour" — [NIM 3.0.0 API reference](https://docs.nvidia.com/nim/large-language-models/3.0.0/reference/api-reference.html)
- [docs] vLLM (v0.6.6-0.7.2 docs): the generation config "is set to None by default" for backward compatibility. Setting it to "auto" loads the model's `generation_config.json` defaults into the sampling parameters — [vLLM docs, default generation config](https://docs.vllm.ai/en/v0.6.6/getting_started/examples/offline_inference_with_default_generation_config.html); [vLLM PR 11164](https://github.com/vllm-project/vllm/pull/11164). The older SamplingParams signature has `top_k = -1` (no top-k) when unset — [vLLM sampling params](https://docs.vllm.ai/en/v0.6.0/dev/sampling_params.html)
- [preprint, Aug 2026] Masoudian et al., "What We Observe as LLM Behavior Can Be a Side-effect of Inference Backend". Switching backend (HF, vLLM, Ollama) can "significantly alter" results even under greedy decoding. About "roughly 39%" of out-of-the-box variability comes from the backend; the rest comes from sampling noise and differing default generation parameters. The authors recommend disclosing backend, version and full generation config — [arXiv 2608.04714](https://arxiv.org/abs/2608.04714)
- [blog, Thinking Machines, 2025] "Defeating Nondeterminism in LLM Inference" ran 1,000 temperature-0 completions on Qwen3-235B-A22B-Instruct-2507 and got 80 unique outputs (most common: 78). All runs matched for 102 tokens. At token 103, 992 continued "Queens, New York" and 8 "New York City". With batch-invariant kernels all 1,000 were identical. Root cause: kernels are not batch-invariant and "the load (and thus batch-size) nondeterministically varies". LLM APIs "are still not deterministic in practice", and self-hosted vLLM/SGLang sampling "still isn't deterministic" — [Thinking Machines blog](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)
- [preprint; workshop follow-up] Atil et al., "Non-Determinism of 'Deterministic' LLM Settings". Across deterministically configured LLMs (temperature 0) on 8 tasks with repeated identical runs, accuracy varied by up to 10%. Variation was not normally distributed, and "no LLM consistently delivers repeatable accuracy across all tasks". A follow-up at the Eval4NLP 2025 workshop extends this to cloud-hosted APIs — [arXiv 2408.04667](https://arxiv.org/abs/2408.04667); [Eval4NLP 2025](https://preview.aclanthology.org/ingest-ijcnlp-aacl/2025.eval4nlp-1.12.pdf)
- [docs] OpenAI's seed parameter gives "mostly" reproducible outputs on a best-effort basis. Changes to `system_fingerprint` signal backend changes that can alter outputs. Not re-fetched in this pass — [OpenAI Cookbook: reproducible outputs with seed](https://cookbook.openai.com/examples/reproducible_outputs_with_the_seed_parameter)

### Inferences
- **What T = 1, top_p = 1 sampling estimates.** If the request settings are honoured and there is no hidden top_k, penalties or injected system prompt, then E[c/k] = π_text(X), the model's probability of a reply that parses as X under the hosted serving stack. That is the "text answer" probability in Q1, not the letter softmax after "Answer:".
- **Effect of truncation.** top_k = 64 almost never matters for a two-letter choice: both letters are in the top 64, and renormalisation keeps P(A)/P(B) unchanged at that position. top_p < 1 does matter. Under top_p = 0.95, a minority option with probability below about 0.05 is removed entirely, so sampled proportions become more extreme than the softmax. If the server silently applied Gemma's recommended top_p = 0.95, every pair with p < 0.05 or p > 0.95 would always return unanimous counts. The project's explicit top_p = 1 guards against this only if the endpoint honours it. A cheap check: count presentations where p_j from a local Gemma-family log-prob readout lies in (0.01, 0.05) but hosted replies never show the minority letter across many draws.
- **Seeds.** If a fixed `seed` is sent and the server honours it, the "3 passes" can return identical replies, so k collapses to 1 effective sample. Send no seed, or a distinct seed per pass. Diagnostic: under independence, P(all 3 agree) = p³ + (1-p)³, which is ≥ 0.25 and equals 0.25 at p = 0.5. Unanimity much above what the per-presentation proportions imply suggests correlated passes. Batch-dependent numerical non-determinism (Thinking Machines; Atil et al.) only perturbs logits slightly. At T = 1 it adds negligible variance relative to Bernoulli noise, but it means hosted results are not exactly reproducible run to run.
- **Truncated or unparseable replies.** With max 16 tokens, a model that opens with preamble or reasoning text may be truncated before naming a letter. Such replies are missing data that may be informative (e.g., more likely on hard or near-tie pairs). They should be counted and reported, not dropped silently.

### Gaps
- No NVIDIA documentation states what the hosted free endpoints apply when a request omits `top_k`, or whether they honour `top_p = 1` exactly for Gemma 4 31B or Nemotron 3.5 Super VL. Whether hosted logprobs are available per model is also undocumented. The NIM reference documents `top_logprobs` generally, so per-model availability may be worth one re-check.
- Whether recent vLLM versions default to `generation_config = "auto"` could not be confirmed. Masoudian et al. reportedly state that vLLM 0.8.5 ignored generation_config, per a search snippet not verified in the paper body.
- No source quantifies how batch non-determinism changes T = 1 sampling distributions; the "negligible" claim above is an inference.

## Q3. Calibration of instruction-tuned / RLHF models: are answer probabilities overconfident, and what does that mean for preference strength vs direction?

### Takeaway
Pre-trained models' token probabilities on multiple-choice questions are fairly well calibrated. RLHF or instruction tuning "polarizes" answer distributions, piling mass on one option regardless of true uncertainty. Direction and ranking still carry signal, but magnitudes overstate certainty. Verbalised probabilities are often better calibrated for RLHF models (about 50% relative ECE reduction), though not always. Sampling at T = 1 inherits the same polarisation, so both readouts overstate strength relative to human proportions.

### Cited Findings
- [preprint, 2022] Kadavath et al., "Language Models (Mostly) Know What They Know": larger models "are well-calibrated on diverse multiple choice and true/false questions when they are provided in the right format" — [arXiv 2207.05221](https://arxiv.org/abs/2207.05221)
- [tech report] GPT-4 Technical Report, Figure 8 and surrounding text. The pre-trained model is highly calibrated on an MMLU subset (confidence matches accuracy), but "after the post-training process, the calibration is reduced" — [arXiv 2303.08774](https://arxiv.org/abs/2303.08774). Exact ECE values could not be read in this pass; see Gaps.
- [PR, NeurIPS 2024] Cruz, Hardt & Mendler-Dünner, "Evaluating language models as risk scores" (17 LLMs, 5 tasks). Zero-shot multiple-choice risk scores "have high predictive signal but are widely miscalibrated". Base models "consistently overestimate outcome uncertainty", while instruction-tuned models "underestimate uncertainty and produce over-confident risk scores". Instruction tuning "polarizes answer distribution regardless of true underlying data uncertainty". Verbalised (chat-style) risk queries gave "substantially improved calibration across instruction-tuned models" — [arXiv 2407.14614](https://arxiv.org/abs/2407.14614)
- [PR, EMNLP 2023] Tian et al., "Just Ask for Calibration". For RLHF models (ChatGPT, GPT-4, Claude) on TriviaQA, SciQ and TruthfulQA, "verbalized confidences emitted as output tokens" are typically better calibrated than conditional probabilities, "often reducing the expected calibration error by a relative 50%" — [arXiv 2305.14975](https://arxiv.org/abs/2305.14975)
- [PR, ICLR 2024] Xiong et al., "Can LLMs Express Their Uncertainty?": when verbalising confidence, LLMs "tend to be overconfident, potentially imitating human patterns of expressing confidence". Not re-fetched in this pass — [arXiv 2306.13063](https://arxiv.org/abs/2306.13063)
- [preprint 2024] Meister, Guestrin & Hashimoto. Log-probabilities "systematically underestimate" distributional alignment and score worse than a uniform baseline. Average TV distance: GPT-3.5-Turbo 0.455, Llama 3 70B 0.495, GPT-4 0.550, versus uniform 0.363. The authors attribute this to probability mass concentrated on one or two options, "especially in models trained with Reinforcement Learning from Human Feedback". Oracle temperature scaling helps GPT-4 (0.273) and GPT-3.5 (0.296) but not Llama 3 70B (0.469) — [arXiv 2411.05403](https://arxiv.org/html/2411.05403v1)
- [PR, ICML 2023] Santurkar et al., "Whose Opinions Do Language Models Reflect?" (OpinionQA, 60 US groups). RLHF-tuned models tend to express the dominant viewpoint of certain groups rather than the spread of opinion, and human-feedback tuning "seems to only amplify" the misalignment — [PMLR 202](https://proceedings.mlr.press/v202/santurkar23a.html); [arXiv 2303.17548](https://arxiv.org/abs/2303.17548)
- [PR, AAAI 2025] Lyu et al., "Calibrating LLMs with Sample Consistency" (11 models, 9 reasoning datasets). Consistency-based confidence from multiple samples (agreement, entropy, first-second distance) outperforms existing post-hoc calibration. "Scaling model size enhances calibration, whereas instruction-tuning has a negative effect" — [arXiv 2402.13904](https://arxiv.org/html/2402.13904v1)
- [preprint 2025; listed as ICML 2026 poster] Zhang et al., "Verbalized Sampling". Mode collapse after alignment is driven partly by typicality bias in preference data, with typicality-bias rates of 54-62% across OpenAI TL;DR, UltraFeedback, HelpSteer-v2 and Skywork. Asking for several candidates with probabilities raised creative-writing diversity 1.6-2.1× and recovered 66.8% of base-model diversity after DPO, versus 23.8% for direct prompting — [arXiv 2510.01171](https://arxiv.org/abs/2510.01171v3); [ICML 2026 listing](https://icml.cc/virtual/2026/poster/60489)

### Inferences
- **Direction vs strength.** Cruz et al.'s pattern (high predictive signal, poor calibration) suggests the sign and rank order of an instruction-tuned VLM's pair log-odds may still track human majorities. The magnitudes, in nats, should not be read as preference strength on a human scale. Comparing |z| from a local RLHF model with human log-odds logit(q) will show "overconfidence" by construction.
- **Sampling does not fix calibration.** At T = 1, sampled proportions estimate the same polarised distribution. If p_j = 0.99, three samples are unanimous 97% of the time. The sampled readout looks less extreme only because its estimator is capped at ±log(2k+1) (see Q4), not because it is better calibrated.
- **Calibrating to humans.** Fit one temperature/slope, logit(q_ij) ≈ a + b·ẑ_ij, on dev stimuli only (no tuning on test). This maps model log-odds onto the human scale; it is Meister's temperature scaling without the oracle. A fitted slope b well below 1 quantifies overconfidence and is itself a reportable result. Fit it separately per model and per readout type.

### Gaps
- The GPT-4 report's Figure 8 ECE values (commonly quoted as about 0.007 pre-training vs 0.074 post-training) could not be verified: the PDF did not render in this pass.
- Kadavath et al.'s reported finding that an RLHF policy can be recalibrated by temperature (about T = 2.5) is recalled from the paper body and was not re-verified.
- No calibration study of VLM answer probabilities on preference or opinion tasks with images was found. All evidence is from text LLMs on factual QA, risk scores or surveys.

## Q4. Statistics: estimating a probability or log-odds from k = 1-3 Bernoulli samples; bias of sign/majority statistics; samples needed to match a log-prob readout

### Takeaway
With k ≤ 3 per presentation, any per-presentation estimate is very coarse. The project's empirical logit L = log((c+½)/(k-c+½)) is capped at ±log(2k+1) (±1.10, ±1.61, ±1.95 nats for k = 1, 2, 3) and strongly biased toward 0 for p beyond about 0.7. The Haldane-Anscombe ½ correction only removes first-order bias asymptotically. The sign/majority "choice" statistic is a nonlinear amplifier: its expectation is g_k(p), not p. A deterministic log-prob readout has zero sampling variance. Matching ±0.05 precision on p at p = 0.5 needs about 100 independent samples. Pooling across presentations and pairs (beta-binomial or mixed logistic models) is the principled fix.

### Cited Findings
- [PR, Statistical Science 2001] Brown, Cai & DasGupta, "Interval Estimation for a Binomial Proportion". The Wald interval's coverage is erratic and poor even at moderate n. They recommend the Wilson or Jeffreys interval for small n (n ≤ 40) and Agresti-Coull for larger n. The Jeffreys interval uses quantiles of the Beta(x+½, n-x+½) posterior, whose mean (x+½)/(n+1) is the project's smoothed probability. Not re-fetched in this pass — [doi:10.1214/ss/1009213286](https://doi.org/10.1214/ss/1009213286)
- [PR, The American Statistician 1998] Agresti & Coull, "Approximate is better than 'exact'". Adding 2 successes and 2 failures (for 95%) gives an interval with better coverage than Wald and less conservatism than Clopper-Pearson. Not re-fetched in this pass — [doi:10.1080/00031305.1998.10480550](https://doi.org/10.1080/00031305.1998.10480550)
- [PR, Biometrika 1967] Gart & Zweifel compared the small-sample bias of logit estimators and their variance estimators: Berkson's, Haldane's (1955) and Anscombe's (1956) +½ correction, Tukey's and Hitchcock's — [PubMed 6049534](https://pubmed.ncbi.nlm.nih.gov/6049534/)
- Later work on the +½ correction. A CRiSM working paper notes that the Haldane-Anscombe adjustment adds a = ½ to the response and 2a to the total, that the bias depends on the parameter values, and that "there cannot be a universal constant a which always eliminates the first-order bias" (in its regression setting) — [Warwick CRiSM 09-36](https://warwick.ac.uk/fac/sci/statistics/crism/papers/paper09-36/09-36w.pdf). A search snippet attributes to Gart, Pettigrew & Thomas (Biometrika 1985) the finding that neither the +½ correction nor Cox's -½ is "universally effective" in reducing bias. The underlying page was not opened, so treat this as unverified.
- [PR, EMNLP 2025 Findings] Wang, Zhang & Choi, "Improving LLM-as-a-Judge Inference with the Judgment Distribution". Taking the mean of the judge's judgment-token distribution "consistently outperforms taking the mode" (greedy) across pointwise, pairwise and listwise settings. Chain-of-thought can collapse the spread of the judgment distribution, which often hurts — [arXiv 2503.03064](https://arxiv.org/abs/2503.03064)
- [PR, EMNLP 2024] Liusie, Raina, Fathullah & Gales, "Efficient LLM Comparative Assessment: a Product of Experts Framework". It keeps soft pairwise probabilities p_ij = P_lm(z_i ≻ z_j) instead of win/loss and combines them as Gaussian or soft Bradley-Terry "experts". This significantly improves comparative assessment, especially when only a subset of comparisons is made — [arXiv 2405.05894](https://arxiv.org/abs/2405.05894); [ACL Anthology](https://aclanthology.org/2024.emnlp-main.389.pdf)

### Inferences
These are exact calculations by the note-writer (script at `C:\Users\USER\AppData\Local\Temp\claude\4d3b911dca749cf7\0a23886b-f5b4-48ac-b66b-d9a69105dba3\scratchpad\sign_stats.py`). They assume the same true p in all 4 presentations and independent replies.

- **Ceiling.** |L| ≤ log(2k+1): 1.099 (k=1), 1.609 (k=2), 1.946 (k=3) nats. A log-prob readout from an RLHF model can produce |z| of 5-15 nats. Mean log-odds from the two readouts are therefore on different scales and should not be pooled or compared as magnitudes.
- **Bias of E[L] relative to the true logit(p).** k=1 gives E[L] = (2p-1)·log 3, which is linear in p, not logistic.

  | p | logit(p) | E[L], k=1 | E[L], k=2 | E[L], k=3 |
  |---|---|---|---|---|
  | 0.55 | 0.201 | 0.110 | 0.161 | 0.184 |
  | 0.60 | 0.405 | 0.220 | 0.322 | 0.369 |
  | 0.70 | 0.847 | 0.439 | 0.644 | 0.744 |
  | 0.80 | 1.386 | 0.659 | 0.966 | 1.128 |
  | 0.90 | 2.197 | 0.879 | 1.288 | 1.527 |
  | 0.99 | 4.595 | 1.077 | 1.577 | 1.903 |

  The ½ correction makes L finite and nearly unbiased only for p near 0.5 at k=3. For strong preferences it attenuates heavily.
- **SD of the pair score** (mean of 4 L) at p = 0.5: 0.55 (k=1), 0.57 (k=2), 0.53 (k=3) nats. This is the same order as the bias-corrected signal for p ≤ 0.7, so single-pair strength estimates are mostly noise.
- **The sign "choice" amplifies.** E[choice] = g_k(p) = P(Σ L > 0) + ½·P(Σ L = 0):

  | p | k=1 | k=2 | k=3 |
  |---|---|---|---|
  | 0.55 | 0.575 | 0.608 | 0.633 |
  | 0.60 | 0.648 | 0.710 | 0.753 |
  | 0.70 | 0.784 | 0.874 | 0.922 |
  | 0.80 | 0.896 | 0.967 | 0.988 |
  | 0.90 | 0.972 | 0.997 | 1.000 |

  For k=1, g_1(p) = 3p² - 2p³ exactly: with ties at ½, a majority of 4 equals a majority of 3. Ties are common. At p = 0.5, P(tie) is 0.375 (k=1), 0.273 (k=2) and 0.173 (k=3).
- **Consequence for comparability.** For the same underlying model with p = 0.6 in every presentation:
  - The log-prob sign readout returns "X" with certainty.
  - The hosted readout returns "X" only 65-75% of the time (in expectation).
  - Human proportions would show q ≈ 0.6, if the model were calibrated to humans.

  So "% of pairs where the model chooses the human-preferred image" is not comparable across readouts. Sampled readouts are diluted toward 50% on weak-preference pairs, and log-prob sign readouts are a step function. Neither choice rate is comparable to the human choice proportion, which estimates p itself.
- **Aggregation interacts with position effects differently.** If the per-presentation p varies (e.g., 0.9 in one order and 0.3 in the other), the log-prob mean of logits is (2.197 - 0.847)/2 = +0.675. The k=3 sampled readout's expectation is about (1.527 - 0.744)/2 = +0.39. One extreme presentation (e.g., z = +10 from a strong letter bias) can outvote three moderate ones under log-probs, but not under capped sampled logits. Averaging probabilities instead of logits across presentations treats the two readouts alike.
- **Samples needed versus a log-prob readout.** The log-prob readout of p has no sampling variance; only the run-to-run numerical noise in Q2 remains. For sampled estimates, with n = total replies per pair (n = 4k ≤ 12 here):
  - SE(p̂) = √(p(1-p)/n). At p = 0.5, SE ≤ 0.10 needs n = 25, ≤ 0.05 needs n = 100, and ≤ 0.025 needs n = 400.
  - On the logit scale (delta method), SE(logit p̂) ≈ 1/√(n·p(1-p)). SE 0.5 needs n = 16 at p = 0.5 and n = 25 at p = 0.8. SE 0.25 needs 64 and 100. SE 0.1 needs 400 and 625.
  - At n = 12, SE(p̂) at p = 0.5 is 0.144, roughly the sampling noise of a human proportion from about 12 raters.
- **Better estimators for k ≤ 3.**
  - **(a) Pool on the probability scale.** Per pair, p̂ = C/K, where C and K are totals over all presentations and passes. Use the Jeffreys posterior Beta(C+½, K-C+½) for intervals. This is unbiased for the mean choice probability over counterbalanced presentations, the same estimand as a human choice proportion from counterbalanced trials.
  - **(b) Beta-binomial empirical Bayes.** Fit Beta(α, β) across pairs, then use the posterior mean (C+α)/(K+α+β). This shrinks noisy pairs toward the population mean and has lower MSE than Jeffreys when K is tiny.
  - **(c) Mixed logistic model (GLMM)** for the individual replies: logit P(y = X) = β_pair + γ·order + δ·letter, with β_pair ~ N(μ, τ²). This uses every reply, absorbs position and letter effects as fixed effects, and returns shrunken pair log-odds on the same latent scale as log-prob z. Most importantly, it estimates τ, the spread of true preference log-odds across pairs. τ is identifiable even when no single pair's strength is, and can be compared with the SD of local-model z and with the SD of human logit(q) (after correcting for binomial noise).
- **Varying k.** If k varies across presentations (passes failed, rate limits), presentations carry different caps and weights in a mean of L. If k depends on the replies themselves (e.g., stopping when unanimous), the estimator is biased unless the stopping rule is modelled. (a) and (c) handle variable k naturally when the missingness is unrelated to the answer.

### Gaps
- No source was found that analyses the sign-of-mean-empirical-logit statistic specifically; the g_k(p) values above are the note-writer's own exact computations.
- No paper was found that reports how many i.i.d. T = 1 samples are needed to reproduce an LLM's log-prob readout empirically. The precision figures follow from binomial theory and assume the sampled and first-token distributions coincide, which Q1 shows may not hold.

## Q5. Methods that recover graded preferences from sampled answers, and what "silicon sample" / distributional-alignment work concludes about comparing model and human choice proportions

### Takeaway
Graded information comes from: probability-weighted readouts (mean of the judgment distribution, soft pairwise probabilities); many i.i.d. samples; consistency measures; and asking the model to verbalise a probability or a distribution. Verbalised distributions matched human opinion distributions better than log-probs or sampled sequences (TV ≈ 0.23 vs 0.46-0.55 for log-probs). They measure the model's knowledge about a distribution, which is not its own sampling behaviour (the "knowledge-to-simulation gap"). Silicon-sample studies find that model means can match humans while the variance is too small, and that results are fragile to prompt wording and model version. Model sampled-choice proportions should therefore not be treated as estimates of human population proportions without calibration.

### Cited Findings
- [preprint 2024] Meister, Guestrin & Hashimoto benchmark three ways of expressing a distribution, by average TV to human opinion distributions (OpinionQA plus NYT Book Opinions; lower is better):
  - Verbalised JSON distribution: Opus 0.226, GPT-4 0.229, Llama 3 70B 0.244, Haiku 0.254, GPT-3.5 0.291.
  - "Sequence" (the model emits 30 answers in one response): GPT-4 0.278, Haiku 0.309, GPT-3.5 0.318, Opus 0.325, Llama 3 70B 0.328.
  - Log-probs: 0.455-0.550.
  - Baselines: uniform 0.363, majority vote ≈0.71, sequence discretisation error 0.115, and a human baseline of 0.250 ± 0.004.

  Models "can know about distributional alignment yet struggle to sample from their own distribution". The knowledge-to-simulation gap is 9.17% (GPT-3.5), 21.35% (GPT-4), 21.49% (Haiku), 34.65% (Llama 3 70B) and 43.63% (Opus) — [arXiv 2411.05403](https://arxiv.org/html/2411.05403v1)
- [preprint 2025] "Improving the Distributional Alignment of LLMs using Supervision" builds on this comparison of elicitation methods and adds supervised calibration — [arXiv 2507.00439](https://arxiv.org/html/2507.00439v3)
- [PR, Political Analysis 2024] Bisbee, Clinton, Dorff, Kenkel & Larson had ChatGPT-3.5-turbo answer ANES feeling thermometers under personas. Averages tracked ANES closely, but there was "less variation in responses than in the real surveys". Regression coefficients often differed significantly from ANES estimates, and results raised concerns about reliability and reproducibility, including model drift over time — [doi:10.1017/pan.2024.5](https://www.cambridge.org/core/product/B92267DC26195C7F36E63EA04A47D2FE)
- [PR, Political Analysis 2023] Argyle et al., "Out of One, Many". GPT-3 conditioned on sociodemographic backstories reproduced subgroup response patterns ("algorithmic fidelity"); this is the founding "silicon sample" claim. Not re-fetched in this pass — [doi:10.1017/pan.2023.2](https://doi.org/10.1017/pan.2023.2)
- [PR, NeurIPS 2024] Dominguez-Olmedo et al. Relative "alignment" of model answers with demographic subgroups "can be predicted from the subgroups' entropy, irrespective of the model's training data or training strategy". This warns that a match in choice proportions can be an artefact of near-uniform model answers — [arXiv 2306.07951](https://arxiv.org/abs/2306.07951)
- [PR, ICML 2023] Santurkar et al. LM opinion distributions are misaligned with US demographic groups by an amount comparable to the Democrat-Republican divide on climate change, and this persists after steering — [arXiv 2303.17548](https://arxiv.org/abs/2303.17548)
- [PR, EMNLP 2025 Findings] Wang, Zhang & Choi: use the mean of the judgment distribution rather than the mode. Risk-averse aggregation often helps, and CoT collapses the distribution — [arXiv 2503.03064](https://arxiv.org/abs/2503.03064)
- [PR, AAAI 2025] Lyu et al.: sample-consistency confidence (agreement, entropy, first-second distance) is an effective post-hoc confidence signal — [arXiv 2402.13904](https://arxiv.org/html/2402.13904v1)
- [PR, EMNLP 2023] Tian et al.: verbalised confidence beats conditional probability for RLHF models — [arXiv 2305.14975](https://arxiv.org/abs/2305.14975)
- [PR, NeurIPS 2024] Cruz et al.: verbalised risk improves calibration for instruction-tuned models — [arXiv 2407.14614](https://arxiv.org/abs/2407.14614)
- [preprint/ICML 2026] Zhang et al.: verbalised sampling recovers diversity lost to mode collapse — [arXiv 2510.01171](https://arxiv.org/abs/2510.01171v3)
- [PR, EMNLP 2024] Liusie et al.: soft probabilities beat hard decisions for pairwise comparative assessment — [arXiv 2405.05894](https://arxiv.org/abs/2405.05894)

### Inferences
- **Independent T = 1 sampling is not a different readout from log-probs; it is a noisy estimate of the same distribution**, provided the answer is the first token. Meister et al.'s finding that log-probs are too concentrated therefore applies to i.i.d. sampling in expectation. Their better-performing "sequence" method is different: the model writes 30 answers in one response, which is closer to a verbalised distribution.
- **Readout options for the hosted models**, ordered by fidelity to the local log-prob readout:
  - (i) More i.i.d. samples per presentation (cost-bound; see the Q4 table).
  - (ii) Ask in the same call for a probability ("How likely is it that you prefer A? Give a number 0-100") or for a verbalised split. This yields graded output from a single call, but it measures a metacognitive or verbalised quantity. Per Hu & Levy and the knowledge-to-simulation gap, it is not the same construct as the forced choice. It must be validated against log-probs on the local models before being used as a bridge.
  - (iii) Logit lens or other internal readouts need weights and are impossible on hosted endpoints. They are only an option for the open-weight local models.
- **A comparable pipeline across all three sources.** Define the estimand as the probability of choosing X on a random counterbalanced presentation:
  - Local: P̄ = mean_j p_j, with two-way normalised letter probabilities averaged on the probability scale.
  - Hosted: C/K (Jeffreys or beta-binomial smoothed).
  - Human: the proportion q of trials choosing X.
  
  Then compare P̄ with q pair by pair:
  - For direction, use sign(P̄ - ½) vs sign(q - ½) and report expected attenuation for hosted models with g_k.
  - For strength, use the calibration slope b of logit(q) on logit(P̄), fitted on dev stimuli.
  - For heterogeneity, compare τ from a GLMM for hosted models with the binomial-noise-corrected SD of logit(q) and the SD of local z.
- **"Virtual hosted readout" for local models.** Feed each local p_j through the exact hosted estimator (k draws, empirical logit, mean, sign); its expectation can be computed analytically, as in Q4. This makes local "choice" numbers distributionally identical to hosted ones under the assumption that sampled = first-token. Running the Q1 free-reply check on the local models tests that assumption.
- **Population vs individual variability.** A human q mixes between-person disagreement with within-person noise. A model's T = 1 sampling is one "individual's" response noise. Even a perfectly calibrated model need not reproduce q, and the silicon-sample literature (Bisbee: too little variance; Dominguez-Olmedo: too much entropy after debiasing) shows both failure directions occur.

### Gaps
- No study was found that compares log-prob, i.i.d.-sampling and verbalised readouts for VLM image-preference judgments specifically, or on a 2AFC aesthetic task.
- Meister et al.'s final venue could not be confirmed in this pass (v1 lists only arXiv).
- No published evidence was found on whether verbalised preference probabilities from Gemma- or Nemotron-family models track their own letter log-probs. This would need the local validation described above.
- "Logit lens" as a preference readout for VLM 2AFC: no 2023-2026 source was found applying it to this problem.
