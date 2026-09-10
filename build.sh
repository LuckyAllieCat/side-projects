#!/usr/bin/env bash
# Rebuild wordle.html from the word lists, then package it as dist/Wordle.
set -euo pipefail
cd "$(dirname "$0")"
python3 build.py
[ -d .venv ] || { uv venv --system-site-packages .venv -q && uv pip install -q --python .venv/bin/python pywebview pyinstaller; }
.venv/bin/pyinstaller --noconfirm --clean --onefile --windowed --name Wordle \
  --add-data "wordle.html:." \
  --hidden-import gi --hidden-import gi.repository.Gtk --hidden-import gi.repository.WebKit2 \
  --hidden-import webview.platforms.gtk app.py
echo "Built dist/Wordle"
