#!/usr/bin/env bash
# Cria o ambiente virtual e instala dependências (macOS / Apple Silicon).
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-}"
if [ -z "$PY" ]; then
  for c in python3.12 python3.11 python3; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)'; then PY="$c"; break; fi
  done
fi
[ -n "$PY" ] || { echo "Python >= 3.11 não encontrado (brew install python@3.11)"; exit 1; }
echo "Usando $($PY --version)"
$PY -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt
.venv/bin/python -m ipykernel install --user --name python3 >/dev/null 2>&1 || true
command -v ffmpeg >/dev/null 2>&1 || echo "Aviso: ffmpeg ausente — 'make video' exige 'brew install ffmpeg' (os quadros PNG funcionam sem ele)."
[ -f PAE-UHE-Jurumirim.pdf ] || echo "Aviso: coloque PAE-UHE-Jurumirim.pdf na raiz do projeto para reextrair os dados."
echo "Ambiente pronto. Próximos passos: make data | make test | make run"
