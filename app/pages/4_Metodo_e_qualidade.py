import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import D, data, footer, setup, sidebar_filter, st, tag  # noqa: E402

import pandas as pd  # noqa: E402

from jurumirim import cascade  # noqa: E402

setup("Método e qualidade")
sel = sidebar_filter()

# ------------------------------------------------------------------ Jurumirim (conteúdo original, inalterado)
if "JUR" in sel.dam_ids:
    st.header("UHE Jurumirim")
    prov = data.provenance()
    g = prov["georreferenciamento"]
    st.subheader("Fonte primária")
    st.json(prov["fonte_primaria"])
    st.subheader("Georreferenciamento")
    c1, c2, c3 = st.columns(3)
    c1.metric("RMS (36 pontos de controle)", f"{g['rms_m']:.2f} m")
    c2.metric("Resíduo máximo", f"{g['max_residual_m']:.2f} m")
    c3.metric("Escala", f"{g['scale_x_m_per_pt']:.3f} m/pt")
    st.caption(g["control_points"] + ". Datum: SIRGAS 2000 / UTM 22S (prancha p. 38).")
    st.markdown("**Checagem independente**: distância do ponto central de cada ST ao traço da seção na prancha (m)")
    st.dataframe(pd.Series(g["checagem_independente_m"], name="m").to_frame().T, hide_index=True)
    st.caption(g["checagem_independente_nota"])
    st.subheader("Vetorização das manchas")
    v = prov["vetorizacao"]
    st.write(v["metodo"]); st.write(f"Resolução do render: {v['resolucao_m_px']:.2f} m/pixel.")
    st.dataframe(pd.DataFrame(v["qualidade_por_classe"]).T)
    for lim in v["limitacoes"]:
        st.markdown(f"- {lim}")

# ------------------------------------------------------------------ Piraju
if "PIR" in sel.dam_ids:
    st.header("UHE Piraju")
    v = D.validation()
    st.markdown(tag("DERIVADO") + "  As Tabelas 9 e 10 do PAE Piraju são **imagens** no PDF: foram lidas por OCR (RapidOCR, duas "
                "escalas) e checadas. Não há revisão de engenheiro.", unsafe_allow_html=True)
    if v:
        a, b, c = st.columns(3)
        a.metric("Discordâncias OCR (2 escalas)", f"{len(v['tabela10_discordancias_ocr']) + len(v['tabela9_discordancias_ocr'])}",
                 help=f"{v['n_rupture_rows']} linhas (T10) + {v['n_natural_rows']} (T9) comparadas célula a célula")
        b.metric("RMS da Figura 17 (cruzes UTM)", f"{v['fig17_rms_m']:.1f} m", help=f"{v['fig17_n_control_points']} pontos; {v['fig17_pixel_size_m']} m/px")
        c.metric("9,68 km do eixo → UHE Paranapanema", f"{v['pos_9_68km_to_official_paranapanema_dam_m']} m",
                 help="distância da posição por quilometragem à coordenada oficial do PAE Paranapanema")
        st.markdown(
            f"- **Posição das seções:** por quilometragem sobre o eixo OSM do rio (ILUSTRAÇÃO). A quilometragem OSM até a UHE "
            f"Paranapanema é {v['km_osm_piraju_to_paranapanema_dam']} km (PAE: {v['km_pae_piraju_zas']} km). A coordenada oficial de Piraju "
            f"fica a {v['piraju_official_vs_jurumirim_st017_m']} m do ponto ST-017 do PAE Jurumirim (dois documentos independentes).\n"
            f"- **Rótulos da Figura 17** ficam a {v['label_offset_m_min']}–{v['label_offset_m_max']} m das posições previstas "
            "(caixas de texto ao lado das linhas): só um limite grosseiro, não uma medida de precisão.\n"
            f"- {v['fig17_st08_fix']}.")
    chk = pd.DataFrame(cascade.validate())
    chk["ok"] = chk.ok.map({True: "✅", False: "❌"})
    with st.expander("Validações automáticas (todas)"):
        st.dataframe(chk, hide_index=True, width="stretch")
    st.markdown("**Mancha de Piraju:** indisponível. Os mapas estão no Apêndice 9 (arquivos G5-945-PIR-DE-PAE-0001 e "
                "3308-HID-CBA-A-DE-G00-0001), que o PDF apenas lista. Nada foi vetorizado ou estimado.")

# ------------------------------------------------------------------ Paranapanema
if "PAR" in sel.dam_ids:
    st.header("UHE Paranapanema")
    st.markdown("O PDF traz ficha técnica, cenários HEC-RAS e áreas em texto; as Figuras 2–6 são capturas do HEC-RAS **sem coordenadas "
                "nem grade**, portanto não são georreferenciáveis com pontos de controle. Tempos de chegada e velocidades estão nos mapas "
                "do Anexo 2, que o PDF não inclui.")

# ------------------------------------------------------------------ inconsistências nas fontes (todas as barragens selecionadas)
f = D.facts()
if len(f):
    bad = f[(f.flag.notna()) & f.dam.isin(sel.dam_ids)]
    if len(bad):
        st.subheader("Inconsistências encontradas nas próprias fontes")
        st.caption("Registradas como publicadas; não foram corrigidas nem usadas para derivar nada.")
        st.dataframe(bad[["dam", "label", "value", "unit", "page_printed", "page_pdf", "note"]].rename(columns={
            "dam": "Barragem", "label": "Item", "value": "Valor", "unit": "Unid.", "page_printed": "Pág. impressa",
            "page_pdf": "Pág. PDF", "note": "Observação"}), hide_index=True, width="stretch")

st.subheader("Fontes públicas")
for k, d in data.sources().items():
    with st.expander(k):
        st.json(d)
st.subheader("O que NÃO pode ser inferido")
st.markdown(
    "- Nível de risco de endereços/rotas, ou segurança de imóveis.\n- Probabilidade de rompimento (de qualquer barragem).\n"
    "- Alcance para outras cotas/cenários além dos publicados em cada PAE.\n"
    "- Profundidade/velocidade por pixel ou rua.\n- Efeitos além do trecho modelado de cada PAE.\n"
    "- **Ruptura em cascata** (não modelada): nenhum tempo, mancha ou probabilidade de efeito de uma barragem sobre outra.\n"
    "- Comparação de cotas do DEM com sobrelevação para ‘estender’ a mancha.")
footer()
