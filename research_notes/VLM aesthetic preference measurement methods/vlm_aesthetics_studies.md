# VLM / MLLM aesthetic judgement and preference: what the 2023-2026 literature has found

Scope note: compiled 2026-11-18 from about 30 searches and page reads. "Peer-reviewed" means the venue was confirmed in this session. "Preprint" means only an arXiv version was seen. Numbers come from the papers' own tables as read via fetched pages. A few figures come only from search-engine snippets; those are flagged "(snippet only)" and should be checked before being quoted in a report.

## 1. Which papers/benchmarks evaluate VLM aesthetic perception or preference, and how well do they agree with humans?

### Takeaway
Since 2024 there has been a large family of photo- and art-aesthetics benchmarks: AesBench, UNIAA, AesExpert, Q-Align/Q-Bench, AesTest, PhotoBench, FineArtBench, Venus, PortraitCraft and others. They use natural photos, artworks or AI-generated images and mostly score multiple-choice accuracy or rank correlation with mean opinion scores. They show that general MLLMs are well above chance but well short of experts on fine-grained aesthetic questions. Agreement with humans rises sharply when a model is fine-tuned on human scores (Q-Align SRCC on AVA about 0.8) or when the prompt is structured (ArtCoT roughly doubles rank correlation). Zero-shot rank correlations with human art preferences are only about 0.3-0.5. None of these benchmarks uses controlled synthetic stimuli.

### Cited Findings
**Benchmarks built on photos and art (multiple-choice format)**
- **AesBench** (Huang et al., arXiv 2401.08276, preprint): 2,800 images (natural, artistic, AI-generated), 8,400 QA pairs and 2,800 expert interpretations from 32 professional aesthetics experts. It has four dimensions: Perception (AesP), Empathy (AesE), Assessment (AesA) and Interpretation (AesI). Results by dimension:
  - AesP: chance 35.02%; best Q-Instruct (7B) 72.61%; GPT-4V 72.08%.
  - AesE: chance 34.98%; best Q-Instruct 72.68%; GPT-4V 70.16%.
  - AesA (assessment): chance 33.33%; best only 52.86% (Q-Instruct); GPT-4V 50.86%.
  - AesI (0-2 scale, GPT-graded): GPT-4V best at 1.301.
  - TinyGPT-V (Phi-2 backbone, about 2.7B) scored below chance on AesE (32.04%).
  - The authors claim "a significant gap between MLLMs and humans" but report no human accuracy figure. — [AesBench, arXiv HTML](https://arxiv.org/html/2401.08276v1)
- **AesExpert** (arXiv 2404.09624): a 7B model fine-tuned on a 409K-item aesthetic instruction set. Its authors report that it clearly beats GPT-4V and Gemini-Pro-Vision on aesthetic perception. Exact numbers were not verified here. — [AesExpert summary](https://www.emergentmind.com/papers/2404.09624)
- **UNIAA** (arXiv 2404.09619, preprint): a unified MLLM baseline and benchmark (UNIAA-Bench) covering aesthetic perception, description and assessment. — [UNIAA](https://arxiv.org/pdf/2404.09619)
- **AesTest** (Wang et al., arXiv 2511.06360, preprint, Nov 2025): ten multiple-choice subtasks (perception, appreciation, creation, photography including "Framing Choice"), 17,885 images and 8,757 items.
  - Overall accuracy: Qwen2.5-VL-32B 0.53; Gemini 2.0 Flash 0.50; GPT-4o 0.50; Qwen2.5-VL-7B 0.50; MiniCPM-V (8B) 0.45; InternVL2-8B 0.42; UNIAA-7B 0.41; AesExpert-7B 0.39; CogVLM2 (19.5B) 0.37.
  - Humans, on a 100-item subset: 10 amateurs 0.43; 5 professional photographers 0.54.
  - On the Photography subtask the best model scored 0.32 (Gemini), below amateurs (0.35) and far below professionals (0.83).
  - The aesthetics-specialised models scored below most general models overall.
  - Caveat: the paper's text and tables disagree in several places. — [AesTest](https://arxiv.org/html/2511.06360)

**Fine-tuned scoring models**
- **Q-Align** (Wu et al., ICML 2024, peer-reviewed): teaches an LMM to output discrete text levels (excellent/good/fair/poor/bad). At inference the score is the probability-weighted average over those level tokens, which the authors report beats direct numeric scoring by about 10%.
  - Papers with Code lists the OneAlign variant at SRCC 0.823 on AVA.
  - A third-party re-run lists Q-Align at SRCC 0.798 / PLCC 0.796 on AVA.
  - The paper's own AVA table was not read in this session. — [Q-Align arXiv](https://arxiv.org/html/2312.17090v1); [Papers with Code entry](https://ml.paperswithcode.com/paper/q-align-teaching-lmms-for-visual-scoring-via)

**Zero-shot preference for artworks**
- **FineArtBench / ArtCoT** (Jiang & Chen, arXiv 2501.09012, preprint): 2,000 items (1,000 content, 1,000 style). 18 fine-art experts gave about 80,000 2AFC judgments with no tie option. Inter-annotator R² was only 0.17 raw and 0.31 after removing uncertain and non-transitive pairs.
  - Spearman rho between model-derived and expert rankings (per-artist, Elo):
    - Random: 0.061.
    - LAION Aesthetics Predictor: 0.424. HPSv2: 0.343. PickScore: 0.275. CLIP Score: -0.024.
    - Base prompting: GPT-4o 0.395; Claude 3.5 Sonnet 0.341; Gemini 1.5 Flash 0.496.
    - With the structured ArtCoT prompt: GPT-4o 0.630; Claude 3.5 Sonnet 0.598; Gemini 1.5 Flash 0.705.
  - So under plain prompting, the CLIP-based LAION predictor matched or beat the frontier MLLMs. — [ArtCoT](https://arxiv.org/html/2501.09012v2)

**Aesthetic retrieval with GPT-4V as judge**
- **HPIR aesthetic retrieval** (Zhang et al., NeurIPS 2024, peer-reviewed): GPT-4V judged which of two retrieval result sets was better.
  - With a "ranker" prompt: accuracy 72.01 and aesthetic agreement 64.48 without order-consistency.
  - With order-consistency filtering (judge both orders; count only consistent verdicts): 86.01 and 86.70, against human experts at 87.79 and 85.00.
  - CLIP scored 68.11 on accuracy and 62.05 on aesthetics on HPIR. — [Zhang et al., arXiv HTML](https://arxiv.org/html/2406.09397); [NeurIPS proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/file/9d3faa41886997cfc2128b930077fa49-Paper-Conference.pdf)

**General multimodal judging**
- **MLLM-as-a-Judge** (Chen et al., ICML 2024, peer-reviewed): GPT-4V's pair-comparison agreement with humans is 0.636 with ties and 0.773 without ties. Scoring and batch-ranking modes showed "a huge gap" from human preferences. The authors list position bias, egocentric bias and length bias. (Snippet only for the figures.) — [MLLM-as-a-Judge](https://arxiv.org/pdf/2402.04788)

**Composition and photography benchmarks**
- **PhotoBench / "The Photographer's Eye"** (CVPR 2025, peer-reviewed): a professional photography benchmark built around 284 sub-topics.
- **PortraitCraft** (arXiv 2604.03611, preprint): tests portrait composition understanding through score prediction, attribute reasoning and VQA.
- **SLU-SUITE** (arXiv 2603.18448, preprint): includes a KU-PCP composition-rule identification task whose labels include Rule of Thirds.
- **Venus** (CVPR 2026, peer-reviewed): tests aesthetic guidance and cropping against GPT-4o, Gemini 2.0 Pro, AesExpert and UNIAA.
- Per-rule accuracies for these four were not retrieved. — [Photographer's Eye](https://arxiv.org/html/2509.18582v2); [PortraitCraft](https://arxiv.org/pdf/2604.03611); [SLU-SUITE](https://arxiv.org/pdf/2603.18448); [Venus, CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/papers/Du_Venus_Benchmarking_and_Empowering_Multimodal_Large_Language_Models_for_Aesthetic_CVPR_2026_paper.pdf)

**Other domains (peer-reviewed)**
- **Fashion:** a zero-shot GPT-4V study of outfit aesthetics found predictions align "fairly well" with human judgments, but the model struggles to rank outfits in similar colours. — [arXiv 2410.23730 / ACM DOI 10.1145/3681758.3698022](https://arxiv.org/abs/2410.23730)
- **Restaurant and environment photos:** a ScienceDirect journal paper (2025) concluded GPT-4V "currently demonstrates limited ability" to give meaningful ratings relative to humans. It found only moderate agreement for GPT-4V, and none for Gemini Pro Vision, on general restaurant preference. (Snippet only.) — [ScienceDirect S2949882125001185](https://www.sciencedirect.com/science/article/pii/S2949882125001185)
- **Rock images** (Dickson et al., Behavior Research Methods 2025, peer-reviewed; a psychology-journal comparison of LMM and human perceptual ratings):
  - GPT-4o's 1-9 ratings of 360 rock images correlated 0.84-0.89 with mean human ratings on elementary dimensions (lightness, chromaticity, grain, shininess).
  - Correlations were only 0.61-0.62 for the abstract "disorganized/organized" dimension and 0.68-0.73 for smooth/rough.
  - Human split-half reliabilities were 0.86-0.97; GPT-4o stayed below them on every dimension.
  - Individual humans correlated 0.66-0.87 with the group mean. — [Dickson et al., PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12178973)

### Inferences
- The literature measures aesthetic competence mostly as agreement with crowd or expert scores on rich natural images (AVA, AADB, PARA, artworks). Agreement there can come from content and quality cues (sharpness, subject, colourfulness) rather than from sensitivity to compositional structure. A good AVA correlation therefore says little about whether a model would show balance or inward-facing effects on abstract stimuli.
- The "assessment" and "photography/framing" subtasks are the closest to compositional judgement, and they are consistently the weakest: AesBench AesA about 51-53% against 33% chance, and AesTest Photography 0.30-0.32. This matches the project's finding that small models do not reproduce compositional effects.
- On FineArtBench, under base prompting, the CLIP-based LAION predictor (rho 0.42) was as good as or better than GPT-4o and Claude 3.5 Sonnet. Simple embedding regressors are therefore a meaningful baseline next to generative 2AFC.

### Gaps
- No human accuracy was reported for AesBench. The AesExpert and UNIAA numbers were not independently verified here.
- The paper's own Q-Align AVA SRCC/PLCC table was not read; only secondary listings were seen.
- No benchmark found reports per-item agreement on composition-only manipulations.

## 2. Have studies tested classic controlled empirical-aesthetics effects (balance, centre of mass, inward bias, colour weight, golden ratio, symmetry, complexity) on VLMs or vision models with synthetic stimuli?

### Takeaway
I found no 2023-2026 study that re-creates any of these paradigms on VLMs with controlled synthetic stimuli: Wilson & Chatterjee's balance test (APB), Palmer's inward-facing bias, Locher's colour-weight work or McManus-style golden-section comparisons. The nearest work comes in three kinds:
- linear probes of VLM hidden states against AADB photo attribute labels, including "BalancingElements", "RuleOfThirds" and "Symmetry", which give weak correlations of about 0.27-0.33;
- deep nets predicting beauty ratings of natural images;
- VLM "machine psychology" on synthetic stimuli in non-aesthetic domains, where models fall well short of humans.

On the evidence found, the project's design looks novel.

### Cited Findings
**Attribute probes**
- **Ryu & Yanaka** (arXiv 2604.11374; also listed in Findings of ACL 2026) fitted ridge-regression probes on layer-pooled hidden states (prompt: "Assess the aesthetics of this image.") against AADB attribute labels on photographs. Best Spearman rho:

  | Attribute | Range across models |
  |---|---|
  | BalancingElements | 0.300-0.332 (Qwen3-VL 2B/4B/8B and Gemma 3 4B/12B) |
  | RuleOfThirds | 0.266-0.288 |
  | Symmetry | 0.281-0.329 |
  | ColorHarmony | 0.49-0.52 |
  | Overall score | 0.70-0.73 |

  - The vision-only baseline DINOv3 reached 0.307-0.317 on BalancingElements, about the same as the VLMs.
  - The authors find that balance, thirds and symmetry are the most weakly encoded attributes. — [Ryu & Yanaka, arXiv HTML](https://arxiv.org/html/2604.11374); [ACL Anthology Findings 2026](https://aclanthology.org/2026.findings-acl.1706.pdf)

**Deep nets predicting beauty ratings**
- **Conwell, Graham & Vessel** (PNAS 2024, peer-reviewed): features from 180 deep nets trained only on standard vision tasks predicted the majority of explainable variance in human beauty, arousal and valence ratings for objects, faces, landscapes and art. On the Vessel dataset, the model predictions were more representative of the group average than any individual respondent. (Snippet only for that comparison.) — [PNAS 10.1073/pnas.2306025121](https://www.pnas.org/doi/10.1073/pnas.2306025121)
- **Conwell et al.** (arXiv 2410.23603, preprint): unimodal vision models (SimCLR) explain most explainable variance in beauty ratings of natural images. Language alignment (SLIP, CLIP-style) adds "small gains", and captions alone predict worse. — [arXiv 2410.23603](https://arxiv.org/abs/2410.23603)
- A Science Advances paper (2024) reports that "integrative processing" in artificial and biological vision predicts perceived beauty of natural images. Only the title was seen; numbers were not read. — [Science Advances adi9294](https://www.science.org/doi/10.1126/sciadv.adi9294)
- A 2026 PubMed-indexed study using human-aligned deep CNNs found:
  - a reduced-complexity "integration" metric from early layers predicts perceptual fluency of paintings well, but liking less well;
  - ridge regression on deeper layers predicts liking better.
  (Snippet only.) — [PubMed 42291181](https://pubmed.ncbi.nlm.nih.gov/42291181/)

**Symmetry**
- Symmetry *detection* (older, context only, 2021): feed-forward deep nets were inadequate at learning symmetry as an abstract concept, and recurrent connections helped. This tests detection, not preference. — [arXiv 2112.04162](https://arxiv.org/pdf/2112.04162)

**Centre bias (non-aesthetic)**
- A 2026 preprint on counterfactual semantic saliency found VLMs over-rely, relative to humans, on large objects, centrally placed objects and high-saliency objects. This is about scene understanding, not preference, but it is relevant to centre-of-mass and balance manipulations. (Snippet only.) — [arXiv 2605.13047](https://arxiv.org/html/2605.13047v1)

**Machine psychology on synthetic stimuli (non-aesthetic)**
- **Schulze Buschoff, Akata, Bethge & Schulz** ("Visual cognition in multimodal LLMs", arXiv 2311.16093 v3; journal version not confirmed here) tested GPT-4V, Claude-3 Opus, Fuyu-8B, Otter (about 7B) and LLaMA-Adapter V2 (about 7B) on classic synthetic-stimulus paradigms.
  - Block-tower stability: GPT-4V was barely above chance (odds ratio 2.6; R² with humans 0.066, against 0.354 for individual humans).
  - Michotte launching, counterfactual question: best model fit 0.42 against 0.85 for humans.
  - Help/hinder intention: best model 0.19 against 0.93 for humans.
  - Conclusion: no model matched human behaviour in any domain. — [arXiv 2311.16093](https://arxiv.org/html/2311.16093v3)

**Complexity and creativity ratings**
- GPT-4o mini rated visualisation complexity well, whereas classic image-complexity metrics did not correlate with human complexity ratings (arXiv 2512.05536, preprint). — [Eye of the Beholder](https://arxiv.org/html/2512.05536)
- In a 2026 preprint, MLLMs matched human visual-creativity ratings, and partial correlations suggest this is not explained by shared sensitivity to low-level complexity. — [arXiv 2606.29672](https://arxiv.org/html/2606.29672v1)
- In Dickson et al. (BRM 2025), the "organization" dimension, the closest to a compositional judgement, was the weakest for every model (GPT-4o r = 0.61-0.62). A revised prompt stressing "global organization", plus nine anchor images, did not help. — [Dickson et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC12178973)

**Background (pre-2023, context only)**
- Palmer, Gardner & Wickens (2008, *Spatial Vision*) found strong centre and inward-facing biases using 2AFC, adjustment and free-choice paradigms. — [Palmer et al. 2008 PDF](https://palmerlab.berkeley.edu/pdf/PalmerGardner&Wickens-1.pdf)
- A 2021 follow-up attributes the inward bias mainly to frame proportions. — [Forman et al.](https://perception.yale.edu/papers/21-Forman-EtAl-APP.pdf)
- A bioRxiv preprint argues pictorial balance is a bottom-up percept affecting eye movements. — [bioRxiv 2020.05.26.104687](https://www.biorxiv.org/content/10.1101/2020.05.26.104687.full.pdf)

### Inferences
- The AADB probe results suggest that "balance" information on natural photos is weakly and similarly present in 2B-12B VLMs and in vision-only DINOv3, with rho about 0.3. A balance preference on synthetic compositions is therefore not something these models obviously inherit from training on photos.
- The deep-net beauty results (Conwell et al.) are driven by naturalistic content variation, so they do not predict how models react to subtle compositional changes with content held constant, which is the regime of APB/Palmer-style stimuli.
- VLMs over-weight centrally placed and large objects relative to humans (arXiv 2605.13047). One possible mechanism for a model showing a *stronger* centre/balance preference than people is an attentional or representational centre bias rather than aesthetic sensitivity. This is a hypothesis, not a tested finding.

### Gaps
- I found no study of VLM/MLLM preference for: pictorial balance or centre of mass (APB-style); inward vs outward facing; colour and visual weight (Locher); golden section vs other rectangle proportions (McManus-style); or symmetry preference (as opposed to detection) with synthetic stimuli.
- I also found no CNN/CLIP study from 2023-2026 that predicts APB-type human balance ratings. A targeted search returned only body-balance (posture) papers.
- Science Advances 2024 and PubMed 42291181 were seen only as snippets.

## 3. Model scale: do larger models match human aesthetic effects better? Do models over-apply "textbook" rules?

### Takeaway
Evidence on scale is thin and mostly negative or mixed. Within families, bigger is slightly better on perception-type aesthetic items but not on compositional or photography items. Across families, size does not predict alignment, and the "most capable" or "thinking" variants are sometimes worse. I found no study showing that models apply textbook rules (rule of thirds, golden ratio) more strongly than people. Adjacent work shows strong knowledge priors (VLMs answer from memorised knowledge instead of the image) and a skew in the LAION predictor toward realistic over abstract imagery.

### Cited Findings
**Scale within and across families**
- **AesTest** (preprint): Qwen2.5-VL-32B against 7B gained 0.57 vs 0.52 on Perception and 0.61 vs 0.58 on Appreciation, but was flat on Creation (0.46 vs 0.45) and Photography (0.30 vs 0.30). CogVLM2-19.5B (0.37) scored below several 7-8B models (0.42-0.50). — [AesTest](https://arxiv.org/html/2511.06360)
- **Ryu & Yanaka** (Findings of ACL 2026): across Qwen3-VL 2B/4B/8B and Gemma 3 4B/12B, probe performance on aesthetic attributes did not track model size. The 2B model sometimes beat larger ones, for example RuleOfThirds 0.288 for 2B against 0.266 for 8B. — [Ryu & Yanaka](https://arxiv.org/html/2604.11374)
- **AesBench**: the smallest model tested, TinyGPT-V (Phi-2 backbone), fell below chance on Aesthetic Empathy (32.04% against 34.98% chance). 7B models reached about 60-73% on perception items. — [AesBench](https://arxiv.org/html/2401.08276v1)
- **ArtCoT** (preprint): "thinking" variants aligned worse with expert art rankings than a plain base model. Per-artist Elo rho was 0.285 for Claude 3.7 Sonnet thinking and 0.204 for Gemini 2.0 Flash thinking, against 0.496 for base Gemini 1.5 Flash. — [ArtCoT](https://arxiv.org/html/2501.09012v2)
- **Dickson et al.** (BRM 2025): among Claude-3 models, Sonnet beat Haiku and Opus on 9 of 10 perceptual dimensions. Opus, the largest and "most capable", led on none. GPT-4o was best overall. — [Dickson et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC12178973)
- **Schulze Buschoff et al.**: the 8B Fuyu sometimes matched GPT-4V on synthetic cognition tasks. The authors left scale effects as an open question. — [arXiv 2311.16093](https://arxiv.org/html/2311.16093v3)

**Knowledge priors and predictor skew**
- **"Vision Language Models are Biased"** (Vo et al., arXiv 2505.23941, preprint): on counterfactual images of familiar subjects (for example a logo given a fourth stripe), state-of-the-art VLMs averaged 17.05% counting accuracy over 7 domains. Removing backgrounds improved accuracy by 21.09 percentage points. The authors attribute the failures to memorised-knowledge responses overriding the visual evidence. — [arXiv 2505.23941](https://arxiv.org/abs/2505.23941)
- **LAION-Aesthetics Predictor audit** (arXiv 2601.09896, preprint): the predictor is a linear head on CLIP ViT-L/14 embeddings, trained largely on AVA photo-contest ratings. The audit reports it favours realistic landscapes, cityscapes and people over abstract art, and calls it a reflection of "imperial, realist, and male" sensibilities. The developer chose the architecture and data weighting partly by "visual inspection" and "subjective taste". — [Algorithmic Gaze, arXiv v4](https://arxiv.org/html/2601.09896v4); [LAION blog](https://laion.ai/blog/laion-aesthetics/); [Moonlight review](https://www.themoonlight.io/en/review/the-algorithmic-gaze-an-audit-and-ethnography-of-the-laion-aesthetics-predictor-model)
- **Facial golden ratio** (clinical, PMC12112453): a plastic-surgery study asked ChatGPT-4o, ChatGPT-4, Gemini 1.5 Pro and Claude 3.5 Sonnet to assess golden-ratio and rule-of-thirds adherence in faces. They were compared with a surgeon and with manual measurement, not with lay preference. Accuracy numbers were not retrieved. — [PMC12112453](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12112453/)

### Inferences
- Because larger models did not reliably improve on compositional or photography items in AesTest, and the probes showed no size trend, the project's 0.8B-5B models should not be expected to be fixed simply by scale. The hosted 31B-class models may help on "perception" items more than on composition.
- The memorised-knowledge failure mode (Vo et al.) and the textbook-heavy aesthetic text in pretraining make a "rule over-application" effect plausible: for example, a model choosing the more "balanced" image more consistently than people. The literature found does not test this. A model with a balance preference stronger than humans would be a new observation rather than a replication.
- Reasoning or "thinking" modes lowered alignment in ArtCoT. Longer deliberation may therefore not bring VLM choices closer to human 2AFC preferences.

### Gaps
- No study found compares VLM effect sizes on golden-ratio, rule-of-thirds or balance manipulations against human effect sizes.
- No systematic within-family scale sweep (for example 0.5B to 72B) on aesthetic preference was found.
- The facial golden-ratio study's numbers were not retrieved.

## 4. Methods used and methodological problems reported

### Takeaway
Methods range widely:
- multiple-choice accuracy (AesBench, AesTest);
- MOS-style ratings, sometimes read out as probability-weighted level tokens (Q-Align; exploratory top-20 log-probs in Dickson et al.);
- linear probes on hidden states (Ryu & Yanaka);
- pairwise 2AFC (FineArtBench, 2AFC-LMM, HPIR, MLLM-as-a-Judge).

Problems reported repeatedly:
- position or order bias in pairwise judgements, worst for near-equal pairs;
- prompt-wording sensitivity, including chain-of-thought lowering alignment;
- format non-compliance and invalid answers;
- answers driven by priors or memorised knowledge.

Some major benchmarks (AesTest, ArtCoT) did not control order or prompt wording at all.

### Cited Findings
**Pairwise designs and order effects**
- **2AFC-LMM** (Zhu et al., IEEE TCSVT 2024, peer-reviewed): adapts the psychophysics 2AFC paradigm to LMM quality judgement with a fixed prompt ("Which image has better visual quality?") and estimates global scores from sparse pairs by MAP estimation. It scores models on three criteria, one of which is consistency (kappa) when the two images are swapped. LMMs did well on coarse-grained comparisons but poorly on fine-grained discrimination. The follow-up Co-Instruct reports very high kappa under swapping after fine-tuning on comparisons. — [Zhu et al., arXiv 2402.01162](https://arxiv.org/pdf/2402.01162); [IEEE TCSVT](https://dl.acm.org/doi/abs/10.1109/TCSVT.2024.3434999); [Co-Instruct](https://arxiv.org/html/2402.16641v1)
- **HPIR** (NeurIPS 2024): GPT-4V "tends to prefer the first row when the two results look comparable", and for pairs with small aesthetic differences its results "depend heavily on presentation order". Requiring the verdict to hold under both orders raised GPT-4V's aesthetic agreement from 64.48 to 86.70. — [Zhang et al.](https://arxiv.org/html/2406.09397)
- **MLLM-as-a-Judge** (ICML 2024): MLLM judges favour responses in specific positions. Chain-of-thought plus a "vision expert system" partly reduced this. (Snippet only.) — [arXiv 2402.04788](https://arxiv.org/pdf/2402.04788)
- **FineArtBench/ArtCoT** used a fixed left/right 2AFC readout (0 = left, 1 = right), repeated 3 times, and did not report any order-swap control. Human 2AFC pairs were pruned when uncertain (P in [0.4, 0.6], 20.1% removed) or non-transitive (15.3% removed). — [ArtCoT](https://arxiv.org/html/2501.09012v2)

**Prompt sensitivity**
- In ArtCoT, zero-shot chain-of-thought lowered alignment with human rankings by about 16-18% on average and increased subjective, hallucinated "interpretation". The structured ArtCoT prompt raised rho by 19-51%. — [ArtCoT](https://arxiv.org/html/2501.09012v2)
- In Schulze Buschoff et al., forcing single-number answers made GPT-4V give constant judgements. Removing quotation marks around labels made Fuyu's ratings flip completely on some items. — [arXiv 2311.16093](https://arxiv.org/html/2311.16093v3)
- AesTest used one standardised prompt with no sensitivity test. — [AesTest](https://arxiv.org/html/2511.06360)

**Format, invalid answers and refusals**
- In AesBench, models often ignored the required answer format (for example answering "The image can not maintain..." instead of a letter). The authors fell back on GPT-assisted grading. — [AesBench](https://arxiv.org/html/2401.08276v1)
- In AesTest, items with no valid response after repeated queries were scored wrong. Multi-image items were tiled into one composite for single-image models, which is a format confound. — [AesTest](https://arxiv.org/html/2511.06360)
- In Schulze Buschoff et al., answers from small open models were parsed by hand, and LLaMA-Adapter V2 gave only invalid answers on one question. — [arXiv 2311.16093](https://arxiv.org/html/2311.16093v3)

**Readout and sampling**
- Dickson et al. used temperature 0 with no repeated sampling. Outputs clustered on 0.05 increments, a rounding artefact. Probability-weighting GPT-4o's top-20 log-prob answers gave "small, systematic" gains (exploratory). — [Dickson et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC12178973)
- Q-Align reads scores as probability-weighted averages over level tokens rather than sampled text. — [Q-Align](https://arxiv.org/html/2312.17090v1)

**Contamination, priors and noisy human references**
- Vo et al. show VLM answers driven by memorised priors on familiar subjects (17.05% accuracy on counterfactual counting). — [arXiv 2505.23941](https://arxiv.org/abs/2505.23941)
- In FineArtBench, inter-expert agreement was itself low (R² 0.17-0.31), which caps how much model-human agreement is possible. — [ArtCoT](https://arxiv.org/html/2501.09012v2)

### Inferences
- The project's design (counterbalanced A/B order, a fixed one-letter answer, synthetic stimuli with no familiar subjects) directly addresses the three most-cited problems: order bias, format non-compliance and prior-driven answers. Several large published benchmarks did not do this.
- HPIR's "count only order-consistent verdicts" approach and the 2AFC-LMM swap-kappa are the two published precedents for handling position bias in aesthetic 2AFC with MLLMs. Both report that bias is concentrated in near-equal pairs, which is exactly where subtle compositional manipulations sit.

### Gaps
- No quantitative position-bias rate was retrieved for MLLM-as-a-Judge, or for 2AFC-LMM's per-model kappa values.
- I found no aesthetics paper that systematically varies the "more pleasing" wording, for example "beautiful" vs "pleasing" vs "prefer", across many paraphrases.
- I found no aesthetics study reporting refusal rates for "which do you prefer" questions. The refusal mentions found concern invalid formats rather than declined preference questions.

## 5. CLIP / vision-encoder aesthetic predictors (LAION predictor etc.) against human judgements, including composition

### Takeaway
CLIP-embedding regressors (LAION Aesthetics Predictor, CLIP-IQA, HPSv2, PickScore) agree moderately with human preferences on natural or artistic images (rho about 0.3-0.45 against expert art rankings). Under plain prompting they are competitive with frontier MLLMs. Vision-only features explain most explainable variance in beauty ratings, and language alignment adds little. However, the main predictor is trained on photo-contest data with documented skews, and no study found validates these predictors against composition psychophysics.

### Cited Findings
- **FineArtBench** (per-artist Elo rho with experts):

  | Predictor | rho |
  |---|---|
  | LAION Aesthetics Predictor | 0.424 |
  | CLIP-IQA | 0.366 |
  | HPSv2 | 0.343 |
  | PickScore | 0.275 |
  | Compare2Score | 0.091 |
  | Raw CLIP Score | -0.024 |
  | GPT-4o, base prompt (for comparison) | 0.395 |

  — [ArtCoT](https://arxiv.org/html/2501.09012v2)
- **HPIR** (NeurIPS 2024): CLIP scored 68.11 on accuracy and 62.05 on aesthetics. Other aesthetic models scored 58.35 (CLIP-IQA), 63.32 (IAP) and 53.21 (MANIQA) on aesthetics. Human experts scored 85.00 on aesthetics. — [Zhang et al.](https://arxiv.org/html/2406.09397)
- **Conwell et al.**: in PNAS 2024, features from 180 vision-only deep nets explain the majority of explainable variance in beauty ratings. In the 2024 preprint, language-aligned vision models (SLIP) add only "small gains" over unimodal SimCLR. — [PNAS](https://www.pnas.org/doi/10.1073/pnas.2306025121); [arXiv 2410.23603](https://arxiv.org/abs/2410.23603)
- **Ryu & Yanaka**: DINOv3 (vision-only) probes give BalancingElements rho 0.307-0.317 and RuleOfThirds 0.230 on AADB. These are similar to or slightly below the VLM language-decoder layers. — [Ryu & Yanaka](https://arxiv.org/html/2604.11374)
- **LAION predictor audit** (preprint): a linear head on CLIP ViT-L/14, trained mostly on AVA plus SAC and LAION-Logos. It favours realistic over abstract imagery. Captions mentioning women, Hindus or Christians are more likely to pass the 6.5+ threshold, and captions mentioning men, Jews or Muslims are more likely to be filtered out. — [arXiv 2601.09896](https://arxiv.org/pdf/2601.09896); [LAION blog](https://laion.ai/blog/laion-aesthetics/)
- **Older context:** a pre-2023 MIRFLICKR study compared an algorithmic rule-of-thirds score with rankings from 255 human participants and reported broadly human-like behaviour. — [Springer chapter](https://link.springer.com/chapter/10.1007/978-3-319-75417-8_44)

### Inferences
- A CLIP/LAION aesthetic score would make a useful non-generative comparison condition for the project's synthetic stimuli. The audit's finding that the predictor favours realistic over abstract imagery means its absolute scores on abstract compositions may be compressed or uninformative. Only within-pair differences would be interpretable.
- Since language alignment adds little to beauty prediction (Conwell et al.), differences between VLMs on compositional preference are more likely to come from the vision encoder and readout than from linguistic "aesthetic knowledge", unless the textbook-rule-prior route described in Section 3 is operating.

### Gaps
- I found no study testing the LAION predictor, CLIP-IQA or similar against APB balance stimuli, Palmer facing or position stimuli, or golden-section rectangles.
- The exact explained-variance numbers in Conwell et al. were not retrieved: the PNAS figures came as snippets and the 2024 preprint abstract gives no numbers.
- Venus (CVPR 2026) cropping results and PortraitCraft composition scores were not retrieved, so it is unknown whether MLLM cropping prefers centred or thirds placements more than humans do.
