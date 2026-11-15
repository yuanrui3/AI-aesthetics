# Source experiments

Status: **draft for Gate 1**, 15 November 2026. Dev stimuli exist for all five; contact
sheets are in `stimuli/<experiment>/dev/contact_<experiment>.png`. E1 to E3 meet the
brief's criteria (with one caveat each). **E4 and E5, the grid-composition leads, do
not**; what was built instead and the decision this needs are at the end.

Conventions used throughout:

- **Provenance of every human number** is one of: *printed* (read by me in the paper's
  text or table, page given), *digitised* (measured from a published figure; error about
  one percentage point unless stated), *derived* (computed from printed numbers by a
  formula in `scripts/human_effects.py`), or *reader* (reported by a delegated reader and
  not yet checked by me; never used for an anchor).
- **A pair** is a reference image and its manipulated twin. Each pair is shown four ways
  (both orders x both letter assignments). The pair's **preference** is the mean over the
  four presentations of the log-odds for the reference; the pair's **choice** is 1 if
  that mean is positive. Position and label bias cancel in both.
- **Readout (local models).** The model's reply is started with "Answer:" and the
  log-probabilities of the two permitted answers are read from the next token. Refusals
  are counted separately, from replies the model writes freely on a sample of trials
  (see `PLAN.md`).
- **Model intervals** are 95% bootstrap intervals over stimuli. Pairs that share images
  are resampled together.
- A model is one observer. Where a paper gives both an aggregate effect (computed on
  ratings averaged over people) and the spread of individual effects, both are shown,
  because a single model is more fairly compared with an individual.

| | Experiment | Manipulation | Source task | Human anchor | Status of the human effect |
|---|---|---|---|---|---|
| E1 | Balance (Wilson & Chatterjee 2005) | Shift of visual weight, 5 dose levels | Ratings, converted | r = -.85 to -.88 over images | Replicated in aggregate; weak and variable in individuals; two nulls on a subset |
| E2 | Two objects (Leyssen et al. 2012, Exp 5) | Shift of the object pair off-centre | Forced choice | P(balanced) about .53, not above chance | **The contested null** |
| E3 | One object (Palmer et al. 2008) | In-place mirror flip; position shift | Forced choice | Inward-facing chosen about 74% | Robust in the source; small samples (N = 9, 17) |
| E4 | Colour swap in grids (Locher et al. 2005) | Colours exchanged between the largest and a small area | Weight ratings; **no preference task** | Direction only: red rated heavier than yellow | Reduced form; **owner to decide** |
| E5 | Altered proportions (McManus et al. 1993) | Grid lines moved | Forced choice against the artist's original | **None** for generated grids (55% for real paintings) | Cannot be re-run under the code-only rule; kept as a control; **owner to decide** |

---

## E1. Balance: the Assessment of Preference for Balance

**Citation.** Wilson, A., & Chatterjee, A. (2005). The assessment of preference for
balance: Introducing a new test. *Empirical Studies of the Arts, 23*(2), 165-180.

### Source design
- Stimuli: a white 750 x 750 px square with seven black elements of varying sizes, all
  circles, all squares or all hexagons (p.168). 216 images were hand-made in Photoshop
  "to cover a range of balance scores (range 3.6% to 65.9%)" (p.171). The paper gives no
  element sizes and no placement rule.
- Balance score (p.168): the mean of eight measures, each
  `|area1 - area2| / (area1 + area2) x 100`, where the two areas are the element pixels
  in two equal halves of the square. Four splits are halves about the vertical axis, the
  horizontal axis and the two diagonals; four are "inner" versus "outer" regions about
  the same axes. **0 = balanced, 100 = everything on one side. Lower is more balanced.**
- Experiment 1 (N = 10): balance ratings, then preference ratings, of all 216 images.
  21 images were then removed (15 for regression residuals beyond 2 SD, 6 to equalise
  shapes), leaving 195 (pp.172-173).
- Experiment 2 (N = 30, no art training): preference ratings on a 1-5 scale for the 195
  images, each shown once, no time limit (p.175). **A rating task, not a forced choice.**

### Human result
Linear regression across images of the mean rating on the balance score. The paper
prints R squared, slope and its standard error; r and its interval are derived.

| Set | N raters | Images | R squared | Slope (rating points per score point) | r (derived) | 95% CI (derived) |
|---|---|---|---|---|---|---|
| Exp 2, circles | 30 | 65 | .73 | -0.022 (SE 0.002) | -.854 | [-.909, -.771] |
| Exp 2, hexagons | 30 | 65 | .78 | -0.025 (SE 0.002) | -.883 | [-.927, -.815] |
| Exp 2, squares | 30 | 65 | .44 | -0.018 (SE 0.003) | -.663 | [-.781, -.500] |
| Exp 1, circles (before removing outliers) | 10 | 72 | .49 | -0.024 (SE 0.003) | -.700 | [-.802, -.559] |
| Exp 1, hexagons (before removing outliers) | 10 | 72 | .47 | -0.021 (SE 0.003) | -.686 | [-.792, -.540] |

All *printed* in Tables 1b and 2 (pp.173, 175; Table 2 checked against the page image).
Dose response: the paper has no table by level; it reports that for circles and hexagons
preference "seemed to plateau at the objective balance score of around 20%", i.e. below
about 20 a better score bought no more liking (p.175).

**How solid is it?**
- The Experiment 2 fit is on a set from which the worst-fitting images had been removed
  using Experiment 1, so it overstates the effect for unselected images. The Experiment 1
  rows are the before-removal figures, but there preference was rated straight after
  balance, which the authors flag as a possible carry-over.
- Hübner & Fillinger (2016, *Frontiers in Psychology* 7:335) re-ran the 130 circle and
  hexagon images with 21 new raters. Aggregate: r = -.867 (circles -.882, hexagons
  -.928). **Individual raters: mean r = -.42 (SD .36) for circles and -.46 (SD .35) for
  hexagons, ranging from -.86 to +.39** (*printed*, their Tables 7-8, checked in the
  text). With 144 newly generated images (their Exp 3, N = 23), aggregate r = -.737 for
  the balance score and -.742 for the deviation of the centre of mass; mean individual
  r = -.28.
- Two studies using an 18-image subset found no effect of balance on liking: Silvia &
  Barona (2009), N = 40, and Cotter et al. (2017), N = 119 (*reader*; not checked by me).
- Hübner & Fillinger also show the score is not a pure balance measure: its four
  inner/outer terms rate a clump in the middle of the frame as badly unbalanced.

### Our stimuli (`src/aesx/experiments/apb.py`, `src/aesx/balance.py`)
- 512 x 512 px white square, seven black circles or seven black hexagons, diameters drawn
  uniformly from 7% to 20% of the side, no overlaps, nothing touching the frame.
- A **family** is one set of seven elements laid out at five balance levels (targets 6,
  15, 25, 40, 58; search tolerance 1 point). Each level is made from the previous one by
  moving elements one at a time until the score reaches the next target.
- All ten pairs of levels within a family are forced-choice pairs. Reference = the more
  balanced layout; dose = the difference in balance score (about 8 to 52 points).
- Dev: 8 families (80 pairs, 16 identical controls). Test: 20 families (200 pairs, 40
  identical controls).
- **Validation of the score.** Measuring the paper's own worked example (its Figure 2,
  with the overlaid lines removed) with our code gives 8.61 against the printed 8.58, and
  an element area of 76,916 px against the printed 76,666. The diagonal inner/outer
  boundary is not stated in the text; Figure 2 draws it at 0.293 of the side, which is the
  equal-area band (1 - 1/sqrt 2) and is what we implement.

**Deviations from the source.**
1. Rating converted to forced choice between two layouts of the *same* elements.
2. Layouts are generated by search, not drawn by hand, and nothing is removed afterwards.
   The fair human comparator is therefore somewhere between the Experiment 1 and
   Experiment 2 rows, and Hübner & Fillinger's generated-stimulus r = -.74.
3. The search is constrained so that higher scores come from weight pushed toward a side
   or corner (centre of mass displaced by at least 3, 7, 13 and 22% of the side at
   levels 2 to 5), as in the paper's Figure 3. Without that constraint the search reaches
   high scores with a clump in the middle, which the source set did not contain. In our
   dev set the balance score and the centre-of-mass deviation correlate at r = .94
   (Hübner & Fillinger report .87 for the source set).
4. Squares are left out, as in the final test.

### Model counterpart (`aesx.effects.apb_effects`)
- **Primary:** each image gets a scale value, its mean preference over the four other
  layouts in its family. The statistic is Pearson's r between balance score and scale
  value across images (per shape and overall), the same statistic as the source, with a
  bootstrap interval over families. Shown beside the aggregate human r and beside the
  range of individual human r.
- **Dose:** the share of pairs in which the more balanced layout is chosen, by size of the
  score difference (0-12, 12-25, 25-40, 40+), and separately for pairs with both scores
  under 20, where the source reports a plateau.
- Also reported: the same r using the centre-of-mass deviation instead of the score.

---

## E2. Two objects in a frame: the contested null

**Citation.** Leyssen, M. H. R., Linsen, S., Sammartino, J., & Palmer, S. E. (2012).
Aesthetic preference for spatial composition in multiobject pictures. *i-Perception,
3*(1), 25-49. Experiment 5.

### Source design (pp.43-45, read in full)
- 20 participants. On each trial two framed pictures of the same two objects in the same
  left/right order; "choose the image that they found most aesthetically pleasing".
  288 trials.
- Frame 680 x 430 px, a wall above and a floor below, objects standing on the floor. Six
  object positions at 45, 135 and 225 px either side of centre (one unit = 90 px).
- A picture is **balanced** when the two objects are equidistant from the centre. Balance
  is purely geometric: no size or weight term.
- Balance comparisons hold the distance between the objects fixed and shift the pair so
  its midpoint is 90 px (13% of the width) off-centre: (-45, +45) against (-135, -45) or
  (+45, +135); and (-135, +135) against (-225, +45) or (-45, +225).
- Distance comparisons hold balance fixed and change the gap between the objects.
- Objects: colour photographs of everyday things in four sets, each giving semantically
  related pairs (shoes and slippers) and unrelated pairs (cheese and a football helmet).

### Human result
- **Balance.** "Participants did not prefer the pictures that showed balance over those
  that were unbalanced more often than expected by chance for any quartet, F(1, 19) < 1
  for all quartets" (*printed*, p.46). No proportion, SD or SE is printed.
- The proportions exist only as bars in Figure 14b: about **.55 for related and .51 for
  unrelated pairs, .53 overall**; the eight bars run from .48 to .56 (*digitised* with
  `scripts/digitise_figures.py`, about +/- .006).
- No interval can be computed from the paper. What follows from F(1,19) < 1 is that in
  each object set the mean lies within one standard error of .50, i.e. |d| < 0.22
  (*derived*, assuming one-sample tests).
- **Distance, the effect that did appear:** related objects were preferred closer together
  (about .82 choosing the smaller distance; F(1,19) = 217.6, 22.4, 17.5, 17.7 for the four
  sets), unrelated objects were not (about .46; two sets reliably preferred the larger
  distance) (*printed* F values, *digitised* proportions).
- **Why "contested".** In the same paper a centred group of objects *was* preferred
  (Experiment 4, F(4,56) = 8.66), and a regression in Experiment 3 found a weak balance
  term. Wilson & Chatterjee found a strong balance relation with abstract elements.
  Samuel & Kerzel (2013, *i-Perception* 4:57-77), with two black rectangles and ratings,
  report a small effect of the centre of mass being off-centre (*reader*).

### Our stimuli (`src/aesx/experiments/multiobject.py`)
- Same frame size, positions, shift and comparisons as the source. Flat wall and floor
  colours, a dark border, two shapes standing on the floor.
- **The objects are two different plain shapes in two different colours** (dev: disc,
  square, triangle, star; test: pentagon, hexagon, diamond, cross, dome, trapezoid), about
  80 px across.
- Per unit (two shapes, two colours, a left/right order): 4 balance pairs at the source's
  90 px shift; 4 dose pairs at 45 and 135 px; 2 distance pairs; 1 identical control.
  Dev 8 units (80 pairs), test 30 units (300 pairs, 120 of them at the anchor).

**Deviations from the source, and what they cost.**
1. **Abstract shapes instead of photographs of things.** The source's authors restrict
   their claim to meaningful objects and say abstract-element studies do not address
   their question. So the human figure of .53 is an anchor for *this layout and this
   shift*, not for these exact stimuli. This is the weakest link in the set, and it is
   unavoidable under the code-only rule: photographs cannot be regenerated.
2. With abstract shapes there are no related and unrelated pairs, so the source's
   positive control (the distance effect for related objects) has no counterpart. The
   distance pairs are kept as a descriptive extra.
3. The 45 and 135 px shifts have no human data. They are there only to show whether a
   model's response grows with the size of the shift.

An alternative the owner may prefer: use the schematic icons built for E3 (cup, teapot,
bottle, goblet...) in related and unrelated pairs. That restores "meaningful objects" and
the positive control, at the cost of leaving purely abstract compositions.

### Model counterpart (`aesx.effects.multiobject_effects`)
- **Primary:** the share of 90 px pairs in which the balanced picture is chosen, with a
  bootstrap interval over units. Compared with the human .53 and the .48 to .56 range of
  the source's eight bars.
- **Dose:** the same share at 45, 90 and 135 px.
- Split by shift direction and by inter-object distance; the distance pairs separately.

---

## E3. One object in a frame: centre bias, inward bias, mirror flips

**Citation.** Palmer, S. E., Gardner, J. S., & Wickens, T. D. (2008). Aesthetic issues in
spatial composition: Effects of position and direction on framing single objects.
*Spatial Vision, 21*(3-5), 421-449. Experiments 1 and 2.

### Source design (pp.425-436, read in full)
- A single object on a black floor against a white wall, horizon on the horizontal
  midline, in a 4:3 frame. Two pictures of the same object per trial; press a button for
  the one preferred. An object's position is the midpoint between its leftmost and
  rightmost points.
- **Experiment 1** (N = 9): ten rendered objects (man, woman, car, boat, cat; chair,
  teapot, flower, windmill, telescope) facing left, right or front, at 25, 50 and 75% of
  the frame width.
- **Experiment 2** (18 run, 17 analysed): six objects (man, flower, teapot, rocking horse,
  wolf, jeep) at seven positions from 25 to 75%. Two kinds of pair:
  *opposite-facing*, the same object at the same position reflected about its own centre
  (an in-place mirror flip); and *same-facing*, the same view at two different positions.

### Human result
**In-place mirror flip (Exp 2, Figure 5).** Percentage choosing each view over its
reflection at the same position (*digitised*; the two curves sum to 100):

| Position (% of width) | 25 | 33 | 42 | 50 | 58 | 67 | 75 |
|---|---|---|---|---|---|---|---|
| Right-facing chosen | 87 | 69 | 70 | 57 | 29 | 30 | 24 |
| Inward-facing chosen | 87 | 69 | 70 | (centre) | 71 | 71 | 76 |

Mean over the six off-centre positions: **inward-facing chosen about 74%**. Printed tests:
position F(6, 96) = 38.11, p < .001; linear trend F(1, 16) = 67.68; no quadratic trend.
At the centre the right-facing view was chosen 57% of the time, which was not reliable in
Experiment 2 (F < 1) but was in Experiment 1 (F(1, 8) = 11.46 at the centre).

**Position (Exp 2, Figure 6).** Percentage of same-facing comparisons won at each
position (*digitised*), with left-facing objects mirrored so the first column is the
position where the object faces furthest *into* the frame:

| | in, 25% off | in, 17% | in, 8% | centre | out, 8% | out, 17% | out, 25% |
|---|---|---|---|---|---|---|---|
| Won | 54 | 63 | 68 | 65 | 52 | 37 | 23 |

(The seven points of a curve should sum to 350 and sum to 357 and 365 in the figure, so
single points are good to about two percentage points.)

Printed tests: facing x position F(6, 96) = 19.05; linear and quadratic trends both
reliable for each facing (F(1, 16) between 24 and 43). The curve is a centre bias plus an
inward bias: the best position is slightly off-centre on the side the object faces away
from.

**Centre bias with symmetrical objects (Exp 1).** Front views were chosen more often at
the centre than at either quarter line (F(1, 8) = 11.99, p < .01); left and right did not
differ (F(1, 8) = 2.33). Figure 3 plots these, but its front-view points do not sum to
the value a win percentage must, so no proportion is quoted for them.

### Our stimuli (`src/aesx/experiments/framing.py`, `src/aesx/icons.py`)
- 512 x 384 px, white wall, black floor, horizon on the midline, one object standing on
  the floor. Seven positions as in Experiment 2.
- **Objects are flat schematic icons drawn in code** (car, duck, chair, dog, snail,
  locomotive, person, desk lamp, watering can...) plus abstract directed shapes (arrow,
  wedge, notched disc, chevron). Icons are split so no test icon is used in development.
- *flip* pairs: each directed icon at each of the seven positions against its in-place
  reflection. Reference = the inward-facing view (right-facing at the centre).
- *position* pairs: all 21 pairs of positions for one facing of an icon.
- *centre* pairs: a symmetrical icon or shape at 25, 50 and 75%.
- Dev: 28 flip + 84 position + 12 centre pairs. Test: 168 flip (12 icons x 2 colour and
  size variants) + 168 position (8 icons) + 54 centre (18 icons) = 390 pairs.

**Deviations from the source.**
1. Schematic icons instead of rendered three-dimensional objects. The effect depends on
   the object having a front; the abstract shapes test whether a bare pointing direction
   is enough, and are reported separately.
2. A whole-picture mirror flip is *not* tested by the flip pairs: reflecting the whole
   picture moves the object and reverses it together, which leaves inward/outward
   unchanged. In this design the whole-picture flip appears only at the centre position,
   where the two coincide.

### Model counterpart (`aesx.effects.framing_effects`)
- **Primary:** share of off-centre flip pairs in which the inward-facing view is chosen
  (human: about 74%), and the seven-point curve of P(right-facing chosen) against
  position (human: Figure 5).
- **Dose:** the same share at 8, 17 and 25% from the centre.
- Position: the seven-point win profile (human: Figure 6) and its in-minus-out difference.
- Centre: share choosing the centre over a quarter line for symmetrical objects.

---

## E4. Colour swap in a grid composition

**Citation.** Locher, P., Overbeeke, K., & Stappers, P. J. (2005). Spatial balance of
color triads in the abstract art of Piet Mondrian. *Perception, 34*(2), 169-189.

**This lead does not meet the brief's criteria as written. It is included in a reduced
form, and the owner should decide whether that form is acceptable (see "Decision").**

### Source design
(Abstract read by me; everything else is *reader*: a delegated reader read the full text
on ResearchGate, whose text layer is garbled, and I could not open it to check.)
- Six grid compositions **adapted from six specific Mondrian paintings** (1928-1935), each
  with three coloured areas; area 1 is the largest. All six assignments of red, blue and
  yellow to the three areas were shown: 36 stimuli. Fixed colours: red (220, 0, 0), blue
  (0, 0, 152), yellow (255, 223, 0), lines (1, 1, 1), field (231, 231, 231).
- Tasks: mark the balance centre; rate each coloured area's visual weight from 1 to 10.
  **No preference, forced-choice or which-is-the-original judgement was collected**, and
  participants were told not to let liking influence them.
- Participants: 60 in Experiment 1 (45 untrained, 15 design-trained), 23 in Experiment 2.

### Human result (*reader*, unchecked)
- **Weight by colour.** The largest area was rated heavier when red than when yellow, by
  about 0.6 to 1.1 points on the 1-10 scale, reliably in four of six compositions (those
  where it covered 9, 9, 16 and 23% of the field). Blue fell between and was not reliably
  different from either. Where the largest area covered about 65% of the field, untrained
  viewers showed no colour effect. Printed means have standard errors of 0.16 to 0.27.
- **Balance centre.** Marked centres moved by 10 to 17% of the display width between the
  original and its colour-swapped versions, more for design-trained viewers. This is
  defined against the original and is never tested against placement noise.
- Supporting literature on colour and apparent weight is itself mixed: Pinkerton &
  Humphrey (1974, N = 20) found red heaviest and yellow lightest; Alexander & Shansky
  (1976, N = 20) found weight driven by chroma and value, with yellow *heavier* than blue
  at one chroma level.

### What can and cannot be regenerated
| Part of the source | Regenerable in code? | Forced choice? | Human effect size? |
|---|---|---|---|
| Balance-centre shift from the original | No: needs the six real layouts | No | Yes, but original-relative |
| Weight of the largest area by its colour | Yes: any three-colour grid | Converts to "which looks heavier" | Rating-scale difference only; no choice proportion |
| Preference between colour versions | Yes | Yes | **None: never measured** |

### Our stimuli (`src/aesx/experiments/colour.py`, `src/aesx/grid.py`)
- 512 x 512 px random recursive partitions (5 to 9 cells, lines 2% of the side) in the
  source's colours. **No painting's layout is copied.** Three cells are coloured: one
  "largest area" at one of three sizes (8-13%, 16-24%, 55-70% of the field) and two small
  areas (1-8% each).
- A pair is one layout in two of the source's six colour versions that differ by a single
  swap between the largest area and one small area: red vs yellow, red vs blue, or blue
  vs yellow in the largest area. Reference = the version with the colour ranked heavier
  (red > blue > yellow) in the largest area.
- Dev 12 layouts (72 pairs), test 36 layouts (216 pairs; 72 per contrast, 72 per size).

### Model counterpart
Two questions are asked on every pair:
1. **Weight** (the source's variable): "In which of these two images does the largest
   coloured rectangle look visually heavier?" Statistic: share of pairs in which the
   reference (heavier-ranked colour) is named. Human anchor: **direction only**, for red
   vs yellow at the two smaller sizes; and "no effect" at the largest size for untrained
   viewers. Dose: the three sizes.
2. **Preference** (the project's standard question). **No human anchor exists.** Reported
   descriptively, never scored against people.

---

## E5. Altered proportions in a grid composition

**Citation.** McManus, I. C., Cheema, B., & Stoker, J. (1993). The aesthetics of
composition: A study of Mondrian. *Empirical Studies of the Arts, 11*(2), 83-94.

**This lead cannot be re-run under the code-only rule.** What is built is a control with
no human anchor; the owner should decide whether to keep it.

### Source design and result (*reader*, unchecked: read from page scans on ResearchGate)
- 25 real Mondrian paintings (M). Every line coded as a proportion between two other
  lines or edges; altered versions made by logit-transforming each proportion and adding
  or subtracting 0.5 (P1) or 1.0 (P2) at random.
- 52 participants, 75 pairs each (M vs P1, M vs P2, P1 vs P2), six-point preference scale
  collapsed to a choice. Participants were told one picture "would probably be an actual
  Mondrian".
- The original was chosen in 55.8% of M vs P1 and 54.9% of M vs P2 judgements; P1 over P2
  in 51.7%. Per participant: 40.5 of 75 correct (SD 8.14), t = 2.63 against 37.5.
  No dose response (P1 vs P2 alteration size: F(1, 100) = 0.20).
- Replication (McManus & Gesiak 2014, poster, N = 277): 54.7%.

### Why it does not transfer
Every scored trial is "nearer the artist's original". A generated grid has no original
that an artist chose, so "share choosing the original" has no meaning, and copying the 25
real layouts is ruled out by the brief. Three searches for a study with fully generated
grids, a preference choice and a printed effect size found none.

### What is built instead (`src/aesx/experiments/proportion.py`)
- The same alteration applied to random partitions: G (as generated), G1 (logit shift
  0.5), G2 (1.0); same topology, same coloured cells; pairs G vs G1, G vs G2, G1 vs G2.
  Dev 24 sets (72 pairs), test 67 sets (201 pairs).
- **Use: a control.** Nothing privileges G, so an observer with no view about the
  generator's proportions should be at 50%. A model that prefers the less-altered member
  is responding to something about more even divisions, not reproducing the McManus
  effect. Reported descriptively; the human 55% is quoted for context only and is **not**
  an anchor.

---

## Decision needed from the owner (Gate 1)

The brief requires every experiment to have code-regenerable stimuli, a forced choice,
and a human effect size, and requires the set to cover colour swaps. For the two grid
leads those requirements cannot all be met at once:

| Option | What it means |
|---|---|
| **A (recommended).** Keep E4 as the weight question with a direction-only anchor; keep E5 as an unanchored control; headline findings rest on E1, E2, E3. | Colour swaps are covered, honestly labelled. Four experiments carry human effects (E1-E3 fully, E4 in direction). |
| B. Drop E5; keep E4 as in A. | Leaner. Loses the control. |
| C. Replace E5 with an anchored proportion experiment on generated figures (for example paired comparisons of rectangle proportions, where the golden-section preference is itself contested). | A fifth anchored experiment, but another literature pass, and no longer a grid composition. |
| D. Allow line layouts of the specific paintings to be re-drawn in code for E4 and E5. | Makes both source effects testable as published. **Contradicts the brief's rule against copies of specific paintings**; listed only for completeness. |
