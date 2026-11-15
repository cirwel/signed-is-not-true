#!/bin/bash
# Regenerates every table, every figure and the report from the run files, in one go.
#   bash scripts/regenerate.sh [out.pdf]        (default: report/signed-is-not-true.pdf)
# Needs matplotlib, pandoc and Google Chrome. Nothing here calls a model.
set -eu
OUT="${1:-}"
case "$OUT" in "" | /*) ;; *) OUT="$PWD/$OUT" ;; esac   # a relative path is taken from the caller's directory
cd "$(dirname "$0")/.."
OUT="${OUT:-$PWD/report/signed-is-not-true.pdf}"

table() {  # table <output file> <module> <args...>; the old file stays if the module fails
  local out="$1"; shift
  python3 -m "$@" > "$out.tmp"
  mv "$out.tmp" "$out"
}

table results/tables.md          harness.analyze          runs/full
table results/tables_receiver.md harness.analyze_receiver runs/receiver
table results/tables_organic.md  harness.analyze_organic  runs/organic
table results/paper_tables.md    harness.paper_tables     runs/receiver runs/organic runs/receiver_note runs/full
table results/tables_request.md  harness.analyze_request  runs/request runs/wording runs/receiver_note

python3 -m harness.figure_chain   runs/full runs/organic results/figure1.png runs/request
python3 -m harness.figure_studies runs/receiver runs/organic results runs/receiver_note runs/request
python3 -m harness.figure         runs/full results/figure_study1.png

python3 -m harness.report_tables   # report/REPORT.src.md -> report/REPORT.md
bash report/build.sh "$OUT"
echo "regenerated: tables, figures, report/REPORT.md, $OUT"
