# Related work, and how this project differs

Search date: 14 November 2026.

**How to read the citations here.** Three levels of access are marked:
`[abstract]` = I read the abstract page myself; `[full text via reader]` = a delegated
reader queried the full HTML through a fetch tool that summarises pages, so details are
second-hand; `[listing]` = search snippet or secondary description only. Numbers marked
`[full text via reader]` or `[listing]` have **not** been checked against the PDFs and
must be checked before they are quoted in the final report. None of them feeds any
analysis in this project.

## 1. The benchmark named in the brief: AesEval-Bench

An, Sun, Huang, Cheng, Gao, Li, Qiao & Bian (2026), "Can Vision Language Models Assess
Graphic Design Aesthetics? A Benchmark, Evaluation, and Dataset Perspective",
arXiv:2603.01083, ICLR 2026. `[abstract]` for the first paragraph, `[full text via
reader]` for the second.

It frames design aesthetics as question answering over **four dimensions, twelve
indicators and three tasks** (aesthetic judgment, region selection, precise
localisation), evaluates proprietary, open-source and reasoning VLMs, and builds a
training set to fine-tune them.

Per the reader: the images are real professional templates (the Crello test split), each
given one to three random perturbations at the layout-description level (moving an
element, changing a font or a colour) and re-rendered; human annotators then decide
whether the perturbed design really shows a flaw, and the label is their majority vote.
Scoring is accuracy against that vote (and IoU for localisation). The best reported
model reaches roughly 0.7 accuracy on the yes/no judgment task. The paper reports no
analysis by perturbation type or size.

So AesEval-Bench *does* perturb its images, but the perturbation is a way of
manufacturing flawed examples of real designs. The reference is still a fresh human
label per image, and the output is an accuracy.

## 2. The rest of the field does the same kind of thing

Every VLM aesthetics benchmark the search found grades models against human ratings,
votes or expert labels collected for that benchmark, on real photographs, artworks,
designs, or AI-generated images. Representative examples (all `[listing]` or
`[full text via reader]`): AesBench (arXiv:2401.08276), UNIAA (2404.09619), AesExpert
(2404.09624), Q-Bench and Q-Align (2309.14181, 2312.17090; image quality rather than
aesthetics), DesignProbe (2404.14801), VisJudge-Bench (2510.22373), ArtiMuse
(2507.14533), AesTest (2511.06360), Visual Aesthetic Benchmark (2605.12684), TASTE
(2605.20731).

## 3. Nearest neighbours

None of these re-runs a published empirical-aesthetics experiment, but each shares one
ingredient with this project.

| Work | Shared ingredient | What it lacks for our purpose |
|---|---|---|
| Krol & McCormack, ICCC 2026, arXiv:2606.00112 `[full text via reader]` | Code-generated abstract images; a VLM makes pairwise aesthetic choices | Reference is one artist's ranking; no psychological manipulation; no order control reported |
| Cherep et al., ICML 2026, arXiv:2602.15278 `[full text via reader]` | 2AFC between an image and an edited twin, both orders run | Edits are generative changes to photographs; composition is not isolated; new human data rather than a published effect |
| Mehmood et al. 2026, arXiv:2603.24578 `[full text via reader]` | VLMs re-run the pairwise protocol of an earlier human experiment | Tone-mapping of photographs, not composition |
| Di Bartolomeo et al., Computer Graphics Forum 2026, doi:10.1111/cgf.70436 `[listing]` | Replicates two classic human studies with an AI as participant | Graph-drawing readability, not aesthetics of composition |
| Athreya & Malladi 2026, arXiv:2608.10195 `[full text via reader]` | Scores models on replication of published human behavioural effects | Gestalt grouping, not preference |
| Lelièvre & Neri, J. Vision 2021, doi:10.1167/jov.21.5.9 `[full text via reader]` | Abstract paintings, a controlled transformation (rotation) | Real artworks; a CNN judging orientation, not preference |

**Looked for and not found:** any VLM, CLIP/CNN or image-generator re-run of Wilson &
Chatterjee's balance test, Palmer, Gardner & Wickens's centre and inward biases, Leyssen
et al.'s multi-object compositions, Locher's colour swaps or McManus's altered
Mondrians; any aesthetics benchmark that reports a model effect size next to a
published human one; any report of first-versus-second choice rates on literally
identical image pairs. Citation lists for the five source papers (Semantic Scholar,
OpenAlex) contained no VLM study. Indexes lag for recent preprints, so absence here is
"not found on this date", not proof of absence.

## 4. How this project differs

1. **Stimuli are generated, not collected.** Every image is drawn by code from a seed,
   so the manipulated property (balance score, position, facing, colour placement) is
   known exactly and nothing else varies within a pair. Benchmarks on real images cannot
   say *which* property a model responded to.
2. **The reference is a published experiment, not a new label.** The target is the
   effect the source paper reports (a proportion, a correlation, a null), with its
   sample size and interval. There is no per-image ground truth and no accuracy.
3. **The human record is allowed to be wrong, weak or absent.** One source experiment is
   a published failure to find a balance preference. A model that shows the textbook
   effect where people did not is a finding, not an error.
4. **Bias is measured, not assumed away.** Identical pairs give each model's position
   bias; a same/different question on the same pairs shows whether the model can see the
   manipulation at all; every pair is run in both orders with both label assignments.
5. **No ranking of taste.** The output is a set of model-versus-human effect
   comparisons, not a leaderboard.

## 5. What we take from the forced-choice literature

Reported order effects in two-image comparisons are large, which is why position bias
gets its own control here. Examples (all `[full text via reader]`, unchecked numbers):
Zhu et al. (arXiv:2402.01162) report order-swap consistency well under 0.5 for several
open models; TASTE (2605.20731) and Zhang et al. (2406.09397) run both orders and treat
disagreement as a tie; Asaria et al. (2606.20364) find the order-flip rate tracks how
discriminable the pair is. Zheng et al. (ICLR 2024, arXiv:2309.03882) `[listing]` show a
separate prior over option letters, which is why labels are counterbalanced
independently of position here.

Two practices we adopt: run both orders always; and never score a hard choice without
also reporting the graded log-odds, because a model with strong position bias gives
50/50 hard choices that hide a real preference.
