"""Figures 2 and 3.

    python3 -m harness.figure_studies runs/receiver runs/organic results

Figure 2 (Study 2): catch rate on false-done handoffs by signal, per receiver and prompt.
Figure 3 (Study 3): what the evidence check can see among handoffs where nobody planted an error.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from . import analyze_receiver as ar  # noqa: E402
from .analyze import load  # noqa: E402
from .figure import wilson_bounds  # noqa: E402

SIGNAL_TICK = {
    "none": "no signal", "sig": "signature\nvalid", "badge": "✔ Verified",
    "scoped": "signature +\nscope note", "evidence": "signature +\nevidence result",
}
COND_COLOR = {"lie": "#c2410c", "fault": "#1d4ed8"}
COND_LABEL = {"lie": "planted lie (table empty)", "fault": "silent fault (one refund missing)"}


ORDER = (
    "gemma4:latest", "qwen3.6:27b-coding-mxfp8", "nemotron3:33b",
    "gpt-5.4-nano", "gpt-6-luna", "claude-haiku-5-5", "gpt-6.1-sol",
)
TITLE = {
    "gemma4:latest": "gemma4 (8B)", "qwen3.6:27b-coding-mxfp8": "qwen3.6 (27B)",
    "nemotron3:33b": "nemotron3 (33B)", "claude-haiku-5-5": "claude-haiku-5-5",
}


def short(model: str) -> str:
    return TITLE.get(model, model.split(":")[0])


def ordered(models: set[str]) -> list[str]:
    return [m for m in ORDER if m in models] + sorted(models - set(ORDER))


# Okabe-Ito colours, one per receiver, in the order of ORDER.
RECEIVER_STYLE = {
    "gemma4:latest": ("#E69F00", "o"), "qwen3.6:27b-coding-mxfp8": ("#999999", "v"),
    "nemotron3:33b": ("#D55E00", "s"), "gpt-5.4-nano": ("#56B4E9", "^"),
    "gpt-6-luna": ("#0072B2", "D"), "claude-haiku-5-5": ("#009E73", "P"), "gpt-6.1-sol": ("#000000", "X"),
}


def figure2(root: Path, out: Path) -> None:
    """Catch rate by signal, one line per receiver, one panel per prompt (lie and fault pooled)."""
    runs = [r for r in ar.load(root) if "crashed" not in r and r["signal"] in ar.SIGNALS]
    cells: dict[tuple, list[dict]] = defaultdict(list)
    for r in runs:
        if r["condition"] in ar.FALSE_DONE:
            cells[(r["receiver"], r["duty"], r["signal"])].append(r)
    receivers = ordered({r["receiver"] for r in runs})
    duties = [d for d in ("discretion", "duty") if any(r["duty"] == d for r in runs)]
    fig, axes = plt.subplots(1, len(duties), figsize=(7.4, 2.9), sharey=True, squeeze=False)
    spread = 0.5
    for ax, duty in zip(axes[0], duties):
        for k, rec in enumerate(receivers):
            colour, marker = RECEIVER_STYLE.get(rec, ("#555555", "o"))
            offset = (k - (len(receivers) - 1) / 2) * spread / max(len(receivers) - 1, 1)
            xs, ps, lo, hi = [], [], [], []
            for x, s in enumerate(ar.SIGNALS):
                rs = cells.get((rec, duty, s), [])
                if not rs:
                    continue
                p, a, b = wilson_bounds(sum(ar.caught(r) for r in rs), len(rs))
                xs.append(x + offset)
                ps.append(p)
                lo.append(max(0.0, p - a))  # rounding can leave -1e-17 at p = 0 or 1
                hi.append(max(0.0, b - p))
            if not xs:
                continue
            n = len({r["seed"] for s in ar.SIGNALS for r in cells.get((rec, duty, s), [])})
            ax.errorbar(
                xs, ps, yerr=[lo, hi], color=colour, marker=marker, markersize=3.6, linewidth=0.9,
                elinewidth=0.5, capsize=1.2, capthick=0.5, label=f"{short(rec)}",
            )
        ax.axhline(1.0, color="#2b8a3e", linewidth=0.7, linestyle="--")
        ax.set_ylim(-0.04, 1.08)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_xticks(range(len(ar.SIGNALS)))
        ax.set_xticklabels([SIGNAL_TICK[s] for s in ar.SIGNALS], fontsize=6.3)
        ax.set_title(f"{duty} prompt", fontsize=7.8, pad=3)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="both", length=2, pad=1.5)
        ax.tick_params(axis="y", labelsize=6.3)
        ax.grid(axis="y", linewidth=0.3, color="#dddddd")
    axes[0][0].set_ylabel("share of false dones caught", fontsize=7)
    handles, labels = axes[0][0].get_legend_handles_labels()
    handles.append(plt.Line2D([0], [0], color="#2b8a3e", linewidth=0.7, linestyle="--"))
    labels.append("rule C")
    fig.legend(handles, labels, fontsize=6.3, frameon=False, loc="lower center", ncol=len(labels), columnspacing=1.0,
               handletextpad=0.4)
    fig.tight_layout(rect=(0, 0.07, 1, 1), w_pad=1.0)
    fig.savefig(out, dpi=300)
    print(out)


def figure3(root: Path, out: Path) -> None:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in load(root):
        # handoffs where W1 had imported the orders correctly: see analyze_organic.clean
        if "crashed" not in r and r["arms"]["handoff"] and r["truth"]["orders_correct"]:
            groups[(r["model"], r["condition"])].append(r)
    wanted = ("blocked", "blocked_t", "derived", "derived_t")
    models = ordered({m for m, c in groups if c in wanted})
    label = {
        "blocked": "visible\ntool error", "blocked_t": "visible error,\nreasoning",
        "derived": "amount to\nwork out", "derived_t": "work out,\nreasoning",
    }
    fig, axes = plt.subplots(1, len(models), figsize=(7.4, 2.75), sharey=True, squeeze=False)
    for ax, model in zip(axes[0], models):
        conditions = [c for c in wanted if groups.get((model, c))]
        parts: dict[str, list[float]] = {"correct": [], "mis": [], "unusable": [], "faithful": []}
        ns = []
        for cond in conditions:
            rs = groups[(model, cond)]
            n = len(rs)
            fd = [r for r in rs if r["truth"]["false_done"]]
            faithful = sum(r["truth"]["claim_matches_state"] for r in fd)
            unusable = sum(not r["truth"]["claim_usable"] for r in fd)
            parts["correct"].append((n - len(fd)) / n)
            parts["mis"].append((len(fd) - faithful - unusable) / n)
            parts["unusable"].append(unusable / n)
            parts["faithful"].append(faithful / n)
            ns.append(n)
        xs = list(range(len(conditions)))
        style = (
            ("correct", "#d4d4d8", None, "work correct"),
            ("mis", "#2b8a3e", None, "false done, report differs from the table: the evidence check catches it"),
            ("unusable", "#a7d7b0", "////", "false done, report not in the agreed form: the evidence check rejects it"),
            ("faithful", "#b91c1c", None, "false done, report matches the table: the evidence check passes it"),
        )
        bottom = [0.0] * len(conditions)
        for key, colour, hatch, text in style:
            ax.bar(xs, parts[key], 0.62, bottom=bottom, color=colour, hatch=hatch, edgecolor="white",
                   linewidth=0.4, label=text)
            bottom = [a + b for a, b in zip(bottom, parts[key])]
        ax.set_xticks(xs)
        ax.set_xticklabels([f"{label[c]}\nn={n}" for c, n in zip(conditions, ns)], fontsize=5.4)
        ax.set_title(short(model), fontsize=7.5, pad=3)
        ax.set_ylim(0, 1.0)
        ax.set_yticks([0, 0.5, 1.0])
        ax.set_xlim(-0.6, 3.6)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="both", length=2, pad=1.5)
        ax.tick_params(axis="y", labelsize=6)
    axes[0][0].set_ylabel("share of handoffs", fontsize=6.5)
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=6.2, frameon=False, loc="upper center", ncol=2, columnspacing=1.2)
    fig.tight_layout(rect=(0, 0, 1, 0.87), w_pad=0.6)
    fig.savefig(out, dpi=300)
    print(out)


def main() -> None:
    receiver = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/receiver")
    organic = Path(sys.argv[2] if len(sys.argv) > 2 else "runs/organic")
    out = Path(sys.argv[3] if len(sys.argv) > 3 else "results")
    out.mkdir(parents=True, exist_ok=True)
    if receiver.exists():
        figure2(receiver, out / "figure2.png")
    if organic.exists():
        figure3(organic, out / "figure3.png")


if __name__ == "__main__":
    main()
