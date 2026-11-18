"""Exploratory, post hoc (2026-11-18): how the readout and the choice statistic shape the
comparison of model and human effects. See reports/readout_math.md for the derivations.

Uses only the local models' test runs, opened at Gate 3. No NVIDIA result is read.

For each local model and headline subset (two-image layout, "you" framing):
  E1  all balance pairs           (reference = the more balanced image)
  E2  90 px balance pairs         (reference = the balanced arrangement)
  E3  off-centre flip pairs       (reference = the inward-facing version)

it reports
  P_sign    share of pairs whose mean log-odds favours the reference: the pre-registered
            statistic of reports/main.md
  P_soft    mean over pairs of sigmoid(mean log-odds): the expected choice proportion of a
            temperature-1 chooser once position and label bias are removed
  P_cells   mean over presentations of the probability given to the reference: what a
            temperature-1 sampler chooses on average, bias included
  normal    Phi(mean/sd) of the pair log-odds: P_sign under a normal model of pairs
  samp_k    the pre-registered API statistic (sign of the mean smoothed log-odds, ties 1/2)
            when each presentation is answered by k samples from the model's own two-letter
            distribution; Monte Carlo mean (and SD) over 200 replications, k = 1, 2, 3
  glmm_k3   P_sign recovered from one simulated k = 3 sample set by a random-intercept logistic
            model, Phi(mu/tau): can sampled answers be put back on the log-probability scale?
  bias      median |position bias| (log-odds) over the subset's pairs

    uv run python scripts/readout_math.py          -> reports/readout_math.csv
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from scipy import optimize, special, stats

from aesx import analysis
from aesx.effects import manifest_table
from aesx.manifest import ROOT

MODELS = ("qwen3.5-0.8b", "minicpm-v-4.7-1b", "smolvlm2-2.2b", "internvl3.5-2b",
          "north-micro-vision", "qwen3.5-4b", "gemma-4-e2b")
REPS = 200
GH_X, GH_W = np.polynomial.hermite_e.hermegauss(40)  # nodes/weights for E over N(0, 1)
GH_W = GH_W / GH_W.sum()


def cells(model: str, meta: pd.DataFrame) -> dict[str, dict[str, np.ndarray]]:
    """Per subset: arrays (pairs x 4) of log-odds toward the reference, order sign and label sign."""
    df = analysis.load_results(ROOT / "runs" / "test" / model / "results.jsonl")
    d = df[(df.task == "prefer") & (df.layout == "two") & (df.framing == "you")].merge(meta, on="pair_id")
    d = d[d.kind == "manipulation"].copy()
    d["lo_ref"] = np.where(d["first"] == "ref", d.lo_first, -d.lo_first)
    d["o"] = np.where(d["first"] == "ref", 1.0, -1.0)  # +1: reference shown first
    ref_letter = np.where(d["first"] == "ref", d["labels"].str[0], d["labels"].str[1])
    d["g"] = np.where(ref_letter == "A", 1.0, -1.0)  # +1: reference labelled A
    subsets = {
        "E1": d[d.experiment == "apb"],
        "E2": d[(d.experiment == "multiobject") & (d.condition == "balance")],
        "E3": d[(d.experiment == "framing") & (d.condition == "flip") & (d.p_pos_ref != 50)],
    }
    out = {}
    for key, s in subsets.items():
        s = s.sort_values(["pair_id", "first", "trial_id"])
        n4 = s.groupby("pair_id").size()
        s = s[s.pair_id.isin(n4[n4 == 4].index)]
        k = s.pair_id.nunique()
        out[key] = {name: s[name].values.reshape(k, 4) for name in ("lo_ref", "o", "g", "lo_first")}
    return out


def sampled_sign(lo_ref: np.ndarray, k: int, rng) -> np.ndarray:
    """The pre-registered API statistic under k samples per presentation, for REPS replications."""
    p = special.expit(lo_ref)
    c = rng.binomial(k, np.broadcast_to(p, (REPS,) + p.shape))
    lo = np.log((c + 0.5) / (k - c + 0.5))
    pref = lo.mean(axis=2)
    choice = np.where(np.abs(pref) < 1e-12, 0.5, (pref > 0).astype(float))
    return choice.mean(axis=1)


def fit_glmm(counts: np.ndarray, k: int, o: np.ndarray, g: np.ndarray) -> tuple[float, float, float, float]:
    """Random-intercept logistic model for choose-reference counts:
    logit P = mu + u_i + b*o + a*g,  u_i ~ N(0, tau^2); marginal likelihood by Gauss-Hermite.
    Returns (mu, tau, b, a)."""

    def nll(theta):
        mu, b, a, log_tau = theta
        tau = np.exp(log_tau)
        eta = mu + b * o + a * g  # pairs x 4
        eta = eta[:, :, None] + tau * GH_X[None, None, :]  # pairs x 4 x nodes
        ll = counts[:, :, None] * -np.logaddexp(0, -eta) + (k - counts[:, :, None]) * -np.logaddexp(0, eta)
        per_node = ll.sum(axis=1)  # pairs x nodes
        m = per_node.max(axis=1, keepdims=True)
        return -(np.log((np.exp(per_node - m) * GH_W).sum(axis=1)) + m[:, 0]).sum()

    res = optimize.minimize(nll, x0=np.array([0.0, 0.0, 0.0, 0.0]), method="L-BFGS-B")
    mu, b, a, log_tau = res.x
    return float(mu), float(np.exp(log_tau)), float(b), float(a)


def main() -> int:
    meta = manifest_table("test")
    rng = np.random.default_rng(20261118)
    rows = []
    for model in MODELS:
        for key, c in cells(model, meta).items():
            lo, o, g = c["lo_ref"], c["o"], c["g"]
            pref = lo.mean(axis=1)
            row = {
                "model": model, "subset": key, "pairs": len(pref),
                "P_sign": float(np.mean(np.where(pref > 0, 1.0, np.where(pref == 0, 0.5, 0.0)))),
                "P_soft": float(special.expit(pref).mean()),
                "P_cells": float(special.expit(lo).mean()),
                "normal": float(stats.norm.cdf(pref.mean() / pref.std(ddof=1))),
                "mean_pref": float(pref.mean()), "sd_pref": float(pref.std(ddof=1)),
                "bias": float(np.median(np.abs(c["lo_first"].mean(axis=1)))),
            }
            for kk in (1, 2, 3):
                s = sampled_sign(lo, kk, rng)
                row[f"samp_{kk}"], row[f"samp_{kk}_sd"] = float(s.mean()), float(s.std(ddof=1))
            counts = rng.binomial(3, special.expit(lo)).astype(float)
            mu, tau, b, a = fit_glmm(counts, 3, o, g)
            row.update({"glmm_k3": float(stats.norm.cdf(mu / tau)), "glmm_mu": mu, "glmm_tau": tau, "glmm_b": b})
            rows.append(row)
            print(f"{model:19s} {key}  n={len(pref):3d}  sign {row['P_sign']:.3f}  soft {row['P_soft']:.3f}  "
                  f"cells {row['P_cells']:.3f}  normal {row['normal']:.3f}  samp k1/2/3 {row['samp_1']:.3f}/"
                  f"{row['samp_2']:.3f}/{row['samp_3']:.3f}  glmm {row['glmm_k3']:.3f}  |bias| {row['bias']:.2f}",
                  flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "reports" / "readout_math.csv", index=False, float_format="%.4f")
    print(f"{len(out)} rows -> reports/readout_math.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
