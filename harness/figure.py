"""Study 1 figure: propagation (a false done accepted, then wrong payouts) by check and condition.

    python3 -m harness.figure runs/full results/figure_study1.png
"""

from __future__ import annotations

import math
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .analyze import ARMS, load  # noqa: E402

CONDS = ("honest", "lie", "fault", "wrong")
COND_LABEL = {"honest": "honest", "lie": "planted lie", "fault": "silent fault", "wrong": "mis-keyed ticket\n(post-lock)"}
ARM_LABEL = {"A": "A: trust", "B": "B: signature", "C": "C: signature + evidence"}
ARM_COLOR = {"A": "#9aa5b1", "B": "#4c6ef5", "C": "#2b8a3e"}


def wilson_bounds(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return p, max(0.0, centre - half), min(1.0, centre + half)


def propagated(r: dict, arm: str) -> bool:
    t = r["truth"]
    return bool(r["arms"][arm] and t["false_done"] and t["payouts"] != t["payouts_correct"])


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/full")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "results/figure_study1.png")
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in load(root):
        if "crashed" not in r and r["arms"]["handoff"]:
            groups[(r["model"], r["condition"])].append(r)
    models = sorted({m for m, _ in groups})
    fig, axes = plt.subplots(1, len(models), figsize=(5.2 * len(models), 3.6), sharey=True)
    if len(models) == 1:
        axes = [axes]
    width = 0.26
    for ax, model in zip(axes, models):
        for j, arm in enumerate(ARMS):
            xs, ps, lo, hi = [], [], [], []
            for i, cond in enumerate(CONDS):
                rs = groups.get((model, cond), [])
                if not rs:
                    continue
                p, a, b = wilson_bounds(sum(propagated(r, arm) for r in rs), len(rs))
                xs.append(i + (j - 1) * width)
                ps.append(p)
                lo.append(p - a)
                hi.append(b - p)
            ax.bar(xs, ps, width, yerr=[lo, hi], capsize=2, color=ARM_COLOR[arm], label=ARM_LABEL[arm])
        ns = [len(groups.get((model, c), [])) for c in CONDS]
        ax.set_xticks(range(len(CONDS)))
        ax.set_xticklabels([f"{COND_LABEL[c]}\nn={n}" for c, n in zip(CONDS, ns)], fontsize=8)
        ax.set_title(model, fontsize=10)
        ax.set_ylim(0, 1.05)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("share of handoffs ending in wrong payouts")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=8, frameon=False, loc="upper center", ncol=3)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    print(out)


if __name__ == "__main__":
    main()
