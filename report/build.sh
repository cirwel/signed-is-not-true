#!/bin/bash
# Build REPORT.html and the PDF from REPORT.md. Needs pandoc and Google Chrome.
#   bash report/build.sh [output.pdf]     (a relative path is taken from the directory you call it in)
set -euo pipefail
OUT="${1:-}"
case "$OUT" in "" | /*) ;; *) OUT="$PWD/$OUT" ;; esac
cd "$(dirname "$0")"
OUT="${OUT:-$PWD/signed-is-not-true.pdf}"
mkdir -p "$(dirname "$OUT")"
pandoc REPORT.md -f gfm -t html5 -s --metadata pagetitle="Signed Is Not True" -c style.css -o REPORT.html
TMP="$OUT.building"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="$TMP" "file://$PWD/REPORT.html" 2>/dev/null
# Chrome reports nothing useful when it cannot write, so the result is checked here.
if [ ! -s "$TMP" ]; then
  echo "build.sh: Chrome wrote no PDF to $TMP" >&2
  exit 1
fi
mv "$TMP" "$OUT"
echo "$OUT"
