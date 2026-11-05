from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# PDF do PAE de Jurumirim: renomeado pelo usuário (antes CTG-SB-PAEE-2026-R0-JUR.pdf); o nome antigo ainda é aceito.
PDF = ROOT / "PAE-UHE-Jurumirim.pdf"
if not PDF.exists() and (ROOT / "CTG-SB-PAEE-2026-R0-JUR.pdf").exists():
    PDF = ROOT / "CTG-SB-PAEE-2026-R0-JUR.pdf"
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
METADATA = DATA / "metadata"
OUTPUTS = ROOT / "outputs"
# Demais documentos (todos de terceiros, fora do Git). Raiz do projeto; data/raw/PAE_UHE_PIRAJU.pdf ainda é aceito.
PIRAJU_PDF = ROOT / "PAE-UHE-Piraju.pdf"
if not PIRAJU_PDF.exists() and (RAW / "PAE_UHE_PIRAJU.pdf").exists():
    PIRAJU_PDF = RAW / "PAE_UHE_PIRAJU.pdf"
PSB_PIRAJU_PDF = ROOT / "PSB_UHE_Piraju.pdf"
PARANAPANEMA_PDF = ROOT / "PAE-UHE-Paranapanema.pdf"
