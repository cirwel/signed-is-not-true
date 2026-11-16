"""Figure 1: the three links between who signed, what was claimed, what was done and what was meant,
with the check that tests each link and what it caught in these runs.

    python3 -m harness.figure_chain runs/full runs/organic results/figure1.png runs/request

The last argument is optional: the arm that carries the request (run after the cut-off). When its
runs are there, the third link gets one more line with what LLM receivers caught once the handoff
carried the request and the instruction named it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

from .analyze import load  # noqa: E402

GREEN, RED, GREY, INK, BLUE = "#2b8a3e", "#b91c1c", "#6b7280", "#111827", "#1d4ed8"


def request_range(root: Path) -> tuple[int, int, int] | None:
    """Lowest and highest percentage of false dones caught under the request sentence, over the
    receivers of the arm that carries the request, and the number of false dones each was shown."""
    if not root.exists():
        return None
    cells: dict[str, list[dict]] = {}
    for path in sorted(root.rglob("seed_*.json")):
        r = json.loads(path.read_text())
        if "crashed" not in r and r["duty"] == "request" and r["condition"] != "honest":
            cells.setdefault(r["receiver"], []).append(r)
    if not cells or min(len(rs) for rs in cells.values()) < 30:
        return None
    rates = [int(100 * sum(bool(r["held"]) and not r["wrong_payout"] for r in rs) / len(rs)) for rs in cells.values()]
    return min(rates), max(rates), max(len(rs) for rs in cells.values())


def counts(planted: Path, organic: Path) -> dict[str, tuple[int, int]]:
    """(caught by C, total) for false dones on each side of the claim/state link.

    Same partition as the tables: a misreport is a usable report that differs from the table,
    a faithful report equals it. Reports that are not in the agreed form are left out of both
    (C rejects them whatever the state), as are handoffs W1 had already broken.
    """
    out = {"planted_misreport": [0, 0], "planted_faithful": [0, 0], "organic_misreport": [0, 0], "organic_faithful": [0, 0]}
    for root, prefix in ((planted, "planted"), (organic, "organic")):
        if not root.exists():
            continue
        for r in load(root):
            t = r.get("truth") or {}
            if "crashed" in r or not r["arms"]["handoff"] or not t["false_done"]:
                continue
            if not t["orders_correct"] or not t["claim_usable"]:
                continue
            key = f"{prefix}_{'faithful' if t['claim_matches_state'] else 'misreport'}"
            out[key][1] += 1
            out[key][0] += not r["arms"]["C"]
    return {k: (a, b) for k, (a, b) in out.items()}


def main() -> None:
    planted = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/full")
    organic = Path(sys.argv[2] if len(sys.argv) > 2 else "runs/organic")
    out = Path(sys.argv[3] if len(sys.argv) > 3 else "results/figure1.png")
    asked = request_range(Path(sys.argv[4])) if len(sys.argv) > 4 else None
    c = counts(planted, organic)

    fig, ax = plt.subplots(figsize=(7.4, 2.38 if asked else 2.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.08 if asked else 0.35, 3.4)
    ax.axis("off")
    boxes = [
        (0.95, "ISSUER", "who sent the report"),
        (3.65, "CLAIM", "what the report says"),
        (6.35, "STATE", "what is in the table"),
        (9.05, "INTENT", "what the batch calls for"),
    ]
    w, h, y = 1.62, 0.78, 2.35
    for x, head, sub in boxes:
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    linewidth=0.9, edgecolor=INK, facecolor="#f8fafc"))
        ax.text(x, y + 0.14, head, ha="center", va="center", fontsize=8.5, fontweight="bold", color=INK)
        ax.text(x, y - 0.17, sub, ha="center", va="center", fontsize=6.6, color=INK)

    def frac(pair: tuple[int, int]) -> str:
        return f"{pair[0]} of {pair[1]}" if pair[1] else "none occurred"

    links = [
        (2.30, GREY, "signature", "check B",
         "breaks when a message\nis forged or replayed",
         "not tested: every issuer\nhere was authorised"),
        (5.00, GREEN, "evidence digest", "check C",
         "breaks on a lie, a silent\nfault or an overclaim",
         f"C caught {frac(c['planted_misreport'])} planted,\n{frac(c['organic_misreport'])} unplanted"),
        (7.70, RED, "no check here", "A, B and C are all blind",
         "breaks on a mis-keyed ticket,\na miscalculation, or an honest\nreport of unfinished work",
         f"C caught {frac(c['planted_faithful'])} planted,\n{frac(c['organic_faithful'])} unplanted"),
    ]
    for x, colour, name, sub, breaks, caught in links:
        ax.annotate("", xy=(x + 0.52, y), xytext=(x - 0.52, y),
                    arrowprops={"arrowstyle": "<->", "color": colour, "linewidth": 1.6})
        ax.text(x, y + 0.74, name, ha="center", va="center", fontsize=8, fontweight="bold", color=colour)
        ax.text(x, y + 0.50, sub, ha="center", va="center", fontsize=6.6, color=colour)
        ax.text(x, y - 0.62, breaks, ha="center", va="top", fontsize=6.5, color=INK, linespacing=1.3)
        ax.text(x, y - 1.42, caught, ha="center", va="top", fontsize=6.7, fontweight="bold", color=colour,
                linespacing=1.3)
    if asked:
        low, high, n = asked
        ax.text(7.70, 0.42, f"with the request in the handoff, LLM receivers told\nto check it caught {low}% to {high}% of {n} (Section 4.5)",
                ha="center", va="top", fontsize=6.7, fontweight="bold", color=BLUE, linespacing=1.3)
    fig.tight_layout(pad=0.2)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300)
    print(out, c)


if __name__ == "__main__":
    main()
