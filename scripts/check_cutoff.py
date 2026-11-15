"""Checks the stopping rule of the second lock: the analysis uses runs finished by
2026-11-15 12:00 UTC. Every run record carries the time it finished (`finished_utc`).

    python3 scripts/check_cutoff.py           # list runs finished after the cut-off
    python3 scripts/check_cutoff.py --move    # and set them aside in runs/after_cutoff/

Runs set aside are not read by any analysis and are not committed (runs/* is ignored except
the four study folders).
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

CUT = "2026-11-15T12:00:00Z"   # ISO times in UTC compare correctly as text
ROOTS = ("runs/full", "runs/receiver", "runs/organic", "runs/receiver_note")


def main() -> int:
    move = "--move" in sys.argv[1:]
    repo = Path(__file__).resolve().parent.parent
    total, late, latest = 0, [], ""
    for root in ROOTS:
        for path in sorted((repo / root).rglob("seed_*.json")):
            total += 1
            finished = json.loads(path.read_text()).get("finished_utc", "")
            if not finished:
                print(f"no finish time: {path.relative_to(repo)}")
                late.append(path)
                continue
            if finished > CUT:
                late.append(path)
            else:
                latest = max(latest, finished)
    for path in late:
        print(f"after the cut-off: {path.relative_to(repo)}")
        if move:
            dest = repo / "runs" / "after_cutoff" / path.relative_to(repo / "runs")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(dest))
    print(f"{total} run records; {len(late)} finished after {CUT}"
          + (" and were set aside" if move and late else "")
          + f"; the last one counted finished at {latest}")
    return 0 if not late or move else 1


if __name__ == "__main__":
    sys.exit(main())
