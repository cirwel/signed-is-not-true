#!/bin/bash
# Exploratory, added after the second lock: replay claude-haiku-5-5's 20 honest reports of a
# failed refund (Study 3, `blocked`) with the whole report shown to the receiver.
#   bash scripts/sweep_note.sh <receiver> [backend]
set -u
cd "$(dirname "$0")/.."
python3 -m harness.receiver --full-report --backend "${2:-ollama}" --handoffs runs/organic/claude-haiku-5-5 \
  --conditions blocked --signals none,badge,evidence --receivers "$1" --seeds 0-19 --out runs/receiver_note
