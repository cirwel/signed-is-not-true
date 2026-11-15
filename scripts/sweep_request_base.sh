#!/bin/bash
# Exploratory, added on 15 November after a review of the request arm (see HYPOTHESES.md): the same 60
# false dones replayed WITHOUT the request line, under the three prompts that do not refer to it, so that
# what the line adds can be read from a comparison on the same handoffs. Needs OPENAI_API_KEY for the
# OpenAI receivers and the `claude` tool for claude-haiku-5-5. Resumable.
#   bash scripts/sweep_request_base.sh        # log: runs/sweep_request_base.log
set -u
cd "$(dirname "$0")/.."
P=discretion,duty,goal
QS=1,2,3,5,6,7,8,9,10,11,13,14,15,16,17,19,20,22,23,24   # the same 20 reports from qwen3.6 as in the request arm
arm() {  # arm <backend> <receiver> <handoff folder> <condition> <label> <seeds>
  python3 -m harness.receiver --backend "$1" --receivers "$2" --handoffs "$3" --conditions "$4" \
    --label "$5" --seeds "$6" --signals none --duties $P --out runs/request_base
}
(
  for spec in "openai gpt-5.4-nano" "openai gpt-6-luna" "openai gpt-6.1-sol" "claude-cli claude-haiku-5-5" "ollama gemma4:latest"; do
    set -- $spec
    arm "$1" "$2" runs/organic/gpt-6.1-sol blocked partial_sol 0-9 &
    arm "$1" "$2" runs/organic/gpt-6.1-sol blocked partial_sol 10-19 &
    arm "$1" "$2" runs/organic/qwen3.6_27b-coding-mxfp8 blocked partial_qwen 1,2,3,5,6,7,8,9,10,11 &
    arm "$1" "$2" runs/organic/qwen3.6_27b-coding-mxfp8 blocked partial_qwen 13,14,15,16,17,19,20,22,23,24 &
    arm "$1" "$2" runs/full/gemma4_latest wrong miskeyed 0-9 &
    arm "$1" "$2" runs/full/gemma4_latest wrong miskeyed 10-19 &
  done
  wait
  echo "[$(date -u +%FT%TZ)] request baseline finished"
) > runs/sweep_request_base.log 2>&1
