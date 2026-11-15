#!/bin/bash
# Waits for the cut-off the second lock sets for the analysis (2026-11-15 12:00 UTC) and then stops
# this repository's local sweeps, so that no run finished after it enters the tables.
#   bash scripts/stop_at_cutoff.sh
set -u
cd "$(dirname "$0")/.."
python3 - <<'EOF'
import calendar
import time

cut = calendar.timegm((2026, 11, 15, 12, 0, 0))
while time.time() < cut:
    time.sleep(min(30, max(1, cut - time.time())))
EOF
for pattern in \
  "scripts/sweep_qwen.sh" \
  "scripts/resume_qwen_after_nemotron.sh" \
  "scripts/sweep_studies_2_3.sh" \
  "harness.receiver --handoffs runs/full/gemma4_latest --receivers qwen3.6" \
  "harness.run --lenient --models qwen3.6" \
  "harness.receiver --handoffs runs/full/gemma4_latest --receivers nemotron3" \
  "harness.run --lenient --models nemotron3"; do
  pkill -f "$pattern" 2>/dev/null
done
echo "[$(date -u +%FT%TZ)] cut-off reached; local sweeps stopped" >> runs/cutoff.log
date -u +"%Y-%m-%d %H:%M:%S UTC: cut-off reached, local sweeps stopped"
