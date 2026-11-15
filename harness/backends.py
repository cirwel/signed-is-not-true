"""Other ways to reach a model than local Ollama. Added after the second lock; exploratory.

`claude_cli` calls Anthropic's `claude` command-line tool in print mode, once per turn, with
the tool's own system prompt replaced by the worker's, no tools, and no user settings, hooks
or memory files loaded. The CLI still adds a short context block of its own (the date and
the account's email address), has no seed or temperature control, and may think before it
answers, so these runs are not sampled the way the Ollama runs are.

`openai_api` calls the OpenAI Chat Completions API in JSON mode with exactly the messages the
local models get (the worker prompt as the system message). The key is read from the
OPENAI_API_KEY environment variable. A seed is always sent. Temperature is sent where the
model accepts one; the reasoning models accept only their default, and run at their default
reasoning effort.
"""

from __future__ import annotations

import json
import os
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

_EMPTY_DIR = tempfile.mkdtemp(prefix="receiver_cli_")


def render(messages: list[dict]) -> tuple[str, str]:
    """(system prompt, one user prompt holding the whole conversation so far)."""
    system = messages[0]["content"]
    parts = [messages[1]["content"]]
    turn = 0
    for m in messages[2:]:
        if m["role"] == "assistant":
            turn += 1
            parts.append(f"--- Your reply {turn} ---\n{m['content']}")
        else:
            parts.append(f"--- Result of reply {turn} ---\n{m['content']}")
    if turn:
        parts.append("Reply with your next JSON object only.")
    return system, "\n\n".join(parts)


def first_json_object(text: str) -> str:
    """The first balanced {...} in the text, so a fenced or prefaced reply still parses."""
    start = text.find("{")
    if start < 0:
        return text
    depth, in_string, escaped = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return text[start:]


def claude_cli(model: str, messages: list[dict], seed: int, temperature: float) -> tuple[str, dict]:
    system, prompt = render(messages)
    last_error = "no attempt"
    for attempt in range(4):
        started = time.time()
        proc = subprocess.run(
            [
                "claude", "-p", "--model", model, "--setting-sources", "local",
                "--system-prompt", system, "--tools", "", "--no-session-persistence",
                "--output-format", "json", prompt,
            ],
            capture_output=True, text=True, stdin=subprocess.DEVNULL, cwd=_EMPTY_DIR, timeout=300,
        )
        try:
            data = json.loads(proc.stdout)
        except ValueError:
            last_error = f"exit {proc.returncode}: {proc.stdout[:200]!r} {proc.stderr[:200]!r}"
        else:
            if not data.get("is_error") and isinstance(data.get("result"), str):
                usage = data.get("usage") or {}
                meta = {
                    "prompt_tokens": (usage.get("input_tokens") or 0)
                    + (usage.get("cache_read_input_tokens") or 0)
                    + (usage.get("cache_creation_input_tokens") or 0),
                    "output_tokens": usage.get("output_tokens") or 0,
                    "seconds": round(time.time() - started, 2),
                }
                return first_json_object(data["result"]), meta
            last_error = str(data.get("result"))[:300]
        time.sleep(15 * (attempt + 1))
    raise RuntimeError(f"claude CLI failed: {last_error}")


_NO_TEMPERATURE: set[str] = set()   # models that answered "only the default temperature is supported"
_SSL: ssl.SSLContext | None = None


def _ssl_context() -> ssl.SSLContext:
    global _SSL
    if _SSL is None:
        _SSL = ssl.create_default_context()
        try:  # python.org builds on macOS ship without a CA bundle
            import certifi

            _SSL.load_verify_locations(certifi.where())
        except ImportError:
            pass
    return _SSL


def openai_api(model: str, messages: list[dict], seed: int, temperature: float) -> tuple[str, dict]:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("openai API failed: OPENAI_API_KEY is not set")
    last_error = "no attempt"
    for attempt in range(7):
        body = {"model": model, "messages": messages, "response_format": {"type": "json_object"}, "seed": seed}
        if model not in _NO_TEMPERATURE:
            body["temperature"] = temperature
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions", data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        started = time.time()
        try:
            with urllib.request.urlopen(request, timeout=300, context=_ssl_context()) as response:
                data = json.load(response)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            last_error = f"HTTP {exc.code}: {detail}"
            if exc.code == 400 and "temperature" in detail and "temperature" in body:
                _NO_TEMPERATURE.add(model)
                continue
            if exc.code in (408, 409, 429, 500, 502, 503, 504):
                time.sleep(min(60, 5 * 2**attempt))
                continue
            break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = repr(exc)[:300]
            time.sleep(min(60, 5 * 2**attempt))
            continue
        usage = data.get("usage") or {}
        details = usage.get("completion_tokens_details") or {}
        meta = {
            "prompt_tokens": usage.get("prompt_tokens") or 0,
            "output_tokens": usage.get("completion_tokens") or 0,
            "reasoning_tokens": details.get("reasoning_tokens") or 0,
            "cached_tokens": (usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0,
            "seconds": round(time.time() - started, 2),
        }
        log = os.environ.get("HARNESS_USAGE_LOG")
        if log:
            with open(log, "a") as handle:
                handle.write(json.dumps({"model": data.get("model", model), **meta}) + "\n")
        return data["choices"][0]["message"].get("content") or "", meta
    raise RuntimeError(f"openai API failed: {last_error}")


BACKENDS = {"ollama": None, "claude-cli": claude_cli, "openai": openai_api}
