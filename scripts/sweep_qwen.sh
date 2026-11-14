#!/bin/bash
# qwen3.6's share of Studies 2 and 3, restarted on its own once the faster models had the GPU
# to themselves for long enough. Resumable.
#   bash scripts/sweep_qwen.sh > runs/sweep_qwen3.6.log 2>&1
set -u
cd "$(dirname "$0")/.."
H=runs/full/gemma4_latest
Q=qwen3.6:27b-coding-mxfp8
log() { echo "[$(date -u +%FT%TZ)] $*"; }
log "study 2: $Q seeds 0-9";   python3 -m harness.receiver --handoffs $H --receivers $Q --seeds 0-9 --out runs/receiver
log "study 3: $Q blocked,derived seeds 0-19"; python3 -m harness.run --lenient --models $Q --conditions blocked,derived --seeds 0-19 --out runs/organic
log "study 2: $Q seeds 10-19"; python3 -m harness.receiver --handoffs $H --receivers $Q --seeds 10-19 --out runs/receiver
log "study 3: $Q blocked,derived seeds 20-39"; python3 -m harness.run --lenient --models $Q --conditions blocked,derived --seeds 20-39 --out runs/organic
log "study 2: $Q seeds 20-39"; python3 -m harness.receiver --handoffs $H --receivers $Q --seeds 20-39 --out runs/receiver
log "stream finished"
