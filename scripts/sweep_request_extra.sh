#!/bin/bash
# Extra streams for the upper half of the seeds still to run in the request arm (same commands, disjoint seeds).
set -u
cd "$(dirname "$0")/.."
(
python3 -m harness.receiver --request --backend ollama --receivers "gemma4:latest" --handoffs runs/organic/gpt-6.1-sol --conditions blocked --label partial_sol --seeds 19 --signals none --duties discretion,duty,request,goal --out runs/request &
python3 -m harness.receiver --request --backend ollama --receivers "gemma4:latest" --handoffs runs/organic/qwen3.6_27b-coding-mxfp8 --conditions blocked --label partial_qwen --seeds 24 --signals none --duties discretion,duty,request,goal --out runs/request &
python3 -m harness.receiver --request --backend ollama --receivers "gemma4:latest" --handoffs runs/full/gemma4_latest --conditions wrong --label miskeyed --seeds 11,12,13,14,15,16,17,18,19 --signals none --duties discretion,duty,request,goal --out runs/request &
python3 -m harness.receiver --request --backend ollama --receivers "gemma4:latest" --handoffs runs/full/gemma4_latest --conditions honest --label honest --seeds 11,12,13,14,15,16,17,18,19 --signals none --duties discretion,duty,request,goal --out runs/request &
python3 -m harness.receiver --request --backend openai --receivers "gpt-6-luna" --handoffs runs/organic/gpt-6.1-sol --conditions blocked --label partial_sol --seeds 17,18,19 --signals none --duties discretion,duty,request,goal --out runs/request &
python3 -m harness.receiver --request --backend openai --receivers "gpt-6-luna" --handoffs runs/full/gemma4_latest --conditions honest --label honest --seeds 13,14,15,16,17,18,19 --signals none --duties discretion,duty,request,goal --out runs/request &
python3 -m harness.receiver --request --backend claude-cli --receivers "claude-haiku-5-5" --handoffs runs/full/gemma4_latest --conditions honest --label honest --seeds 16,17,18,19 --signals none --duties discretion,duty,request,goal --out runs/request &
python3 -m harness.receiver --request --backend openai --receivers "gpt-6.1-sol" --handoffs runs/full/gemma4_latest --conditions honest --label honest --seeds 18,19 --signals none --duties discretion,duty,request,goal --out runs/request &
wait
echo "[$(date -u +%FT%TZ)] extra streams finished"
) >> runs/sweep_request_extra.log 2>&1
