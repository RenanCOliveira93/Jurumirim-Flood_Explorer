#!/usr/bin/env python
"""Extrai o PAE da UHE Piraju (CBA) se data/raw/PAE_UHE_PIRAJU.pdf existir; senão registra source_unavailable.

Uso:  python scripts/extract_piraju.py [--download]
--download tenta baixar a URL pública candidata (falha com mensagem clara; nada é inventado).
"""
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jurumirim import cascade  # noqa: E402
from jurumirim.paths import PIRAJU_PDF  # noqa: E402


def download() -> bool:
    PIRAJU_PDF.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(cascade.PIRAJU_URL, timeout=30) as r:
            body = r.read()
    except Exception as e:  # noqa: BLE001
        print(f"[piraju] download falhou: {e}")
        return False
    if not body.startswith(b"%PDF"):
        print("[piraju] resposta não é um PDF; descartada.")
        return False
    PIRAJU_PDF.write_bytes(body)
    print(f"[piraju] baixado: {PIRAJU_PDF} ({len(body)} bytes)")
    return True


def main():
    if "--download" in sys.argv and not PIRAJU_PDF.exists():
        download()
    st = cascade.extract_piraju()
    print(f"[piraju] status: {st['status']}")
    if st["status"] == "source_unavailable":
        print("[piraju] PDF ausente. Como obter:")
        for s in st["how_to_obtain"]:
            print("  -", s)
    else:
        print(f"[piraju] {st['n_pages']} páginas, {st['n_evidence']} evidências, {st['n_tables']} tabelas, "
              f"{st['n_figures']} figuras (todas verified=false)")
        for c in cascade.verify_claims():
            print(f"  {c['id']} cenário {c['scenario']}: {c['status']} {c['found_on_pages']}")
    cascade.write_registry()
    bad = [r for r in cascade.validate() if not r["ok"]]
    for r in bad:
        print("[piraju] VALIDAÇÃO FALHOU:", r)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
