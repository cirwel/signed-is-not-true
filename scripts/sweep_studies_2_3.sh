#!/bin/bash
# The sweep behind Studies 2 and 3: three streams side by side, one per model. Inside a stream
# the cells the hypotheses need come first and seeds are filled in blocks, so whenever a
# stream stops every cell it has reached is filled to the same seed.
# Resumable: finished runs are skipped, so rerun the same command.
#
#   bash scripts/sweep_studies_2_3.sh
#
# Logs: runs/sweep_<model>.log
set -u
cd "$(dirname "$0")/.."
H=runs/full/gemma4_latest          # the Study 1 handoffs that Study 2 replays
G=gemma4:latest; N=nemotron3:33b; Q=qwen3.6:27b-coding-mxfp8
log() { echo "[$(date -u +%FT%TZ)] $*"; }
organic() { log "study 3: $1 $2 seeds $3"; python3 -m harness.run --lenient --models "$1" --conditions "$2" --seeds "$3" --out runs/organic; }
receiver() { log "study 2: $1 seeds $2"; python3 -m harness.receiver --handoffs $H --receivers "$1" --seeds "$2" --out runs/receiver; }
T=blocked_t,derived_t,honest_t     # the same conditions with a reasoning field for W2

(
  organic $G blocked,derived 0-19
  receiver $G 0-19
  organic $G blocked,derived 20-39
  organic $G $T 0-19
  receiver $G 20-39
  organic $G $T 20-39
  log "stream finished"
) > runs/sweep_gemma4.log 2>&1 &

(
  receiver $N 0-19
  organic $N honest,blocked,derived 0-19
  organic $N honest,blocked,derived 20-39
  organic $N $T 0-19
  receiver $N 20-39
  organic $N $T 20-39
  log "stream finished"
) > runs/sweep_nemotron3.log 2>&1 &

(
  organic $Q blocked,derived 0-19
  receiver $Q 0-9
  organic $Q blocked,derived 20-39
  receiver $Q 10-19
  receiver $Q 20-39
  organic $Q $T 0-39
  log "stream finished"
) > runs/sweep_qwen3.6.log 2>&1 &

wait
