#!/bin/bash
# Exploratory, added on 16 November (see HYPOTHESES.md): a second wording of the request sentence, on the
# same 80 handoffs of the request arm with the request line shown. Needs OPENAI_API_KEY for the OpenAI
# receivers and the `claude` tool for claude-haiku-5-5. Resumable.
#   bash scripts/sweep_request_b.sh        # log: runs/sweep_request_b.log
set -u
cd "$(dirname "$0")/.."
arm() {  # arm <backend> <receiver> <handoff folder> <condition> <label> <seeds>
  python3 -m harness.receiver --request --backend "$1" --receivers "$2" --handoffs "$3" --conditions "$4" \
    --label "$5" --seeds "$6" --signals none --duties request_b --out runs/request
}
(
  for spec in "openai gpt-5.4-nano" "openai gpt-6-luna" "openai gpt-6.1-sol" "claude-cli claude-haiku-5-5" "ollama gemma4:latest"; do
    set -- $spec
    arm "$1" "$2" runs/organic/gpt-6.1-sol blocked partial_sol 0-19 &
    arm "$1" "$2" runs/organic/qwen3.6_27b-coding-mxfp8 blocked partial_qwen 1,2,3,5,6,7,8,9,10,11,13,14,15,16,17,19,20,22,23,24 &
    arm "$1" "$2" runs/full/gemma4_latest wrong miskeyed 0-19 &
    arm "$1" "$2" runs/full/gemma4_latest honest honest 0-19 &
  done
  wait
  echo "[$(date -u +%FT%TZ)] second wording of the request sentence finished"
) > runs/sweep_request_b.log 2>&1
