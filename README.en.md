# Jurumirim Flood Risk Explorer

> **Independent educational study; it does not replace the official PAE, Civil Defense (Defesa Civil) or an engineering assessment.**

A **local** Python/Streamlit app with reproducible notebooks that checks the popular claim that a Jurumirim dam break
would flood the whole city of Piraju (SP, Brazil), **using only the map and tables of the official Emergency Action Plan (PAE)**
(CTG Brasil, *PAE Externo UHE Jurumirim*, CTG-SB-PAEE-2026-R0-JUR, Jan/2026). No independent hydraulic simulation is run;
the PAE is an emergency study, not evidence of an imminent failure; reproducing its map does not validate an independent model.

## Findings (derived from PAE plate, PDF p. 38)
- Modelled reach: ~33 km, from Jurumirim dam to Piraju dam (the PAE does not model beyond it).
- Digitized dam-break envelope (ZAS+ZSS): ≈ 30.4 km² (ZAS ≈ 6.8 km²) — raster-to-vector by colour; uncertainty of metres to tens of metres.
- ≈ 5.3 % of the municipality of Piraju (26.8 of 506 km²) lies inside the envelope, mostly rural/riverside land.
- The largest IBGE-2019 urbanized patch of Piraju is ≈ 2.0 km from the envelope (no intersection). Two small, low-density patches
  intersect marginally (3,326 m² total, ≤ 1.1 % each) — same order as the digitization uncertainty; the PAE itself labels ST-014/015 "Área urbana Pirajú ME".
- Wave arrival at Piraju dam: 1 h 59 min (rise ≥ 0.61 m).
- **Nothing here classifies any address, property or route as safe or unsafe.**

## Quick start (macOS)
```bash
make setup && make test && make run   # http://localhost:8501
```
`make data` rebuilds the pipeline (needs the PAE PDF in the project root and internet). See `docs/` (Portuguese) and `VALIDATION_REPORT.md`.
Labels used throughout: OFFICIAL DATA · DERIVED FROM PAE · EXPLORATORY ESTIMATE · ILLUSTRATION.

## Downstream dams and the dashboard filter
Sources: Jurumirim PAE, **Piraju PAE** (CBA), Piraju **PSB** and **Paranapanema PAE** (Enel); see `docs/SOURCE_REGISTRY.md` (Portuguese).
- **Sidebar filter** (kept across pages): **"Por Barragem Isolada"** (one dam) or **"Todas barragens selecionadas"** (all selected). The *Simulação* page and the other pages follow it.
- Updates are **incremental**: adding a dam never overwrites or changes the ones already selected.
- "All" **overlays isolated scenarios**, each on its own clock (t = 0 at that dam's own breach). It is **not a cascade simulation**; cascade rupture stays **`not_modelled`**.
- Piraju Tables 9/10 are raster images read by OCR with consistency checks, **not engineer-reviewed**. Piraju section positions are **ILLUSTRATION** (km along the OSM river line). The PDFs contain no georeferenced inundation map for Piraju or Paranapanema.
- Commands: `make dams` (uses the versioned OCR output), `make ocr` (optional), `make piraju`. PDFs and PSB-derived data (header "Sigilo: Interno") are git-ignored; the dashboard starts without the PDFs.
- No failure probability, safe/unsafe classification or extrapolation of the 568.00 m scenario is produced.
