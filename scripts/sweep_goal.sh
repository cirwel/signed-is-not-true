#!/bin/bash
# Exploratory, added after the second lock: the *goal* prompt, which names the aim (the refund
# work is complete and correct) and not one comparison. See HYPOTHESES.md, "Changes after the
# second lock". Needs OPENAI_API_KEY for the OpenAI receivers. Resumable.
#   log: runs/sweep_goal.log
set -u
cd "$(dirname "$0")/.."
H=runs/full/gemma4_latest
N=runs/organic/claude-haiku-5-5
(
  for m in gpt-5.4-nano gpt-6-luna gpt-6.1-sol; do
    python3 -m harness.receiver --full-report --backend openai --handoffs $N --conditions blocked \
      --signals none,badge,evidence --duties goal --receivers $m --seeds 0-19 --out runs/receiver_note &
  done
  for m in gpt-5.4-nano gpt-6-luna; do
    for r in 0-19 20-39; do
      python3 -m harness.receiver --backend openai --handoffs $H --signals none --duties goal \
        --receivers $m --seeds $r --out runs/receiver &
    done
  done
  python3 -m harness.receiver --backend openai --handoffs $H --signals none --duties goal \
    --receivers gpt-6.1-sol --seeds 0-19 --out runs/receiver &
  (
    python3 -m harness.receiver --full-report --backend claude-cli --handoffs $N --conditions blocked \
      --signals none,badge,evidence --duties goal --receivers claude-haiku-5-5 --seeds 0-19 --out runs/receiver_note
    python3 -m harness.receiver --backend claude-cli --handoffs $H --signals none --duties goal \
      --receivers claude-haiku-5-5 --seeds 0-19 --out runs/receiver
  ) &
  (
    python3 -m harness.receiver --full-report --handoffs $N --conditions blocked \
      --signals none,badge,evidence --duties goal --receivers gemma4:latest --seeds 0-19 --out runs/receiver_note
    python3 -m harness.receiver --handoffs $H --signals none --duties goal \
      --receivers gemma4:latest --seeds 0-39 --out runs/receiver
  ) &
  wait
  echo "[$(date -u +%FT%TZ)] goal arm finished"
) > runs/sweep_goal.log 2>&1
