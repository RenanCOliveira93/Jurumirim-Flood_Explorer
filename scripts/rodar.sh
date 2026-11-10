#!/usr/bin/env bash
# Sobe o dashboard em http://localhost:8501 (usa "python -m streamlit",
# que funciona mesmo se a .venv foi movida de pasta).
set -e
cd "$(dirname "$0")/.."

if [ ! -x .venv/bin/python ] || ! .venv/bin/python -c "import streamlit" 2>/dev/null; then
  echo ">> .venv ausente ou quebrada; recriando (make setup)..."
  rm -rf .venv
  make setup
fi

pkill -f "streamlit run" 2>/dev/null || true
(sleep 4; open http://localhost:8501 2>/dev/null || true) &
exec .venv/bin/python -m streamlit run app/Home.py --server.port 8501
