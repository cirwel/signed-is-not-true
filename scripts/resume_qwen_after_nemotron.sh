#!/bin/bash
# qwen3.6 is about ten times slower than nemotron3 and slows it when both run. This waits for
# nemotron3's locked Study 2 runs and its exploratory wording arms to finish, then gives the
# GPU to qwen3.6 (scripts/sweep_qwen.sh, resumable).
set -u
cd "$(dirname "$0")/.."
until grep -q "wording arms finished" runs/sweep_nemotron3_wording.log 2>/dev/null; do sleep 60; done
echo "[$(date -u +%FT%TZ)] nemotron3 done; starting qwen3.6" >> runs/sweep_qwen3.6.log
bash scripts/sweep_qwen.sh >> runs/sweep_qwen3.6.log 2>&1
