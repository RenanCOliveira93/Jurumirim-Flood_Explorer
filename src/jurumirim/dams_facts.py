"""Fatos citáveis dos PAEs/PSB, um a um, com documento e página (impressa e do PDF). Nada inferido.

Conferência: cada valor foi lido no texto do PDF e/ou na página renderizada em 2026-11-05 (inspeção do
assistente, NÃO revisão de engenheiro). Inconsistências internas da fonte são sinalizadas em `flag`.
Os contatos pessoais dos documentos NÃO são reproduzidos.
"""
from __future__ import annotations

VERIFIED = "inspeção da página renderizada/texto do PDF, 2026-11-05 (assistente; sem revisão de engenheiro)"

DOC = {
    "JUR": "PAE Externo UHE Jurumirim, CTG-SB-PAEE-2026-R0-JUR (jan/2026)",
    "PIR": "PAE UHE Piraju, 3308-HID-CBA-A-RT-G00-0001 (emissão 20/10/2025; rev. 5, nov/2025)",
    "PSB": "PSB UHE Piraju – Sumário Executivo, PIR-PS-00-RT rev. 00 (CBA)",
    "PAR": "PAE UHE Paranapanema, GRE.OEM.R.88.BR.H.01111.09.003.08 (rev. 08, 15/12/2025; Enel Green Power)",
}


def _f(dam, doc, key, label, value, unit, printed, pdf, flag=None, note=""):
    return dict(dam=dam, key=key, label=label, value=value, unit=unit, source_document=DOC[doc], page_printed=printed,
                page_pdf=pdf, flag=flag, note=note, verified_by=VERIFIED)


FACTS = [
    # ---- Jurumirim (PDF p.21; numeração impressa não usada nas citações já existentes do projeto)
    _f("JUR", "JUR", "na_max_normal_m", "N.A. máximo normal", 568.00, "m", None, 21),
    _f("JUR", "JUR", "vol_na_max_normal_hm3", "Volume no N.A. máximo normal", 7007.52, "hm³", None, 21),
    _f("JUR", "JUR", "vol_na_max_maximorum_hm3", "Volume no N.A. máximo maximorum", 7701.09, "hm³", None, 21),
    _f("JUR", "JUR", "vol_util_hm3", "Volume útil", 3164.62, "hm³", None, 21),
    _f("JUR", "JUR", "modelagem_trecho_km", "Trecho modelado até a barragem de Piraju", 33, "km (aprox.)", None, 37,
       note="A modelagem termina na barragem de Piraju."),
    # ---- Piraju (PAE)
    _f("PIR", "PIR", "lat_lon", "Coordenadas do empreendimento", "23°9'19,13\"S; 49°22'51,86\"O", "", 13, 14),
    _f("PIR", "PIR", "na_max_maximorum_m", "N.A. máximo maximorum", 533.00, "m", 18, 19),
    _f("PIR", "PIR", "na_max_normal_m", "N.A. máximo normal", 531.50, "m", 18, 19),
    _f("PIR", "PIR", "na_min_normal_m", "N.A. mínimo normal", 531.30, "m", 18, 19),
    _f("PIR", "PIR", "cota_crista_m", "Cota da crista", 534.00, "m", 14, 15),
    _f("PIR", "PIR", "altura_barragem_m", "Altura da barragem", 36.00, "m", 14, 15),
    _f("PIR", "PIR", "comprimento_barragem_m", "Comprimento da barragem", 560.00, "m", 14, 15),
    _f("PIR", "PIR", "vol_na_max_normal_hm3", "Volume do reservatório no N.A. máximo normal", 105.58, "hm³", 14, 15),
    _f("PIR", "PIR", "vert_controlado_cap_m3s", "Vertedouro controlado: capacidade máxima no N.A. 533,00 m (texto)", 2621, "m³/s (aprox.)",
       11, 12, flag="inconsistencia_da_fonte", note="Quadro 1 (p.14 impressa) informa vazão de projeto 2.594,00 m³/s para o mesmo N.A."),
    _f("PIR", "PIR", "vert_controlado_vazao_projeto_m3s", "Vertedouro controlado: vazão de projeto (Quadro 1)", 2594.00, "m³/s", 14, 15,
       flag="inconsistencia_da_fonte", note="Texto da p.11 informa ≈2.621 m³/s."),
    _f("PIR", "PIR", "vert_soleira_livre_m3s", "Vertedouro de soleira livre: capacidade no N.A. 533,00 m", 448, "m³/s", 11, 12),
    _f("PIR", "PIR", "descarga_fundo_m3s", "Descarregador de fundo: capacidade máxima", 414, "m³/s", 11, 12),
    _f("PIR", "PIR", "vazao_projeto_original_m3s", "Vazão de projeto original dos extravasores", 3240, "m³/s", 11, 12,
       note="Exigiria N.A. 533,22 m (sobrelevação de 0,22 m sobre o N.A. máx. maximorum), borda livre 0,78 m."),
    _f("PIR", "PIR", "cheia_10000_natural_m3s", "Cheia decamilenar natural afluente", 4856, "m³/s", 44, 45),
    _f("PIR", "PIR", "cheia_10000_amortecida_m3s", "Cheia decamilenar amortecida por Jurumirim (afluente a Piraju)", 2829, "m³/s", 44, 45),
    _f("PIR", "PIR", "reducao_amortecimento_pct", "Redução pelo amortecimento de Jurumirim", 41.7, "%", 44, 45),
    _f("PIR", "PIR", "na_cheia_10000_amortecida_m", "N.A. do reservatório com a cheia decamilenar amortecida", 532.66, "m", 44, 45),
    _f("PIR", "PIR", "borda_livre_m", "Borda livre resultante (crista 534,00 m)", 1.34, "m", 44, 45),
    _f("PIR", "PIR", "afluencia_depende_de_jurumirim", "Vazão afluente de Piraju depende exclusivamente da defluência de Jurumirim",
       "texto do PAE (sem valor)", "", 44, 45, note="O PAE também afirma que o reservatório de Piraju não tem volume significativo para amortecer cheias."),
    _f("PIR", "PIR", "q_natural_tr2_m3s", "Vazão natural sem ruptura, TR 2 anos", 754.90, "m³/s", 59, 60),
    _f("PIR", "PIR", "q_natural_tr5_m3s", "Vazão natural sem ruptura, TR 5 anos", 1194.86, "m³/s", 59, 60),
    _f("PIR", "PIR", "q_natural_tr10_m3s", "Vazão natural sem ruptura, TR 10 anos", 1527.68, "m³/s", 59, 60),
    _f("PIR", "PIR", "q_natural_tr50_m3s", "Vazão natural sem ruptura, TR 50 anos", 2300.00, "m³/s", 59, 60),
    _f("PIR", "PIR", "q_natural_tr10000_m3s", "Vazão natural sem ruptura, TR 10.000 anos (Quadro 9)", 2827.20, "m³/s", 59, 60,
       flag="inconsistencia_da_fonte", note="Tabela 8 (p.44 impressa) informa 2.829 m³/s para a mesma cheia amortecida."),
    _f("PIR", "PIR", "t9_st00_oddity", "Tabela 9, ST-00 (reservatório): cota máx. para TR 10 anos", 532.70, "m", 61, 62,
       flag="inconsistencia_da_fonte",
       note="É maior que a de TR 50 anos (531,50 m) e difere do N.A. inicial de 531,50 m da ruptura TR 10 anos (Tabela 10); "
            "parece troca de colunas no PAE. Mantido como publicado e não usado em cálculos."),
    _f("PIR", "PIR", "brecha_largura_m", "Brecha: largura (retangular, múltiplos blocos do vertedouro, região central)", 179.50, "m", 60, 61),
    _f("PIR", "PIR", "brecha_altura_m", "Brecha: altura", 20.50, "m", 60, 61),
    _f("PIR", "PIR", "brecha_formacao_min", "Brecha: tempo de formação", 6, "min", 60, 61),
    _f("PIR", "PIR", "ruptura_na_tr10_m", "Ruptura TR 10 anos: nível inicial do reservatório", 531.50, "m", 60, 61),
    _f("PIR", "PIR", "ruptura_na_tr10000_m", "Ruptura TR 10.000 anos: nível inicial do reservatório", 532.70, "m", 60, 61),
    _f("PIR", "PIR", "zas_km", "ZAS (toda a distância até a UHE Paranapanema)", 9.68, "km", 63, 64),
    _f("PIR", "PIR", "zss", "ZSS", "não definida", "", 63, 64),
    _f("PIR", "PIR", "zas_edificacoes", "Edificações na ZAS (HIDROBR 2023): casas e edificações", 84, "un", 63, 64,
       note="Além de 1 casa de força e 1 ponte (SP-270)."),
    _f("PIR", "PIR", "modelo", "Modelo hidrodinâmico", "HEC-RAS 6.3.1 (HIDROBR, mai/2023; MDT Topocart 35,9 km²)", "", 57, 58),
    _f("PIR", "PIR", "estudo_hidrobr", "Memorial do estudo de ruptura", "HBR036-23-CBA-PIR-REL-003_R02", "", 57, 58,
       note="Mapas: G5-945-PIR-DE-PAE-0001 (sem ruptura) e 3308-HID-CBA-A-DE-G00-0001 (ruptura TR 10.000, ZAS). Listados no Apêndice 9; NÃO incluídos neste PDF."),
    _f("PIR", "PIR", "cascata", "Estudo comum de rompimento em cascata", "empreendedores 'em articulação'; o PAE adota ruptura isolada", "",
       58, 59, note="Seção 5.3.1."),
    # ---- PSB Piraju (cabeçalho do documento: 'Sigilo: Interno' -> arquivo psb_facts.csv fica fora do Git)
    _f("PIR", "PSB", "psb_classe", "Classificação (ANEEL RN 1.064/2023)", "Classe B: risco baixo, dano potencial associado alto", "", 9, 10),
    _f("PIR", "PSB", "psb_capacidade_total_hm3", "Capacidade total do reservatório", 105.58, "hm³", 7, 8),
    _f("PIR", "PSB", "psb_capacidade_util_hm3", "Capacidade útil", 3.28, "hm³", 7, 8),
    _f("PIR", "PSB", "psb_vazao_projeto_tr10000_m3s", "Vazão máxima de projeto (TR 10.000 anos)", 2829, "m³/s", 7, 8),
    # ---- Paranapanema (PAE; "PAGE n of 21" = página do PDF)
    _f("PAR", "PAR", "lat_lon", "Coordenadas da usina", "S 23°11'16\"; W 49°23'04\"", "", 5, 5),
    _f("PAR", "PAR", "potencia_mw", "Potência instalada", 31.5, "MW", 5, 5),
    _f("PAR", "PAR", "primeiro_enchimento", "Ano do primeiro enchimento", 1958, "", 5, 5),
    _f("PAR", "PAR", "classe", "Classificação", "B (risco baixo, dano potencial associado alto)", "", 4, 4),
    _f("PAR", "PAR", "na_max_normal_m", "N.A. máximo normal (montante)", 504.77, "m", 5, 5),
    _f("PAR", "PAR", "na_max_maximorum_m", "N.A. máximo maximorum (montante)", 505.88, "m", 5, 5),
    _f("PAR", "PAR", "cota_crista_m", "Cota da crista (vertedouro controlado, contrafortes)", 506.80, "m", 5, 5),
    _f("PAR", "PAR", "vol_na_max_normal_hm3", "Volume total no N.A. máximo normal", 12.2, "hm³", 5, 5),
    _f("PAR", "PAR", "vol_na_max_maximorum_hm3", "Volume total no N.A. máximo maximorum", 14.10, "hm³", 5, 5),
    _f("PAR", "PAR", "area_na_max_normal_km2", "Área inundada no N.A. máximo normal", 1.71, "km²", 5, 5, flag="inconsistencia_da_fonte",
       note="Ficha informa 18,24 km² no N.A. máx. maximorum (≈10× maior para +1,1 m): valor suspeito; não usado."),
    _f("PAR", "PAR", "area_na_max_maximorum_km2", "Área inundada no N.A. máximo maximorum", 18.24, "km²", 5, 5, flag="inconsistencia_da_fonte"),
    _f("PAR", "PAR", "vazao_projeto_vertedouro_m3s", "Vazão de projeto do vertedouro (TR 1.000 anos)", 2315.00, "m³/s", 5, 5),
    _f("PAR", "PAR", "qmlt_m3s", "Vazão média de longo termo", 224, "m³/s", 5, 5),
    _f("PAR", "PAR", "cen_tr100", "Cenário HEC-RAS 1: TR 100 anos, vazão 1.652,57 m³/s, N.A. montante 504,77 m", 1652.57, "m³/s", 14, 14),
    _f("PAR", "PAR", "cen_tr10000", "Cenário HEC-RAS 2: TR 10.000 anos, vazão 2.800,00 m³/s, N.A. montante 506,75 m", 2800.00, "m³/s", 14, 14),
    _f("PAR", "PAR", "cen_dam_break", "Cenário HEC-RAS 3: hidrograma de ruptura hipotética, vazão 2.420,13 m³/s, N.A. montante 505,71 m", 2420.13, "m³/s", 14, 14),
    _f("PAR", "PAR", "cen_vertedouros", "Cenário HEC-RAS 4: abertura total dos vertedouros de comporta, vazão 1.842,00 m³/s, N.A. 506,75 m", 1842.00, "m³/s", 14, 14),
    _f("PAR", "PAR", "contorno_jusante_m", "Condição de contorno de jusante: N.A. do reservatório de Chavantes", 471, "m", 14, 14),
    _f("PAR", "PAR", "area_mancha_km2", "Área total diretamente afetada pela mancha", 3.4, "km² (ordem de grandeza)", 17, 17),
    _f("PAR", "PAR", "zas_km", "ZAS: extensão a jusante, largura = mancha", 10, "km", 18, 18),
    _f("PAR", "PAR", "conclusao_estudo", "Conclusão do estudo de dano incremental",
       "cheias naturais mais desfavoráveis que a própria ruptura", "", 17, 17, note="Citação do texto do PAE Paranapanema (seção 9)."),
    _f("PAR", "PAR", "mapas", "Mapas de inundação (Anexos 1 e 2)", "listados; NÃO incluídos neste PDF (Figuras 2–6 são capturas do HEC-RAS sem coordenadas)", "", 20, 20,
       note="Código do documento: capa/p.2-5 terminam em .08; p.14 em diante em .05 (revisões misturadas)."),
]
