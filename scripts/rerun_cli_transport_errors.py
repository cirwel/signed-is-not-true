"""Set aside runs in which a remote backend could not reach its API, so they are rerun.

A run that stopped because the `claude` tool or the OpenAI client had no network or exhausted
its retries on a rate limit or a server error says nothing about the model: the worker never
got to act. Such run files are moved from `runs/`
to `results/cli_transport_errors/`, keeping their relative path, and the resumable sweep
commands then run them again. Server errors from the local Ollama server are left alone:
they happened while the model was generating a reply and may depend on that reply, so those
runs stay in the tables as incomplete.

    python3 scripts/rerun_cli_transport_errors.py          # list
    python3 scripts/rerun_cli_transport_errors.py --move   # set aside
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
moved = []
for path in sorted((ROOT / "runs" / "receiver").rglob("seed_*.json")) + sorted((ROOT / "runs" / "organic").rglob("seed_*.json")):
    record = json.loads(path.read_text())
    stops = [str((record.get(w) or {}).get("stop", "")) for w in ("w1", "w2", "w3")]
    crashed = str(record.get("crashed", ""))
    failed = ("claude CLI failed", "openai API failed")
    if any(s.startswith("chat_error: " + f) for s in stops for f in failed) or any(f in crashed for f in failed):
        moved.append(path)
        if "--move" in sys.argv:
            target = ROOT / "results" / "cli_transport_errors" / path.relative_to(ROOT / "runs")
            target.parent.mkdir(parents=True, exist_ok=True)
            path.rename(target)
for path in moved:
    print(path.relative_to(ROOT))
print(f"{len(moved)} run(s) {'set aside' if '--move' in sys.argv else 'found'}")
