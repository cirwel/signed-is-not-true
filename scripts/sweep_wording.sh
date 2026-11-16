#!/bin/bash
# Exploratory, added on 15 November after the cut-off of the locked analyses (see HYPOTHESES.md):
# two more wordings of the instruction that names the check and two of the one that names the
# goal, on the 20 reports of the note-carrying arm (no signal line), for the three receivers
# that stopped those batches when left to decide. Needs OPENAI_API_KEY and the `claude` tool.
#   bash scripts/sweep_wording.sh        # log: runs/sweep_wording.log
set -u
cd "$(dirname "$0")/.."
N=runs/organic/claude-haiku-5-5
W=duty_b,duty_c,goal_b,goal_c
arm() {  # arm <backend> <receiver> <seeds>
  python3 -m harness.receiver --full-report --backend "$1" --receivers "$2" --handoffs $N --conditions blocked \
    --signals none --duties $W --seeds "$3" --out runs/wording
}
(
  for m in gpt-6-luna gpt-6.1-sol; do
    arm openai $m 0-9 &
    arm openai $m 10-19 &
  done
  arm claude-cli claude-haiku-5-5 0-9 &
  arm claude-cli claude-haiku-5-5 10-19 &
  wait
  echo "[$(date -u +%FT%TZ)] wording arm finished"
) > runs/sweep_wording.log 2>&1
