"""From raw trial results to per-pair scores and the control statistics.

Definitions (all log-odds are natural-log differences between the two answer
tokens, so 0 means indifference):

  lo_first   log P(answer naming the first/left image) - log P(answer naming the second/right)
  lo_ref     the same quantity signed toward the reference member of the pair
  pref       mean of lo_ref over the 4 counterbalanced cells of a pair: the graded,
             bias-cancelled preference for the reference
  pos_bias   mean of lo_first over cells: preference for whatever is shown first
  label_bias mean log-odds toward the letter "A" regardless of what it names
  diff       same/different task: mean log-odds of answering "these differ"
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .stats import bootstrap_ci

# A trial counts as "off-menu" (the local-model analogue of a refusal) when the
# two permitted answers together hold less than this much next-token probability.
OFF_MENU_MASS = 0.5


def load_results(path: Path) -> pd.DataFrame:
    rows = []
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    df = pd.DataFrame(rows).drop_duplicates("trial_id", keep="last")
    df["lo_first"] = df["lp_first"] - df["lp_second"]
    df["off_menu"] = df["mass"] < OFF_MENU_MASS
    return df


def prefer_by_pair(df: pd.DataFrame, task: str = "prefer") -> pd.DataFrame:
    """One row per (pair, layout, framing) with bias-cancelled preference for the reference.

    ``task`` selects the forced-choice question: "prefer", or an extra question such as "weight".
    """
    d = df[df.task == task].copy()
    d["lo_ref"] = np.where(d["first"] == "ref", d.lo_first, -d.lo_first)
    d["lo_A"] = np.where(d["labels"].str[0] == "A", d.lo_first, -d.lo_first)
    d["hard_ref"] = (d.lo_ref > 0).astype(float)
    d["soft_ref"] = 1 / (1 + np.exp(-d.lo_ref))
    g = d.groupby(["experiment", "pair_id", "layout", "framing"], sort=False)
    out = g.agg(
        pref=("lo_ref", "mean"),
        pos_bias=("lo_first", "mean"),
        label_bias=("lo_A", "mean"),
        p_ref_hard=("hard_ref", "mean"),  # share of raw trials choosing the reference
        p_ref_soft=("soft_ref", "mean"),  # mean probability given to the reference
        p_first_hard=("lo_first", lambda s: float((s > 0).mean())),
        off_menu=("off_menu", "mean"),
        cells=("lo_ref", "size"),
    ).reset_index()
    out["choice_ref"] = (out.pref > 0).astype(float)  # bias-cancelled forced choice
    return out


def samediff_by_pair(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (pair, layout) with mean log-odds of reporting a difference."""
    d = df[df.task == "samediff"].copy()
    lo_yes = d.lo_first  # answers are ("Yes", "No")
    d["lo_diff"] = np.where(d.framing == "different", lo_yes, -lo_yes)
    d["lo_yes"] = lo_yes
    g = d.groupby(["experiment", "pair_id", "layout"], sort=False)
    return g.agg(diff=("lo_diff", "mean"), yes_bias=("lo_yes", "mean"), off_menu=("off_menu", "mean")).reset_index()


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    """P(score of a changed pair > score of an identical pair), ties counted half."""
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    gt = (pos[:, None] > neg[None, :]).mean()
    eq = (pos[:, None] == neg[None, :]).mean()
    return float(gt + 0.5 * eq)


def auc_ci(pos, neg, n_boot: int = 5000, seed: int = 0) -> tuple[float, float, float]:
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    rng = np.random.default_rng(seed)
    boots = [auc(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(n_boot)]
    lo, hi = np.quantile(boots, [0.025, 0.975])
    return auc(pos, neg), float(lo), float(hi)


def mean_ci(values, seed: int = 0) -> tuple[float, float, float]:
    return bootstrap_ci(np.asarray(values, float), np.mean, seed=seed)
