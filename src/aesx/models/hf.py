"""Local open-weight models through Hugging Face transformers.

Scoring is one forward pass per trial: the next-token distribution after the
generation prompt is read at the two candidate answers. No sampling, so a trial
is deterministic for a pinned model revision.
"""
from __future__ import annotations

import time

from PIL import Image

from ..trials import Trial

# Spellings under which a tokenizer may hold a one-token answer at the start of a reply.
_PREFIXES = ("", " ", "▁", "Ġ")


class HFScorer:
    def __init__(
        self,
        repo: str,
        revision: str | None = None,
        dtype: str = "bfloat16",
        model_class: str = "AutoModelForImageTextToText",
        trust_remote_code: bool = False,
        processor_kwargs: dict | None = None,
        model_kwargs: dict | None = None,
        template_kwargs: dict | None = None,
        name: str | None = None,
    ):
        self.template_kwargs = template_kwargs or {}
        import torch
        import transformers

        self.torch = torch
        t0 = time.time()
        self.processor = transformers.AutoProcessor.from_pretrained(
            repo, revision=revision, trust_remote_code=trust_remote_code, **(processor_kwargs or {})
        )
        cls = getattr(transformers, model_class)
        self.model = cls.from_pretrained(
            repo, revision=revision, dtype=getattr(torch, dtype), device_map="cuda",
            trust_remote_code=trust_remote_code, **(model_kwargs or {}),
        ).eval()
        self.tok = self.processor.tokenizer
        self._ids: dict[str, list[int]] = {}
        try:  # the snapshot folder name is the commit actually loaded
            from pathlib import Path

            from transformers.utils import cached_file

            sha = Path(cached_file(repo, "config.json", revision=revision)).parent.name
        except Exception:
            sha = None
        self.spec = {
            "name": name or repo.split("/")[-1], "repo": repo, "revision_requested": revision,
            "commit": sha, "dtype": dtype, "model_class": model_class,
            "transformers": transformers.__version__, "torch": torch.__version__,
            "processor_kwargs": processor_kwargs or {}, "template_kwargs": self.template_kwargs,
            "load_seconds": round(time.time() - t0, 1),
            "params_M": round(sum(p.numel() for p in self.model.parameters()) / 1e6, 1),
        }

    # -- answers --------------------------------------------------------------
    def answer_ids(self, answer: str) -> list[int]:
        """Every single-token spelling of ``answer`` (with/without a leading-space marker)."""
        if answer not in self._ids:
            ids: set[int] = set()
            unk = self.tok.unk_token_id
            for pre in _PREFIXES:
                tid = self.tok.convert_tokens_to_ids(pre + answer)
                if tid is not None and tid != unk and tid >= 0:
                    ids.add(int(tid))
            for text in (answer, " " + answer):
                enc = self.tok.encode(text, add_special_tokens=False)
                if len(enc) == 1:
                    ids.add(int(enc[0]))
            if not ids:
                raise ValueError(f"no single-token spelling of {answer!r} in this tokenizer")
            self._ids[answer] = sorted(ids)
        return self._ids[answer]

    # -- prompt ---------------------------------------------------------------
    @staticmethod
    def messages(trial: Trial, images: list[Image.Image]) -> list[dict]:
        content = []
        for kind, val in trial.segments:
            if kind == "text":
                content.append({"type": "text", "text": val})
            elif kind == "image":
                content.append({"type": "image", "image": images[val]})
            elif kind == "sbs":
                content.append({"type": "image", "image": images[0]})
        return [{"role": "user", "content": content}]

    def encode(self, trial: Trial, images: list[Image.Image], use_prefix: bool = True):
        torch = self.torch
        inputs = self.processor.apply_chat_template(
            self.messages(trial, images), add_generation_prompt=True, tokenize=True,
            return_dict=True, return_tensors="pt", **self.template_kwargs,
        )
        prefix = getattr(trial, "assistant_prefix", "") if use_prefix else ""
        if prefix:
            # Start the reply with the prefix: append its tokens after the generation prompt, and
            # extend every other per-token tensor (attention mask, token types, image masks) to match.
            ids = torch.tensor([self.tok.encode(prefix, add_special_tokens=False)])
            length = inputs["input_ids"].shape[1]
            for k, v in list(inputs.items()):
                if torch.is_tensor(v) and v.dim() == 2 and v.shape[1] == length and not torch.is_floating_point(v):
                    add = ids if k == "input_ids" else torch.ones_like(ids) if k == "attention_mask" else torch.zeros_like(ids)
                    inputs[k] = torch.cat([v, add.to(v.dtype)], dim=1)
        return inputs.to(self.model.device)

    def prompt_text(self, trial: Trial, images: list[Image.Image]) -> str:
        """The exact string the model sees (image tokens collapsed), for the methods section."""
        return self.processor.apply_chat_template(
            self.messages(trial, images), add_generation_prompt=True, tokenize=False, **self.template_kwargs
        ) + getattr(trial, "assistant_prefix", "")

    # -- scoring --------------------------------------------------------------
    def score(self, trial: Trial, images: list[Image.Image]) -> dict:
        torch = self.torch
        with torch.inference_mode():
            inputs = self.encode(trial, images)
            # Cast floating inputs (pixel values) to the model's dtype.
            inputs = {k: (v.to(self.model.dtype) if torch.is_floating_point(v) else v) for k, v in inputs.items()}
            logits = self.model(**inputs).logits[0, -1].float()
            logp = torch.log_softmax(logits, dim=-1)
            lp = [float(torch.logsumexp(logp[self.answer_ids(a)], dim=0)) for a in trial.answers]
            top = int(torch.argmax(logp))
        return {
            "lp_first": lp[0], "lp_second": lp[1],
            "mass": float(torch.exp(torch.tensor(lp)).sum()),
            "top_token": self.tok.decode([top]), "n_input_tokens": int(inputs["input_ids"].shape[1]),
        }

    def generate(self, trial: Trial, images: list[Image.Image], max_new_tokens: int = 24, use_prefix: bool = True) -> str:
        """Free-text reply: a sanity check that prompts are understood, and (with
        ``use_prefix=False``) the refusal probe, where the model answers unaided."""
        torch = self.torch
        with torch.inference_mode():
            inputs = self.encode(trial, images, use_prefix)
            inputs = {k: (v.to(self.model.dtype) if torch.is_floating_point(v) else v) for k, v in inputs.items()}
            out = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
        return self.tok.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
