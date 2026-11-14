"""Other ways to reach a model than local Ollama. Added after the second lock; exploratory.

`claude_cli` calls Anthropic's `claude` command-line tool in print mode, once per turn, with
the tool's own system prompt replaced by the worker's, no tools, and no user settings, hooks
or memory files loaded. The CLI still adds a short context block of its own (the date and
the account's email address), has no seed or temperature control, and may think before it
answers, so these runs are not sampled the way the Ollama runs are.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import time

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


BACKENDS = {"ollama": None, "claude-cli": claude_cli}
