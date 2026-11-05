"""Relatório básico em Markdown com resultados e ressalvas."""
from datetime import date

from . import DISCLAIMER, data


def build_markdown() -> str:
    ov = data.overlap_tables()
    m = ov["municipios"]
    u = ov["urbanizadas"]
    us = data.urban_summary()
    prov = data.provenance()
    pm = m[m.municipio == "Piraju"].iloc[0]
    p = data.polygons().groupby("classe").area_km2.sum()
    lines = [
        "# Relatório básico — Jurumirim Flood Explorer", f"_Gerado em {date.today().isoformat()}_", "",
        f"> **{DISCLAIMER}**", "",
        "## Fonte", f"- {data.SRC_TABLE}", "- Cenário: ruptura isolada em dia seco, N.A. 568,00 m (PAE p. 21, 37, 38).", "",
        "## Resultados (DERIVADO DO PAE)",
        f"- Envoltória ZAS+ZSS digitalizada: {p['ENVOLTORIA_RUPTURA']:.1f} km² (ZAS {p['ZAS']:.1f} km²).",
        f"- Município de Piraju: {pm.area_envoltoria_no_municipio_km2:.1f} km² na envoltória ({pm.pct_do_municipio:.1f} % do município).",
        f"- Maior polígono urbanizado IBGE 2019 de Piraju: {us['main_area_km2']:.1f} km², "
        f"a {us['main_distance_m']/1000:.2f} km da envoltória (sem interseção).",
        f"- {us['n_intersecting']} polígonos urbanizados pequenos (pouco densos) de Piraju intersectam marginalmente a envoltória "
        f"(total {us['intersecting_area_km2']*1e6:,.0f} m²), da ordem da incerteza de digitalização; ST-014/ST-015 são rotuladas pelo PAE como «Área urbana Pirajú ME».", "",
        "## Seções (DADO OFICIAL, PAE p. 38)", data.sections()[["id", "distancia_km", "tempo_chegada_hhmm", "sobrelevacao_m",
                                                               "velocidade_ms", "vazao_pico_m3s"]].to_markdown(index=False), "",
        "## Qualidade", f"- RMS do georreferenciamento: {prov['georreferenciamento']['rms_m']:.2f} m.",
        *[f"- {x}" for x in prov["vetorizacao"]["limitacoes"]], "",
        "## Não inferível",
        "Probabilidade de ruptura; segurança de imóveis/rotas; outras cotas de reservatório; profundidades locais; "
        "efeitos a jusante da UHE Piraju.", "",
        "Em caso de dúvida, consulte a Defesa Civil e o PAE oficial.",
    ]
    return "\n".join(lines)
