"""Turn pairs into fully counterbalanced, model-agnostic trials.

Every pair is shown in both orders, and the two answer letters are assigned to
the two positions both ways, so position bias (first/left vs second/right) and
label bias (A vs B) are separable from preference:

    first ∈ {ref, alt}  ×  labels ∈ {(A,B), (B,A)}            = 4 cells
    × framing ∈ {you, most}  ×  layout ∈ {two, sbs}

A trial is a list of segments (text and image slots) that each model backend
maps onto its own chat template. Prompt wording lives only in this file and is
stamped with PROMPT_VERSION; it is developed on dev stimuli and then frozen.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import product

from .manifest import Pair

# dev-1: instruction ended "...: A or B."            (Gate 1 checks, runs/dev)
# dev-2: the same, followed by "Answer:" on a new line (pilot, runs/pilot). The suffix
#        keeps models that would otherwise start a sentence on the two permitted answers.
PROMPT_VERSION = "dev-2"

LAYOUTS = ("two", "sbs")  # two separate images | one side-by-side image
FRAMINGS = ("you", "most")
LABELINGS = (("A", "B"), ("B", "A"))

PREFER_Q = {
    "you": "Which of these two images do you find more pleasing to look at?",
    "most": "Which of these two images would most people find more pleasing to look at?",
}
# Same/different is asked in both polarities so a yes-bias cancels.
SAMEDIFF_Q = {
    "identical": "Are these two images exactly identical?",
    "different": "Is there any difference between these two images?",
}
# Experiment-specific forced-choice questions asked in addition to preference, where the
# source's dependent variable was not preference. Keyed by experiment, then task name.
EXTRA_Q = {
    "colour": {"weight": "In which of these two images does the largest coloured rectangle look visually heavier?"},
}
SBS_INTRO = "This picture shows two images side by side. The left one is labelled {l1} and the right one is labelled {l2}."
LETTER_INSTR = "Answer with one letter only: {l1} or {l2}.\nAnswer:"
YESNO_INSTR = "Answer with one word only: Yes or No.\nAnswer:"


@dataclass
class Trial:
    trial_id: str
    pair_id: str
    experiment: str
    task: str  # "prefer" | "samediff"
    framing: str  # prefer: you|most ; samediff: identical|different
    layout: str  # "two" | "sbs"
    first: str  # which pair member is first / on the left: "ref" | "alt"
    labels: tuple[str, str]  # letter for the first image, letter for the second
    image_paths: tuple[str, str]  # (first, second), relative to project root
    segments: list  # [["text", str] | ["image", 0|1] | ["sbs", None]]
    answers: tuple[str, str]  # prefer: (letter of first, letter of second); samediff: ("Yes", "No")
    prompt_version: str = PROMPT_VERSION

    def to_json(self) -> dict:
        return asdict(self)


def _segments(layout: str, labels: tuple[str, str], question: str, instr: str) -> list:
    l1, l2 = labels
    if layout == "two":
        return [
            ["text", f"Image {l1}:"],
            ["image", 0],
            ["text", f"Image {l2}:"],
            ["image", 1],
            ["text", f"{question} {instr}"],
        ]
    if layout == "sbs":
        return [["sbs", None], ["text", f"{SBS_INTRO.format(l1=l1, l2=l2)} {question} {instr}"]]
    raise ValueError(layout)


def build_trials(
    pairs: list[Pair],
    tasks=("prefer", "samediff"),
    layouts=LAYOUTS,
    framings=FRAMINGS,
) -> list[Trial]:
    trials: list[Trial] = []
    for p in pairs:
        # An identical pair has no "other order", but it keeps both label cells.
        firsts = ("ref",) if p.kind == "identical" else ("ref", "alt")
        for layout, first, labels in product(layouts, firsts, LABELINGS):
            paths = (p.ref, p.alt) if first == "ref" else (p.alt, p.ref)
            common = dict(pair_id=p.pair_id, experiment=p.experiment, layout=layout, first=first,
                          labels=labels, image_paths=paths)
            tag = f"{p.pair_id}|{layout}|{first}|{labels[0]}{labels[1]}"
            if "prefer" in tasks:
                for fr in framings:
                    instr = LETTER_INSTR.format(l1=labels[0], l2=labels[1])
                    trials.append(Trial(trial_id=f"{tag}|prefer|{fr}", task="prefer", framing=fr,
                                        segments=_segments(layout, labels, PREFER_Q[fr], instr),
                                        answers=labels, **common))
            if "prefer" in tasks:  # extra questions ride along with the preference task
                for task, q in EXTRA_Q.get(p.experiment, {}).items():
                    instr = LETTER_INSTR.format(l1=labels[0], l2=labels[1])
                    trials.append(Trial(trial_id=f"{tag}|{task}|plain", task=task, framing="plain",
                                        segments=_segments(layout, labels, q, instr), answers=labels, **common))
            if "samediff" in tasks:
                for pol, q in SAMEDIFF_Q.items():
                    trials.append(Trial(trial_id=f"{tag}|samediff|{pol}", task="samediff", framing=pol,
                                        segments=_segments(layout, labels, q, YESNO_INSTR),
                                        answers=("Yes", "No"), **common))
    return trials
