#!/bin/bash
# The OpenAI API arms: exploratory, added after the second lock. Needs OPENAI_API_KEY in the
# environment. Resumable: finished runs are skipped, so rerun the same command.
#   bash scripts/sweep_openai.sh        # log: runs/sweep_openai.log
set -u
cd "$(dirname "$0")/.."
H=runs/full/gemma4_latest
rcv() { python3 -m harness.receiver --backend openai --handoffs $H --receivers "$1" --seeds "$2" --out runs/receiver; }
org() { python3 -m harness.run --lenient --backend openai --models "$1" --conditions "$2" --seeds "$3" --out runs/organic; }
note() {
  python3 -m harness.receiver --full-report --backend openai --handoffs runs/organic/claude-haiku-5-5 \
    --conditions blocked --signals none,badge,evidence --receivers "$1" --seeds 0-19 --out runs/receiver_note
}
T=honest,blocked,derived
(
  for r in 0-4 5-9 10-14 15-19; do rcv gpt-6.1-sol $r & done
  for m in gpt-6-luna gpt-5.4-nano; do
    for r in 0-9 10-19 20-29 30-39; do rcv $m $r & done
  done
  org gpt-6.1-sol $T 0-9 &
  org gpt-6.1-sol $T 10-19 &
  org gpt-6-luna $T 0-19 &
  org gpt-6-luna $T 20-39 &
  org gpt-5.4-nano $T,honest_t,blocked_t,derived_t 0-19 &
  org gpt-5.4-nano $T,honest_t,blocked_t,derived_t 20-39 &
  for m in gpt-6.1-sol gpt-6-luna gpt-5.4-nano; do note $m & done
  wait
  echo "[$(date -u +%FT%TZ)] openai sweep finished"
) > runs/sweep_openai.log 2>&1
