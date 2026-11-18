"""Vision-language models on NVIDIA's free hosted API (build.nvidia.com), scored from samples.

Exploratory addendum after Gate 3 (PLAN.md, "NVIDIA addendum"). The trials are the frozen v1
trials: same images, wording and counterbalancing. Only the readout differs from the local
models: the hosted endpoints return no log-probabilities, so each presentation is answered
once per pass with sampling at temperature 1, and the parsed replies are counted.

The API key is read from the NVIDIA_API_KEY environment variable, or, if that is not set, from
a hidden prompt. It is kept in memory for the request header only, and is never printed,
logged or written anywhere.

Standard library only, so the frozen lockfile is untouched.
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from functools import lru_cache

from .manifest import ROOT
from .trials import Trial

ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
KEY_ENV = "NVIDIA_API_KEY"
PARSE_VERSION = "p1"

# Free endpoints that take several images, as listed on build.nvidia.com on 2026-11-18.
# "extra" switches reasoning off, so the reply is the answer and nothing else.
MODELS = {
    "gemma-4-31b": {
        "id": "google/gemma-4-31b-it", "params_b": 30.7, "family": "Gemma 4",
        "extra": {"chat_template_kwargs": {"enable_thinking": False}},
    },
    "mistral-large-4": {
        "id": "mistralai/mistral-large-4-1t-a52b", "params_b": 1000, "active_b": 52, "family": "Mistral Large 4",
        "extra": {"reasoning_effort": "none"},
    },
    # Reserve, used only if one of the two above is unavailable or fails the dev probe.
    "nemotron-3.5-super-vl": {
        "id": "nvidia/nemotron-3.5-super-vl-120b-a12b", "params_b": 120, "active_b": 12, "family": "Nemotron 3.5",
        "extra": {"reasoning_effort": "none"},
    },
}
SAMPLING = {"temperature": 1.0, "top_p": 1.0, "max_tokens": 16, "stream": False}


# -- reply parsing (rule p1) -----------------------------------------------------
# Strip leading markdown, quotes and brackets, an optional "Answer:" and an optional "Image",
# then the reply must start with one of the two permitted answers as a word of its own.
_LEAD = re.compile(r"""^[\s*_#>`"'(\[]*(?:answer\s*[:.\-]?\s*)?[\s*_`"'(\[]*(?:image\s+)?[\s*_`"'(\[]*""", re.I)


def parse_reply(reply: str | None, answers: tuple[str, str]) -> str | None:
    """The permitted answer the reply opens with, or None (off-menu)."""
    text = (reply or "").strip()
    lead = _LEAD.match(text)
    rest = text[lead.end():]
    led = bool(re.search(r"answer|image", lead.group(0), re.I))
    for a in answers:
        if len(a) == 1:  # a letter label, case-sensitive
            if not re.match(rf"{re.escape(a)}(?![A-Za-z0-9])", rest):
                continue
            if a == "A" and not led and re.match(r"A\s+[a-z]", rest):
                continue  # the article "A ...", not the label
            return a
        if re.match(rf"{re.escape(a)}(?![A-Za-z])", rest, re.I):  # Yes / No
            return a
    return None


# -- request content -------------------------------------------------------------
@lru_cache(maxsize=4096)
def data_uri(rel_path: str) -> str:
    """The stimulus file's exact bytes as a base64 data URI (no re-encoding)."""
    raw = (ROOT / rel_path).read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def content(trial: Trial) -> list[dict]:
    """The trial's segments in order, as chat content parts."""
    parts: list[dict] = []
    for kind, val in trial.segments:
        if kind == "text":
            parts.append({"type": "text", "text": val})
        elif kind == "image":
            parts.append({"type": "image_url", "image_url": {"url": data_uri(trial.image_paths[val])}})
        else:
            raise ValueError("API runs use the two-image layout only")
    return parts


def request_body(model: str, trial: Trial, seed: int) -> dict:
    spec = MODELS[model]
    return {"model": spec["id"], "messages": [{"role": "user", "content": content(trial)}],
            "seed": seed, **SAMPLING, **spec["extra"]}


# -- HTTP -----------------------------------------------------------------------
class RateLimited(Exception):
    """429s kept coming for longer than the client is willing to wait (likely a daily cap)."""


class Fatal(Exception):
    """An error no retry will fix: bad key, unknown model, rejected request."""


class Transient(Exception):
    """Server or network errors that outlasted the retries for one request."""


class RateLimiter:
    """Spaces request starts at least 60/rpm seconds apart, across threads; 429s pause everyone."""

    def __init__(self, rpm: float):
        self.interval = 60.0 / rpm
        self.lock = threading.Lock()
        self.next = 0.0

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            start = max(now, self.next)
            self.next = start + self.interval
        time.sleep(max(0.0, start - now))

    def pause(self, seconds: float) -> None:
        with self.lock:
            self.next = max(self.next, time.monotonic() + seconds)


def _console() -> bool:
    """True only for a real interactive console. On Windows the null device also reports isatty(),
    so ask the console API as well; a script with no console must exit, not hang at a prompt."""
    if sys.stdin is None or not sys.stdin.isatty():
        return False
    if os.name != "nt":
        return True
    import ctypes
    import msvcrt

    try:
        handle = msvcrt.get_osfhandle(sys.stdin.fileno())
    except OSError:
        return False
    mode = ctypes.c_uint32()
    return bool(ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(mode)))


def read_key() -> str:
    """NVIDIA_API_KEY if set; otherwise a hidden prompt (nothing echoed, nothing saved to shell
    history). Either way the key lives in this process's memory only."""
    key = os.environ.get(KEY_ENV, "").strip()
    if not key and _console():
        import getpass

        key = getpass.getpass("Paste your NVIDIA API key (nothing will show as you paste), then press Enter: ").strip()
    if not key:
        raise SystemExit(f"No key: set {KEY_ENV}, or run this in a terminal so it can ask for the key.")
    if not key.startswith("nvapi-"):
        print("Note: that does not look like an NVIDIA key (they start with 'nvapi-'). Trying it anyway.", flush=True)
    return key


class Client:
    def __init__(self, rpm: float = 35, timeout: float = 120, max_429_wait: float = 1800, endpoint: str = ENDPOINT):
        self._auth = "Bearer " + read_key()
        self.endpoint = endpoint
        self.limiter = RateLimiter(rpm)
        self.timeout = timeout
        self.max_429_wait = max_429_wait

    def chat(self, body: dict) -> tuple[dict, dict]:
        """POST one chat completion. Returns (response JSON, request facts)."""
        data = json.dumps(body).encode("utf-8")
        attempts, waited_429, n_429 = 0, 0.0, 0
        while True:
            self.limiter.wait()
            attempts += 1
            req = urllib.request.Request(self.endpoint, data=data, method="POST", headers={
                "Authorization": self._auth, "Content-Type": "application/json", "Accept": "application/json"})
            t0 = time.perf_counter()
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    status = r.status
                    raw = r.read()
                    limits = {k.lower(): v for k, v in r.headers.items() if "ratelimit" in k.lower() or k.lower() == "retry-after"}
                if status == 202:  # queued asynchronously; treat as a server hiccup and ask again
                    raise urllib.error.URLError("HTTP 202 (queued)")
                return json.loads(raw.decode("utf-8")), {"attempts": attempts, "seconds": round(time.perf_counter() - t0, 3),
                                                        "wait_429": round(waited_429, 1), "limits": limits}
            except urllib.error.HTTPError as e:
                detail = e.read()[:300].decode("utf-8", "replace").replace("\n", " ")
                if e.code == 429:
                    retry_after = e.headers.get("Retry-After")
                    wait = float(retry_after) if retry_after and retry_after.replace(".", "", 1).isdigit() else min(600.0, 15.0 * 2 ** min(n_429, 5))
                    n_429 += 1
                    waited_429 += wait
                    if waited_429 > self.max_429_wait:
                        raise RateLimited(f"HTTP 429 for {waited_429 / 60:.0f} min: {detail}") from None
                    self.limiter.pause(wait)
                    continue
                if e.code in (401, 403):
                    raise Fatal(f"HTTP {e.code}: the key was rejected or lacks access to this model. {detail}") from None
                if e.code in (500, 502, 503, 504) and attempts < 6:
                    self.limiter.pause(5.0 * 2 ** (attempts - 1))
                    continue
                if e.code in (500, 502, 503, 504):
                    raise Transient(f"HTTP {e.code} after {attempts} attempts: {detail}") from None
                raise Fatal(f"HTTP {e.code}: {detail}") from None
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
                if attempts < 6:
                    time.sleep(5.0 * 2 ** (attempts - 1))
                    continue
                raise Transient(f"{type(e).__name__} after {attempts} attempts: {e}") from None


def answer(client: Client, model: str, trial: Trial, seed: int) -> dict:
    """One sampled reply to one presentation, parsed."""
    resp, facts = client.chat(request_body(model, trial, seed))
    choice = (resp.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    reply = msg.get("content")
    if isinstance(reply, list):  # some servers return content parts
        reply = "".join(p.get("text", "") for p in reply if isinstance(p, dict))
    return {
        "reply": reply, "choice": parse_reply(reply, tuple(trial.answers)), "parse_version": PARSE_VERSION,
        "finish_reason": choice.get("finish_reason"),
        "reasoning_chars": len(msg.get("reasoning_content") or msg.get("reasoning") or ""),
        "served_model": resp.get("model"), "system_fingerprint": resp.get("system_fingerprint"),
        "usage": resp.get("usage"), **facts,
    }
