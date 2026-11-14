"""The compact tables printed in the report, and the counts its prose quotes.

    python3 -m harness.paper_tables runs/receiver runs/organic > results/paper_tables.md

Everything here is a re-arrangement of what analyze_receiver.py and analyze_organic.py print
in full; it adds no new quantity.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from . import analyze_receiver as ar
from .analyze import load
from .analyze_organic import wrong_payout
from .figure_studies import ordered, short

SIGNALS = ar.SIGNALS


def main() -> None:
    receiver = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/receiver")
    organic = Path(sys.argv[2] if len(sys.argv) > 2 else "runs/organic")

    runs = [r for r in ar.load(receiver) if "crashed" not in r]
    cells: dict[tuple, list[dict]] = defaultdict(list)
    for r in runs:
        cells[(r["receiver"], r["duty"], r["condition"], r["signal"])].append(r)
    receivers = ordered({r["receiver"] for r in runs})

    print("## Study 2. False dones caught, by receiver, prompt and signal\n")
    print("Counts are caught / shown, pooled over the *lie* and *fault* handoffs; per-condition rates")
    print("with intervals are in `tables_receiver.md`. The last column is holds on *honest* handoffs,")
    print("pooled over the five signals.\n")
    print("| Receiver | Prompt | Seeds | no signal | signature valid | ✔ Verified | signature + scope note | signature + evidence result | Honest handoffs held |")
    print("|---|---|---|---|---|---|---|---|---|")
    for rec in receivers:
        for duty in ("discretion", "duty"):
            row, seeds = [], set()
            for s in SIGNALS:
                rs = [r for c in ar.FALSE_DONE for r in cells.get((rec, duty, c, s), [])]
                seeds |= {r["seed"] for r in rs}
                row.append(f"{sum(ar.caught(r) for r in rs)}/{len(rs)}")
            hs = [r for s in SIGNALS for r in cells.get((rec, duty, "honest", s), [])]
            print(
                f"| {short(rec)} | {duty} | {len(seeds)} | " + " | ".join(row)
                + f" | {sum(r['held'] for r in hs)}/{len(hs)} |"
            )

    print("\n## Study 2. Read the refunds table before committing, false-done handoffs\n")
    print("| Receiver | Prompt | no signal | signature valid | ✔ Verified | signature + scope note | signature + evidence result |")
    print("|---|---|---|---|---|---|---|")
    for rec in receivers:
        for duty in ("discretion", "duty"):
            row = []
            for s in SIGNALS:
                rs = [r for c in ar.FALSE_DONE for r in cells.get((rec, duty, c, s), [])]
                row.append(f"{sum(r['looked'] for r in rs)}/{len(rs)}")
            print(f"| {short(rec)} | {duty} | " + " | ".join(row) + " |")

    print("\n## Study 3. False dones nobody planted, and what check C did with them\n")
    print("| Worker | Condition | Runs | Handoffs | W1 import wrong | False done | Misreport | Unusable | Faithful | Caught by C | Wrong payouts under C |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in load(organic):
        if "crashed" not in r:
            groups[(r["model"], r["condition"])].append(r)
    names = {
        "honest": "honest", "honest_t": "honest, reasoning field",
        "blocked": "visible tool error", "blocked_t": "visible tool error, reasoning field",
        "derived": "amount to work out", "derived_t": "amount to work out, reasoning field",
    }
    for model in ordered({m for m, _ in groups}):
        for cond in names:
            rs = groups.get((model, cond))
            if not rs:
                continue
            every = [r for r in rs if r["arms"]["handoff"]]
            hs = [r for r in every if r["truth"]["orders_correct"]]
            fd = [r for r in hs if r["truth"]["false_done"]]
            faithful = sum(r["truth"]["claim_matches_state"] for r in fd)
            unusable = sum(not r["truth"]["claim_usable"] for r in fd)
            caught = sum(not r["arms"]["C"] for r in fd)
            wrong = sum(r["truth"]["false_done"] and r["arms"]["C"] and wrong_payout(r) for r in hs)
            print(
                f"| {short(model)} | {names[cond]} | {len(rs)} | {len(every)} | {len(every) - len(hs)} | {len(fd)} | "
                f"{len(fd) - faithful - unusable} | {unusable} | {faithful} | {caught}/{len(fd)} | {wrong}/{len(hs)} |"
            )

    note = Path(sys.argv[3] if len(sys.argv) > 3 else "runs/receiver_note")
    if note.exists():
        nruns = [r for r in ar.load(note) if "crashed" not in r]
        ncells: dict[tuple, list[dict]] = defaultdict(list)
        for r in nruns:
            ncells[(r["receiver"], r["duty"], r["signal"])].append(r)
        print("\n## Exploratory. The worker's own failure note carried in the handoff\n")
        print("The 20 honest reports of a failed refund that claude-haiku-5-5 wrote in Study 3, replayed")
        print("with the whole report shown. The batch is one refund short, so the right action is to hold.")
        print("Counts are held with no wrong payout / shown. The evidence result in these handoffs is MATCH.\n")
        print("| Receiver | Prompt | no signal | \u2714 Verified | signature + evidence result (MATCH) |")
        print("|---|---|---|---|---|")
        for rec in ordered({r["receiver"] for r in nruns}):
            for duty in ("discretion", "duty"):
                row = []
                for sgn in ("none", "badge", "evidence"):
                    rs = ncells.get((rec, duty, sgn), [])
                    row.append(f"{sum(ar.caught(r) for r in rs)}/{len(rs)}")
                print(f"| {short(rec)} | {duty} | " + " | ".join(row) + " |")

    print("\n## Counts quoted in the prose\n")
    quoted = {}
    for rec in receivers:
        for duty in ("discretion", "duty"):
            for s in SIGNALS:
                rs = [r for c in ar.FALSE_DONE for r in cells.get((rec, duty, c, s), [])]
                quoted[f"{short(rec)} | {duty} | {s}"] = {
                    "caught": sum(ar.caught(r) for r in rs), "shown": len(rs),
                    "paid_wrong": sum(r["wrong_payout"] for r in rs),
                    "read_table": sum(r["looked"] for r in rs),
                    "incomplete": sum(r["outcome"] == "incomplete" for r in rs),
                }
    print("```json")
    print(json.dumps(quoted, indent=1))
    print("```")


if __name__ == "__main__":
    main()
