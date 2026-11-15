"""Named subsets of a manifest.

The Gate 2 pilot uses about 40 manipulation pairs per experiment. Pairs are taken
as whole clusters (a family, a unit, a layout) so that statistics needing a
complete cluster, such as E1's within-family scale values, can still be computed.
"""
from __future__ import annotations

from .manifest import Pair

PILOT_PAIRS = 40
PILOT_IDENTICAL = 8


def pilot_subset(pairs: list[Pair], n: int = PILOT_PAIRS, n_ident: int = PILOT_IDENTICAL) -> list[Pair]:
    manip = [p for p in pairs if p.kind == "manipulation"]
    ident = [p for p in pairs if p.kind == "identical"]
    if not manip:
        return []
    if manip[0].experiment == "framing":
        # every dev icon's seven flip pairs (the anchored comparison) and every symmetrical
        # icon's three centre pairs; the 21-pair position designs are left to the main run
        chosen = [p for p in manip if p.condition == "flip"][:28] + [p for p in manip if p.condition == "centre"][:12]
    else:
        chosen = []
        for cluster in dict.fromkeys(p.cluster for p in manip):
            members = [p for p in manip if p.cluster == cluster]
            if len(chosen) + len(members) > n:
                break
            chosen += members
    clusters = {p.cluster for p in chosen}
    ident = sorted(ident, key=lambda p: p.cluster not in clusters)  # controls from the chosen clusters first
    return chosen + ident[:n_ident]
