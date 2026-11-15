"""Pinned local models (Tier 1).

Each entry pins a Hugging Face repo to an exact commit. Commits and licences were
read from the Hub on 2026-11-14; the commit actually loaded is written into every
run's ``run.json`` so a mismatch is visible.
"""
from __future__ import annotations

MODELS: dict[str, dict] = {
    "smolvlm2-500m": dict(
        repo="HuggingFaceTB/SmolVLM2-500M-Video-Instruct",
        revision="4cde9d208e19519c36917aa170fffc7e381aa0ad",
        licence="Apache-2.0", family="SmolVLM (Hugging Face)", params_b=0.51,
    ),
    "qwen3.5-0.8b": dict(
        repo="Qwen/Qwen3.5-0.8B",
        revision="2fc06364715b967f1860aea9cf38778875588b17",
        licence="Apache-2.0", family="Qwen (Alibaba)", params_b=0.87,
        template_kwargs={"enable_thinking": False},
    ),
    "internvl3.5-2b": dict(
        repo="OpenGVLab/InternVL3_5-2B-HF",
        revision="3f301ffcf3dcbb47893afae6650ea3e78d96fb6d",
        licence="Apache-2.0", family="InternVL (OpenGVLab)", params_b=2.35,
    ),
    "minicpm-v-4.7-1b": dict(
        repo="openbmb/MiniCPM-V-4.7-1B",
        revision="ad9bf379feb71204c888b22923d63322452407f9",
        licence="Apache-2.0", family="MiniCPM-V (OpenBMB)", params_b=1.55,
    ),
    "north-micro-vision": dict(
        repo="CohereLabs/North-Micro-Vision-Instruct",
        revision="fa548d9aa62c1220bfd21fc6cfc465f1bd2a1a40",
        licence="Apache-2.0", family="North (Cohere)", params_b=2.48,
    ),
    "qwen3.5-4b": dict(
        repo="Qwen/Qwen3.5-4B",
        revision="851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a",
        licence="Apache-2.0", family="Qwen (Alibaba)", params_b=4.66,
        template_kwargs={"enable_thinking": False},
    ),
    "gemma-4-e2b": dict(
        repo="google/gemma-4-E2B-it",
        revision="4adf15748de9e1a0097b6274cee9c15836c41c37",
        licence="Apache-2.0", family="Gemma (Google)", params_b=5.12,
    ),
}

_META = ("licence", "family", "params_b")


def load(name: str):
    from .hf import HFScorer

    cfg = dict(MODELS[name])
    meta = {k: cfg.pop(k) for k in _META}
    scorer = HFScorer(name=name, **cfg)
    scorer.spec.update(meta)
    return scorer
