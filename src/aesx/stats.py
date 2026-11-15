"""Statistics shared by every experiment.

Model-side intervals are bootstrap intervals over stimuli (pairs). Human-side
intervals are whatever the paper prints, or are derived here from the printed
statistics; every derivation used is one of the small functions below so that
``docs/experiments.md`` can cite the exact formula.
"""
from __future__ import annotations

import math
from typing import Callable

import numpy as np
from scipy import stats as sps


# ---------------------------------------------------------------- bootstrap
def bootstrap_ci(
    values,
    stat: Callable[[np.ndarray], float] = np.mean,
    n_boot: int = 10_000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, float, float]:
    """Percentile bootstrap over stimuli. Returns (estimate, lo, hi)."""
    v = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(v), size=(n_boot, len(v)))
    boots = np.array([stat(v[i]) for i in idx])
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return float(stat(v)), float(lo), float(hi)


def bootstrap_ci_paired(
    x,
    y,
    stat: Callable[[np.ndarray, np.ndarray], float],
    n_boot: int = 10_000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, float, float]:
    """Bootstrap for a statistic of paired columns (e.g. a correlation), resampling stimuli."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    boots = np.array([stat(x[i], y[i]) for i in idx])
    boots = boots[np.isfinite(boots)]
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return float(stat(x, y)), float(lo), float(hi)


def pearson_r(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


# ------------------------------------------------- intervals for human data
def wilson_ci(k: float, n: float, alpha: float = 0.05) -> tuple[float, float, float]:
    """Wilson score interval for a single proportion k/n."""
    z = sps.norm.ppf(1 - alpha / 2)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return p, centre - half, centre + half


def mean_ci_from_sd(mean: float, sd: float, n: int, alpha: float = 0.05) -> tuple[float, float, float]:
    """t interval for a mean across participants, from printed mean, SD and N."""
    half = sps.t.ppf(1 - alpha / 2, n - 1) * sd / math.sqrt(n)
    return mean, mean - half, mean + half


def mean_ci_from_se(mean: float, se: float, n: int, alpha: float = 0.05) -> tuple[float, float, float]:
    half = sps.t.ppf(1 - alpha / 2, n - 1) * se
    return mean, mean - half, mean + half


def fisher_ci(r: float, n: int, alpha: float = 0.05) -> tuple[float, float, float]:
    """Fisher z interval for a Pearson correlation computed over n points."""
    z = math.atanh(r)
    half = sps.norm.ppf(1 - alpha / 2) / math.sqrt(n - 3)
    return r, math.tanh(z - half), math.tanh(z + half)


def d_from_one_sample_t(t: float, n: int) -> float:
    """Cohen's d (dz) for a one-sample or paired t test: d = t / sqrt(n)."""
    return t / math.sqrt(n)


def d_ci_one_sample(t: float, n: int, alpha: float = 0.05) -> tuple[float, float, float]:
    """Exact CI for dz from the non-central t distribution."""
    df = n - 1

    def ncp_for(p: float) -> float:
        lo, hi = t - 20, t + 20
        for _ in range(200):
            mid = (lo + hi) / 2
            if sps.nct.cdf(t, df, mid) > p:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    return t / math.sqrt(n), ncp_for(1 - alpha / 2) / math.sqrt(n), ncp_for(alpha / 2) / math.sqrt(n)


def t_from_mean_sd(mean: float, sd: float, n: int, mu0: float) -> float:
    return (mean - mu0) / (sd / math.sqrt(n))
