#!/bin/bash
# Exploratory, added on 15 November after the cut-off of the locked analyses (see HYPOTHESES.md):
# the request carried in the handoff. 80 recorded handoffs are replayed with one more line, the
# refunds the batch called for, under four prompts, to five receivers. Needs OPENAI_API_KEY for
# the OpenAI receivers and the `claude` tool for claude-haiku-5-5. Resumable.
#   bash scripts/sweep_request.sh        # log: runs/sweep_request.log
set -u
cd "$(dirname "$0")/.."
P=discretion,duty,request,goal
QS=1,2,3,5,6,7,8,9,10,11,13,14,15,16,17,19,20,22,23,24   # qwen3.6's first 20 silent partial reports, by seed
arm() {  # arm <backend> <receiver> <handoff folder> <condition> <label> <seeds>
  python3 -m harness.receiver --request --backend "$1" --receivers "$2" --handoffs "$3" --conditions "$4" \
    --label "$5" --seeds "$6" --signals none --duties $P --out runs/request
}
(
  for spec in "openai gpt-5.4-nano" "openai gpt-6-luna" "openai gpt-6.1-sol" "claude-cli claude-haiku-5-5"; do
    set -- $spec
    arm "$1" "$2" runs/organic/gpt-6.1-sol blocked partial_sol 0-19 &
    arm "$1" "$2" runs/organic/qwen3.6_27b-coding-mxfp8 blocked partial_qwen $QS &
    arm "$1" "$2" runs/full/gemma4_latest wrong miskeyed 0-19 &
    arm "$1" "$2" runs/full/gemma4_latest honest honest 0-19 &
  done
  (
    arm ollama gemma4:latest runs/organic/gpt-6.1-sol blocked partial_sol 0-19
    arm ollama gemma4:latest runs/full/gemma4_latest wrong miskeyed 0-19
  ) &
  (
    arm ollama gemma4:latest runs/organic/qwen3.6_27b-coding-mxfp8 blocked partial_qwen $QS
    arm ollama gemma4:latest runs/full/gemma4_latest honest honest 0-19
  ) &
  wait
  echo "[$(date -u +%FT%TZ)] request arm finished"
) > runs/sweep_request.log 2>&1
