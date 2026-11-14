#!/bin/bash
# The sweep behind Studies 2 and 3. Two passes: seeds 0 to 19 for every model and study, then
# seeds 20 to 39, so that whenever it stops every cell is filled to the same seed.
# Resumable: finished runs are skipped, so rerun the same command.
#
#   bash scripts/sweep_studies_2_3.sh > runs/sweep_studies_2_3.log 2>&1
set -u
cd "$(dirname "$0")/.."
H=runs/full/gemma4_latest          # the Study 1 handoffs that Study 2 replays
G=gemma4:latest; N=nemotron3:33b; Q=qwen3.6:27b-coding-mxfp8
log() { echo "[$(date -u +%FT%TZ)] $*"; }

for SEEDS in 0-19 20-39; do
  log "pass $SEEDS: gemma4, study 3"
  python3 -m harness.run --lenient --models $G --conditions blocked,derived,blocked_t,derived_t,honest_t --seeds $SEEDS --out runs/organic
  log "pass $SEEDS: gemma4, study 2"
  python3 -m harness.receiver --handoffs $H --receivers $G --seeds $SEEDS --out runs/receiver
  log "pass $SEEDS: nemotron3, study 2"
  python3 -m harness.receiver --handoffs $H --receivers $N --seeds $SEEDS --out runs/receiver
  log "pass $SEEDS: nemotron3, study 3"
  python3 -m harness.run --lenient --models $N --conditions honest,blocked,derived,blocked_t,derived_t,honest_t --seeds $SEEDS --out runs/organic
  log "pass $SEEDS: qwen3.6, study 3, base conditions"
  python3 -m harness.run --lenient --models $Q --conditions blocked,derived --seeds $SEEDS --out runs/organic
  log "pass $SEEDS: qwen3.6, study 2"
  python3 -m harness.receiver --handoffs $H --receivers $Q --seeds $SEEDS --out runs/receiver
done
log "last: qwen3.6, study 3, reasoning-field variants"
python3 -m harness.run --lenient --models $Q --conditions blocked_t,derived_t,honest_t --seeds 0-39 --out runs/organic
log "sweep finished"
