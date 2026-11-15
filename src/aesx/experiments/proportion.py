"""E5. Altered proportions in a grid composition: after McManus, Cheema & Stoker
(1993), Empirical Studies of the Arts 11:83-94.

Source: 25 real Mondrian paintings (M). Each line was coded as a proportion
between two other lines or edges; two altered versions were made by logit-
transforming every proportion and adding or subtracting 0.5 (P1) or 1.0 (P2) at
random. 52 participants saw M vs P1, M vs P2 and P1 vs P2 and chose the one they
preferred; the original was chosen 55.8 % and 54.9 % of the time, and P1 over P2
51.7 %.

THE SOURCE EFFECT IS DEFINED AGAINST THE ARTIST'S ORIGINAL, which cannot be used
here. What is generated instead is the same alteration applied to random
partitions: G (as generated), G1 (+/-0.5) and G2 (+/-1.0), same topology, same
coloured cells. There is no privileged original, so there is NO human anchor;
see docs/experiments.md. The pairs serve as a control: a preference for the
less-altered member would mean the observer likes something about the
generator's proportions, not about any artist's.
"""
from __future__ import annotations

import numpy as np

from .. import grid
from ..manifest import Pair, rng_for, save_pair

NAME = "proportion"
TITLE = "E5 Altered proportions (after McManus et al. 1993; no human anchor)"
UNITS = {"dev": 24, "test": 67}
DELTAS = {"G1": 0.5, "G2": 1.0}  # logit shifts, as in the source
COMPARISONS = (("G", "G1", "G_vs_G1"), ("G", "G2", "G_vs_G2"), ("G1", "G2", "G1_vs_G2"))


def caption(p: Pair) -> str:
    return f"{p.condition.replace('_', ' ')}  ({p.params['n_cells']} cells)"


def make_set(rng: np.random.Generator):
    """A partition and its two altered versions, none with a cell thinner than MIN_SIDE."""
    for _ in range(10_000):
        g = grid.random_tree(rng, int(rng.integers(5, 10)))
        versions = {"G": g, "G1": grid.alter(g, DELTAS["G1"], rng), "G2": grid.alter(g, DELTAS["G2"], rng)}
        if all(grid.min_side(t) >= grid.MIN_SIDE for t in versions.values()):
            return versions
    raise RuntimeError("no partition survives alteration")


def generate(split: str, n_units: int) -> list[Pair]:
    out = f"stimuli/{NAME}/{split}"
    pairs: list[Pair] = []
    for u in range(n_units):
        rng = rng_for(NAME, split, u)
        versions = make_set(rng)
        cs = grid.cells(versions["G"])
        keys = sorted(cs, key=lambda k: grid.area(cs[k]))
        # three coloured cells drawn from the smaller two-thirds of the cells, as is typical of the style
        pool = keys[: max(3, (2 * len(keys)) // 3)]
        chosen = [pool[int(i)] for i in rng.choice(len(pool), size=3, replace=False)]
        fills = dict(zip(chosen, rng.permutation(["R", "B", "Y"]).tolist()))
        images = {v: grid.render(t, fills) for v, t in versions.items()}
        path = {v: f"{out}/g{u:03d}_{v}.png" for v in versions}
        fam = f"{NAME}-{split}-g{u:03d}"
        base = {"n_cells": len(cs), "fills": fills,
                "proportions": {v: [round(p, 4) for p in grid.proportions(t)] for v, t in versions.items()}}
        for ref, alt, cond in COMPARISONS:
            p = Pair(experiment=NAME, pair_id=f"{fam}-{ref}_{alt}", split=split, index=u, kind="manipulation",
                     condition=cond, ref=path[ref], alt=path[alt],
                     dose=DELTAS[alt] - DELTAS.get(ref, 0.0), human_direction="none", cluster=fam,
                     params={**base, "version_ref": ref, "version_alt": alt})
            pairs.append(save_pair(p, images[ref], images[alt]))
        if u % 3 == 0:
            v = list(versions)[int(rng.integers(3))]
            p = Pair(experiment=NAME, pair_id=f"{fam}-ident-{v}", split=split, index=u, kind="identical",
                     condition="identical", ref=path[v], alt=path[v], dose=0.0, human_direction="none", cluster=fam,
                     params={**base, "version_ref": v, "version_alt": v})
            pairs.append(save_pair(p, images[v], images[v]))
    return pairs
