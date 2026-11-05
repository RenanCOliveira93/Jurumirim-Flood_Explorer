import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import D, footer, setup, st, tag  # noqa: E402

import pandas as pd  # noqa: E402

from jurumirim import cascade  # noqa: E402

setup("Cascata Jurumirim → Piraju → Paranapanema")
st.error(
    "**Ruptura induzida em cascata NÃO foi simulada nem estudada aqui.** Este painel não estima probabilidade de falha, "
    "tempo de ruptura secundária nem mancha de cascata. Os PAEs de cada barragem adotam ruptura ISOLADA; as manchas "
    "isoladas não podem ser somadas como se fossem uma simulação integrada."
)

reg = pd.DataFrame(cascade.source_registry())
tab_src, tab_cen, tab_ctx, tab_gap, tab_val = st.tabs(
    ["Fontes e alegações", "Cenários A–D", "Contexto numérico", "Lacunas e próximos dados", "Validações"])

with tab_src:
    st.markdown(tag("OFICIAL") + "  Registro de fontes (checksums calculados na execução).", unsafe_allow_html=True)
    st.dataframe(reg[["id", "title", "issuer", "code", "edition", "status", "sha256", "local_path"]], hide_index=True,
                 width="stretch")
    miss = reg[reg.status == "source_unavailable"]
    if len(miss):
        st.warning("Fonte indisponível neste computador: " + ", ".join(miss.title) + ". Os dados já processados continuam disponíveis; "
                   "para reprocessar, coloque o PDF na raiz do projeto e rode `make piraju` / `make dams`.")
    st.warning("O **PSB de Piraju** traz no cabeçalho **'Sigilo: Interno'**. Confirme com a CBA se pode ser divulgado antes de "
               "publicar qualquer derivado; os dados extraídos dele ficam fora do Git e fora da exportação.")
    st.subheader("Alegações do complemento, conferidas contra o PDF do PAE Piraju")
    st.caption("Páginas do complemento = numeração IMPRESSA do PAE Piraju (PDF = impressa + 1). Conferência: leitura das páginas "
               "renderizadas pelo assistente, sem revisão de engenheiro.")
    cl = pd.DataFrame(cascade.verify_claims())
    cl["páginas do PDF com os números"] = cl.found_on_pages.map(lambda p: ", ".join(map(str, p[:6])) + ("…" if len(p) > 6 else ""))
    st.dataframe(cl[["id", "scenario", "page_ref_as_given", "text", "status", "páginas do PDF com os números", "verification_note"]].rename(
        columns={"scenario": "cenário", "page_ref_as_given": "pág. citada (impr.)", "text": "alegação", "verification_note": "conferência"}),
        hide_index=True, width="stretch")

with tab_cen:
    st.dataframe(pd.DataFrame(cascade.scenarios())[["id", "name", "status", "source_document", "source_page", "note"]],
                 hide_index=True, width="stretch")
    st.markdown(tag("OFICIAL") + "  Métricas documentadas.", unsafe_allow_html=True)
    m = cascade.metrics()
    st.dataframe(m[["scenario", "metric", "value", "unit", "source_document", "source_page", "note"]],
                 hide_index=True, width="stretch")
    st.info("Vazão de pico não é hidrograma completo; pico maior que a descarga nominal não comprova falha; a condição inicial do "
            "reservatório importa; nada aqui infere segurança estrutural de nenhuma barragem.")
    st.markdown(tag("DERIVADO") + "  Dependências entre barragens (apenas o que as fontes documentam).", unsafe_allow_html=True)
    st.graphviz_chart(
        'digraph G { rankdir=LR; node [shape=box, style=rounded];'
        'J [label="UHE Jurumirim\\n(CTG)"]; P [label="UHE Piraju\\n(CBA)"]; N [label="UHE Paranapanema\\n(Enel)"];'
        'J -> P [label="A: 32,88 km, onda em 1h59\\n(PAE Jurumirim p.38)"];'
        'P -> N [label="C: ZAS 9,68 km, onda em ~19 min (TR 10.000)\\n(PAE Piraju p.62-63 impr.)"];'
        'J -> N [label="D: cascata = not_modelled", style=dotted, color=red, fontcolor=red]; }')

with tab_ctx:
    st.warning("Ordens de grandeza **documentadas**, lado a lado, **sem conclusão**. São cenários diferentes, de estudos diferentes; "
               "pico de vazão ≠ hidrograma; os PAEs não analisam o efeito da onda de uma barragem sobre a outra. Não indica falha "
               "nem segurança.")
    f = D.facts()
    keys = {("JUR", "vol_na_max_normal_hm3"), ("PIR", "vol_na_max_normal_hm3"), ("PAR", "vol_na_max_normal_hm3"),
            ("PIR", "cheia_10000_natural_m3s"), ("PIR", "cheia_10000_amortecida_m3s"), ("PIR", "vert_controlado_cap_m3s"),
            ("PIR", "vert_soleira_livre_m3s"), ("PIR", "descarga_fundo_m3s"), ("PIR", "vazao_projeto_original_m3s"),
            ("PAR", "vazao_projeto_vertedouro_m3s"), ("PAR", "cen_tr10000"), ("PAR", "cen_dam_break")}
    ctx = f[[(d, k) in keys for d, k in zip(f.dam, f.key)]][["dam", "label", "value", "unit", "page_printed", "page_pdf", "flag"]]
    m = cascade.metrics()
    extra = pd.DataFrame([
        dict(dam="JUR", label="Vazão de pico próxima à UHE Piraju, ruptura de Jurumirim (ST-016, km 31,30)",
             value=float(m[m.metric.str.contains("ST-016")].value.iloc[0]), unit="m³/s", page_printed=None, page_pdf=38, flag=None),
        dict(dam="JUR", label="Vazão de pico na brecha de Jurumirim (ST-001)", value=float(m[m.metric.str.contains("brecha")].value.iloc[0]),
             unit="m³/s", page_printed=None, page_pdf=38, flag=None)])
    ctx = pd.concat([extra, ctx], ignore_index=True)
    ctx["barragem"] = ctx.dam.map(lambda d: D.DAMS[d].name)
    st.dataframe(ctx[["barragem", "label", "value", "unit", "page_printed", "page_pdf", "flag"]].rename(columns={
        "label": "Item (como no PAE)", "value": "Valor", "unit": "Unid.", "page_printed": "Pág. impressa", "page_pdf": "Pág. PDF",
        "flag": "Sinalização"}), hide_index=True, width="stretch")
    st.caption("O PAE de Piraju (p. 44 impressa) afirma que a vazão afluente de Piraju depende exclusivamente da defluência de Jurumirim "
               "e que o reservatório de Piraju não tem volume significativo para amortecer cheias. Ele **não** modela a chegada de uma onda "
               "de ruptura de Jurumirim.")

with tab_gap:
    st.markdown("Dados necessários para qualquer estudo de cascata:")
    st.dataframe(pd.DataFrame(cascade.GAPS, columns=["Dado necessário", "Situação", "Próximo passo"]),
                 hide_index=True, width="stretch")
    st.markdown("Pergunta em aberto: sob quais hipóteses de nível inicial, hidrograma incidente e capacidade hidráulico-estrutural "
                "uma barragem poderia ser afetada por uma ruptura hipotética da barragem a montante? "
                "Veja `docs/COMPARACAO_JURUMIRIM_PIRAJU.md`.")

with tab_val:
    v = pd.DataFrame(cascade.validate())
    v["ok"] = v.ok.map({True: "✅", False: "❌"})
    st.dataframe(v, hide_index=True, width="stretch")

footer("Fontes: PAEs de Jurumirim, Piraju e Paranapanema; PSB de Piraju.")
