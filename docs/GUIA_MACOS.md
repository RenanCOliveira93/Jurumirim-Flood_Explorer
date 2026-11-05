# Guia de execução no macOS

Requisitos: macOS (Apple Silicon ou Intel), Python ≥ 3.11 (`brew install python@3.11`), opcional `brew install ffmpeg` para MP4.

```bash
git clone git@github-pessoal:RenanCOliveira93/Jurumirim-Flood_Explorer.git && cd Jurumirim-Flood_Explorer
# PDFs na raiz (só para refazer extrações): PAE-UHE-Jurumirim.pdf, PAE-UHE-Piraju.pdf, PSB_UHE_Piraju.pdf, PAE-UHE-Paranapanema.pdf
make setup     # venv + dependências (rodas arm64 prontas para geopandas/rasterio/pymupdf)
make test
make run       # abre http://localhost:8501
make data      # opcional: refaz extração, vetorização e baixa dados públicos
make dams      # reconstrói dados das barragens a jusante (a partir dos PDFs)
make ocr       # opcional: refaz a leitura OCR das Tabelas 9/10 de Piraju (exige rapidocr)
make piraju    # registro de fontes + verificação das alegações
make notebooks # reexecuta os 6 notebooks
make video     # MP4 da timeline técnica em outputs/ (exige ffmpeg)
```
Sem PDF: `make run` e `make test` funcionam com os dados processados versionados. Sem internet: usa `data/raw` já baixado.
Se um pacote GIS falhar no Apple Silicon: `brew install gdal` e `pip install --no-binary rasterio rasterio`, ou use conda-forge.
