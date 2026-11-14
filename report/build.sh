#!/bin/bash
# Build REPORT.html and the PDF from REPORT.md. Needs pandoc and Google Chrome.
#   bash report/build.sh [output.pdf]
set -euo pipefail
cd "$(dirname "$0")"
OUT="${1:-$PWD/signed-is-not-true.pdf}"
pandoc REPORT.md -f gfm -t html5 -s --metadata pagetitle="Signed Is Not True" -c style.css -o REPORT.html
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="$OUT" "file://$PWD/REPORT.html" 2>/dev/null
echo "$OUT"
