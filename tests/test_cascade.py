import json

import pymupdf

from jurumirim import cascade


def _fixture_pdf(path):
    """PDF sintético SÓ para testar o pipeline; não é um PAE e nada dele entra no projeto."""
    d = pymupdf.open()
    p = d.new_page()
    p.insert_text((72, 72), "Cheia de projeto decamilenar 4.856 e 2.829 m3/s; nivel 532,66; crista 534,00; borda 1,34; 41,7%.")
    p.insert_text((72, 100), "Pagina 1 de 2")
    p = d.new_page()
    p.insert_text((72, 72), "HEC-RAS; MDT 35,9 km2; UHE Paranapanema 9,68 km; hidrograma; vertedouro; ZAS; cascata.")
    d.save(path)


def test_all_validations_pass():
    bad = [r for r in cascade.validate() if not r["ok"]]
    assert not bad, bad


def test_without_pdf_status_unavailable(tmp_path):
    st = cascade.extract_piraju(piraju_pdf=tmp_path / "nao_existe.pdf", out_dir=tmp_path)
    assert st["status"] == "source_unavailable" and st["how_to_obtain"]


def test_cascade_scenario_always_not_modelled():
    sc = {s["id"]: s for s in cascade.scenarios()}
    assert sc["D"]["status"] == "not_modelled"
    assert set(sc) >= {"A", "B", "C", "C2", "D"}


def test_every_metric_has_document_page_scenario():
    m = cascade.metrics()
    assert m[["source_document", "source_page", "scenario"]].notna().all().all()
    assert set(m.scenario) <= {"A", "B", "C"}


def test_pipeline_processes_pdf_without_code_change(tmp_path):
    pdf = tmp_path / "PAE_UHE_PIRAJU.pdf"
    _fixture_pdf(pdf)
    st = cascade.extract_piraju(piraju_pdf=pdf, out_dir=tmp_path, save_figures=False)
    assert st["status"] == "extracted_pending_review" and st["n_pages"] == 2
    ev = json.loads((tmp_path / "piraju_evidence.json").read_text())
    assert ev and all({"source_page", "source_document", "extraction_method", "verified"} <= set(e) for e in ev)
    assert not any(e["verified"] for e in ev)  # evidências automáticas nunca nascem verificadas
    assert {e["topic"] for e in ev} >= {"cheia_projeto", "modelo_contorno", "paranapanema", "cascata"}
    assert any(e["printed_page"] == 1 for e in ev)


def test_printed_page_label_formats():
    assert cascade._printed_page("Páginas:\n44 de 86\nEmissão") == 44
    assert cascade._printed_page("PAGE\n15 of 21") == 15
    assert cascade._printed_page("sem rótulo") is None


def test_claims_confirmed_against_real_pdf_when_present():
    from jurumirim import paths
    cl = {c["id"]: c for c in cascade.verify_claims()}
    assert all(c["verified"] and c["verified_by"] for c in cl.values())  # conferência registrada
    if paths.PIRAJU_PDF.exists():
        assert all(c["text_match"] and c["page_confirmed"] for c in cl.values())
        assert cl["C-02"]["found_on_pages"] == [45]  # p.44 impressa = p.45 do PDF


def test_claims_text_matching_logic(tmp_path):
    pdf = tmp_path / "p.pdf"
    _fixture_pdf(pdf)
    by_id = {c["id"]: c for c in cascade.verify_claims(pdf)}
    assert by_id["C-02"]["found_on_pages"] == [1] and by_id["C-04"]["found_on_pages"] == [2]
    assert by_id["C-05"]["found_on_pages"] == [] and by_id["C-05"]["status"] == "no_text_match"


def test_claims_without_pdf_still_report_manual_verification(tmp_path):
    cl = cascade.verify_claims(tmp_path / "ausente.pdf")
    assert all(c["text_match"] is None and c["verified"] for c in cl)


def test_registry_covers_all_four_documents_plus_complement():
    reg = {s["id"]: s for s in cascade.source_registry()}
    assert set(reg) == {"SRC-JUR", "SRC-PIR", "SRC-PSB", "SRC-PAR", "SRC-COMPL"}
    assert "Sigilo" in reg["SRC-PSB"]["author_note"]
    assert all(s["status"] in {"available", "source_unavailable", "secondary_checked", "secondary_unverified"} for s in reg.values())


def test_validation_flags_verified_claim_without_manual_record(monkeypatch):
    bad = [dict(c, verified=True, verified_by=None) for c in cascade.verify_claims()]
    monkeypatch.setattr(cascade, "verify_claims", lambda *_: bad)
    assert any(not r["ok"] for r in cascade.validate())
