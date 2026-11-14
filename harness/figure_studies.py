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


def short(model: str) -> str:
    return model.split(":")[0]


def figure2(root: Path, out: Path) -> None:
    runs = [r for r in ar.load(root) if "crashed" not in r]
    cells: dict[tuple, list[dict]] = defaultdict(list)
    for r in runs:
        cells[(r["receiver"], r["duty"], r["condition"], r["signal"])].append(r)
    receivers = sorted({r["receiver"] for r in runs})
    duties = [d for d in ("discretion", "duty") if any(r["duty"] == d for r in runs)]
    fig, axes = plt.subplots(
        len(duties), len(receivers), figsize=(3.7 * len(receivers), 2.55 * len(duties)),
        sharey=True, sharex=True, squeeze=False,
    )
    width = 0.36
    for i, duty in enumerate(duties):
        for j, rec in enumerate(receivers):
            ax = axes[i][j]
            for k, cond in enumerate(ar.FALSE_DONE):
                xs, ps, lo, hi = [], [], [], []
                for x, s in enumerate(ar.SIGNALS):
                    rs = cells.get((rec, duty, cond, s), [])
                    if not rs:
                        continue
                    p, a, b = wilson_bounds(sum(ar.caught(r) for r in rs), len(rs))
                    xs.append(x + (k - 0.5) * width)
                    ps.append(p)
                    lo.append(p - a)
                    hi.append(b - p)
                ax.bar(
                    xs, ps, width, yerr=[lo, hi], capsize=1.5, color=COND_COLOR[cond],
                    label=COND_LABEL[cond], error_kw={"elinewidth": 0.7},
                )
            ax.axhline(1.0, color="#2b8a3e", linewidth=0.8, linestyle="--")
            ax.set_ylim(0, 1.08)
            ax.set_xticks(range(len(ar.SIGNALS)))
            ax.set_xticklabels([SIGNAL_TICK[s] for s in ar.SIGNALS], fontsize=6.5)
            ax.spines[["top", "right"]].set_visible(False)
            if i == 0:
                ax.set_title(short(rec), fontsize=9.5)
            if j == 0:
                ax.set_ylabel(f"{duty} prompt\nshare of false dones caught", fontsize=8)
            ax.tick_params(axis="y", labelsize=7)
    handles, labels = axes[0][0].get_legend_handles_labels()
    handles.append(plt.Line2D([0], [0], color="#2b8a3e", linewidth=0.8, linestyle="--"))
    labels.append("rule-based evidence check (Study 1)")
    fig.legend(handles, labels, fontsize=7.5, frameon=False, loc="upper center", ncol=3)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out, dpi=200)
    print(out)


def figure3(root: Path, out: Path) -> None:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in load(root):
        if "crashed" not in r and r["arms"]["handoff"]:
            groups[(r["model"], r["condition"])].append(r)
    conditions = [c for c in ("blocked", "blocked_t", "derived", "derived_t") if any(k[1] == c for k in groups)]
    models = sorted({m for m, _ in groups})
    fig, axes = plt.subplots(1, len(models), figsize=(3.7 * len(models), 2.9), sharey=True, squeeze=False)
    label = {
        "blocked": "visible\ntool error", "blocked_t": "visible error,\nreasoning field",
        "derived": "amount to\nwork out", "derived_t": "work out,\nreasoning field",
    }
    for ax, model in zip(axes[0], models):
        correct, mis, faithful, ns = [], [], [], []
        for cond in conditions:
            rs = groups.get((model, cond), [])
            n = max(len(rs), 1)
            fd = [r for r in rs if r["truth"]["false_done"]]
            f = sum(r["truth"]["claim_matches_state"] for r in fd)
            correct.append((len(rs) - len(fd)) / n)
            mis.append((len(fd) - f) / n)
            faithful.append(f / n)
            ns.append(len(rs))
        xs = range(len(conditions))
        ax.bar(xs, correct, 0.62, color="#d4d4d8", label="work correct")
        ax.bar(xs, mis, 0.62, bottom=correct, color="#2b8a3e",
               label="false done, report differs from table (evidence check catches it)")
        ax.bar(xs, faithful, 0.62, bottom=[a + b for a, b in zip(correct, mis)], color="#b91c1c",
               label="false done, report matches table (evidence check passes it)")
        ax.set_xticks(list(xs))
        ax.set_xticklabels([f"{label[c]}\nn={n}" for c, n in zip(conditions, ns)], fontsize=6.5)
        ax.set_title(short(model), fontsize=9.5)
        ax.set_ylim(0, 1.0)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="y", labelsize=7)
    axes[0][0].set_ylabel("share of handoffs", fontsize=8)
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=7.5, frameon=False, loc="upper center", ncol=1)
    fig.tight_layout(rect=(0, 0, 1, 0.80))
    fig.savefig(out, dpi=200)
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
