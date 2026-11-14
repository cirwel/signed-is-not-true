"""Figures 2 and 3.

    python3 -m harness.figure_studies runs/receiver runs/organic results [runs/receiver_note]

Figure 2 (Study 2): catch rate on false-done handoffs by signal, per receiver and prompt.
Figure 3 (Study 3 and the note-carrying arm): what each worker's report said where nobody planted
an error, which of those the evidence check can see, and what receivers did with a worker's own
note of a failure.
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
from .analyze_organic import mentions, report_kind  # noqa: E402
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


MIN_SEEDS = 20   # every receiver but qwen3.6 reached at least 20 seeds


def figure2(root: Path, out: Path) -> None:
    """Catch rate by signal, one line per receiver, one panel per prompt (lie and fault pooled)."""
    runs = [r for r in ar.load(root) if "crashed" not in r and r["signal"] in ar.SIGNALS]
    cells: dict[tuple, list[dict]] = defaultdict(list)
    for r in runs:
        if r["condition"] in ar.FALSE_DONE:
            cells[(r["receiver"], r["duty"], r["signal"])].append(r)
    seeds_run: dict[str, set] = defaultdict(set)
    for (rec, _duty, _signal), rs in cells.items():
        seeds_run[rec] |= {r["seed"] for r in rs}
    # A receiver with fewer seeds than every other goes in a table of its own (Table E2).
    receivers = [m for m in ordered({r["receiver"] for r in runs}) if len(seeds_run[m]) >= MIN_SEEDS]
    duties = [d for d in ("discretion", "duty") if any(r["duty"] == d for r in runs)]
    fig, axes = plt.subplots(1, len(duties), figsize=(7.4, 2.25), sharey=True, squeeze=False)
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


CAUGHT, SILENT, NOTED, FINE = "#009E73", "#D55E00", "#CC79A7", "#d4d4d8"   # Okabe-Ito
ROWS = (
    ("gemma4:latest", "", "gemma4"), ("gemma4:latest", "_t", "gemma4, reasoning field"),
    ("gpt-5.4-nano", "", "gpt-5.4-nano"), ("gpt-5.4-nano", "_t", "gpt-5.4-nano, reasoning field"),
    ("gpt-6-luna", "", "gpt-6-luna"), ("claude-haiku-5-5", "", "claude-haiku-5-5"), ("gpt-6.1-sol", "", "gpt-6.1-sol"),
)


def figure3(root: Path, out: Path, note_root: Path | None = None) -> None:
    """(a) and (b): one bar per worker and reply format, split by what the evidence check can see.
    (c): the note-carrying arm, held under each prompt, one line per receiver."""
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in load(root):
        # handoffs where W1 had imported the orders correctly: see analyze_organic.clean
        if "crashed" not in r and r["arms"]["handoff"] and r["truth"]["orders_correct"]:
            groups[(r["model"], r["condition"])].append(r)

    def split(rs: list[dict], blocked: bool) -> dict[str, int]:
        out = {"fine": 0, "caught": 0, "silent": 0, "noted": 0}
        for r in rs:
            t = r["truth"]
            if not t["false_done"]:
                out["fine"] += 1
            elif not t["claim_usable"] or not t["claim_matches_state"]:
                out["caught"] += 1
            elif blocked and report_kind(r) == "partial" and mentions(r):
                out["noted"] += 1
            else:
                out["silent"] += 1
        return out

    have_note = bool(note_root and note_root.exists())
    fig, axes = plt.subplots(
        1, 3 if have_note else 2, figsize=(7.4, 2.55),
        gridspec_kw={"width_ratios": [1.0, 1.0, 0.95] if have_note else [1.0, 1.0]},
    )
    style = (
        ("fine", FINE, None, "work correct"),
        ("caught", CAUGHT, None, "false done, report differs from the table: evidence check catches it"),
        ("silent", SILENT, None, "false done, report matches the table and says no more: check passes it"),
        ("noted", NOTED, "////", "false done, report matches the table and notes the failure: check passes it"),
    )
    panels = (("blocked", "(a) one refund fails with a visible error", True),
              ("derived", "(b) amount to work out from a rule", False))
    for ax, (cond, title, blocked) in zip(axes[:2], panels):
        ys, labels = [], []
        for y, (model, suffix, label) in enumerate(ROWS):
            rs = groups.get((model, cond + suffix), [])
            labels.append(label)
            ys.append(y)
            if not rs:
                continue
            parts = split(rs, blocked)
            left = 0.0
            for key, colour, hatch, _ in style:
                w = parts[key] / len(rs)
                ax.barh(y, w, 0.66, left=left, color=colour, hatch=hatch, edgecolor="white", linewidth=0.4)
                left += w
            ax.text(1.02, y, f"n={len(rs)}", va="center", ha="left", fontsize=5.6, color="#444444")
        ax.set_yticks(ys)
        ax.set_yticklabels(labels if ax is axes[0] else [], fontsize=6.3)
        ax.invert_yaxis()
        ax.set_xlim(0, 1.16)
        ax.set_xticks([0, 0.5, 1.0])
        ax.set_xlabel("share of handoffs", fontsize=6.3, labelpad=1.5)
        ax.set_title(title, fontsize=7, pad=3, loc="left")
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="both", length=2, pad=1.5)
        ax.tick_params(axis="x", labelsize=6)
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=c, hatch=h, edgecolor="white", linewidth=0.4) for _, c, h, _ in style]
    fig.legend(handles, [t for *_, t in style], fontsize=6.1, frameon=False, loc="upper left", ncol=2,
               columnspacing=1.2, handlelength=1.4, bbox_to_anchor=(0.005, 1.0))

    if have_note:
        ax = axes[2]
        nruns = [r for r in ar.load(note_root) if "crashed" not in r]
        cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for r in nruns:
            cells[(r["receiver"], r["duty"])].append(r)
        prompts = [d for d in ("discretion", "duty", "goal") if any(k[1] == d for k in cells)]
        tick = {"discretion": "left to\ndecide", "duty": "told which\ncheck to run", "goal": "told\nthe goal"}
        ends: list[tuple[float, str, str]] = []
        for rec in ordered({r["receiver"] for r in nruns}):
            colour, marker = RECEIVER_STYLE.get(rec, ("#555555", "o"))
            xs, ps, lo, hi = [], [], [], []
            for x, duty in enumerate(prompts):
                rs = cells.get((rec, duty), [])
                if len(rs) < 30:   # a prompt still being run for this receiver
                    continue
                p, a, b = wilson_bounds(sum(ar.caught(r) for r in rs), len(rs))
                xs.append(x)
                ps.append(p)
                lo.append(max(0.0, p - a))
                hi.append(max(0.0, b - p))
            ax.errorbar(xs, ps, yerr=[lo, hi], color=colour, marker=marker, markersize=3.6, linewidth=1.0,
                        elinewidth=0.5, capsize=1.2, capthick=0.5)
            ends.append((ps[-1], short(rec), colour))
        # direct labels at the right end, nudged apart where two lines end together
        ends.sort()
        placed: list[float] = []
        for p, name, colour in ends:
            y = p if not placed else max(p, placed[-1] + 0.085)
            placed.append(y)
            ax.text(len(prompts) - 1 + 0.08, y, name.replace(" (8B)", ""), va="center", ha="left", fontsize=5.6, color=colour)
        ax.set_xlim(-0.2, len(prompts) - 1 + 0.95)
        ax.set_ylim(-0.06, 1.2)
        ax.set_xticks(range(len(prompts)))
        ax.set_xticklabels([tick[d] for d in prompts], fontsize=5.8)
        ax.set_yticks([0, 0.5, 1.0])
        ax.set_ylabel("share of batches held", fontsize=6.3, labelpad=1.5)
        ax.set_title("(c) receiver is shown the note", fontsize=7, pad=3, loc="left")
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="both", length=2, pad=1.5)
        ax.tick_params(axis="y", labelsize=6)
    fig.tight_layout(rect=(0, 0, 1, 0.86), w_pad=0.8)
    fig.savefig(out, dpi=300)
    print(out)


def main() -> None:
    receiver = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/receiver")
    organic = Path(sys.argv[2] if len(sys.argv) > 2 else "runs/organic")
    out = Path(sys.argv[3] if len(sys.argv) > 3 else "results")
    note = Path(sys.argv[4] if len(sys.argv) > 4 else "runs/receiver_note")
    out.mkdir(parents=True, exist_ok=True)
    if receiver.exists():
        figure2(receiver, out / "figure2.png")
    if organic.exists():
        figure3(organic, out / "figure3.png", note)


if __name__ == "__main__":
    main()
