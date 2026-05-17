#!/usr/bin/env bash
# Build presentation PDF for Moodle "Upload your draft presentation" (one file).
set -euo pipefail
cd "$(dirname "$0")"
uv run quarto render presentation.qmd
OUT="build/Spotify_Data_Story_draft_presentation.pdf"
npx --yes decktape reveal \
  -s 1280x720 \
  --load-pause 2500 \
  -p 1500 \
  "file://$(pwd)/build/presentation.html" "$(pwd)/$OUT"
echo "Upload this file to Moodle: $(pwd)/$OUT"
