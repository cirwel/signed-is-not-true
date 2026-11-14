#!/bin/bash
# Exploratory badge wordings for the two small OpenAI receivers; waits for the main OpenAI
# sweep. Needs OPENAI_API_KEY. Resumable.   log: runs/sweep_openai_wording.log
set -u
cd "$(dirname "$0")/.."
until grep -q "openai sweep finished" runs/sweep_openai.log 2>/dev/null; do sleep 20; done
(
  for m in gpt-6-luna gpt-5.4-nano; do
    for r in 0-9 10-19 20-29 30-39; do
      python3 -m harness.receiver --backend openai --handoffs runs/full/gemma4_latest --receivers $m \
        --signals badge_word,badge_sigvalid,badge_sender --seeds $r --out runs/receiver &
    done
  done
  wait
  echo "[$(date -u +%FT%TZ)] openai wording arms finished"
) > runs/sweep_openai_wording.log 2>&1
