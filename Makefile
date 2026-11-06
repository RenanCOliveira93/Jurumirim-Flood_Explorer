VENV := .venv
PY   := $(VENV)/bin/python

.PHONY: setup fetch build data notebooks test run video frames piraju clean

setup:           ## cria .venv e instala dependências
	./scripts/setup.sh

fetch:           ## baixa dados públicos (IBGE, Copernicus DEM, OSM)
	$(PY) -W ignore scripts/fetch_public_data.py

build:           ## extrai seções, vetoriza manchas e calcula interseções (exige o PDF do PAE)
	$(PY) -W ignore scripts/build_dataset.py

data: fetch build ## pipeline completo de dados

notebooks:       ## gera e executa os notebooks
	$(PY) scripts/make_notebooks.py
	cd notebooks && for n in 0*.ipynb; do ../$(VENV)/bin/jupyter nbconvert --to notebook --execute --inplace "$$n"; done

test:            ## roda a suíte de testes
	$(PY) -m pytest -q

run:             ## abre o dashboard em http://localhost:8501
	(sleep 4; open http://localhost:8501 2>/dev/null || true) &
	$(VENV)/bin/streamlit run app/Home.py

piraju:         ## processa o PAE da Piraju se data/raw/PAE_UHE_PIRAJU.pdf existir (senão registra source_unavailable)
	$(PY) -W ignore scripts/extract_piraju.py

dams:           ## constrói (incrementalmente) dados de Piraju/Paranapanema a partir do OCR versionado
	$(PY) -W ignore scripts/build_dams.py

estimates:      ## ZAS (trechos) + ESTIMATIVAS exploratórias de mancha de Piraju (relevo até a cota do PAE) + validação
	$(VENV)/bin/python scripts/build_estimates.py

exposure:       ## força, extensão lateral, % urbana, altitude e tempos (depende de make estimates)
	$(VENV)/bin/python scripts/build_exposure.py

drone:          ## mapas de relevo (docs/img) e vídeos estilo drone (outputs/; exige ffmpeg; leva alguns minutos)
	$(VENV)/bin/python scripts/build_drone.py

ocr:            ## OPCIONAL: refaz o OCR das tabelas (pip install rapidocr-onnxruntime); depois rode make dams
	$(PY) scripts/ocr_pae_images.py

frames:          ## exporta quadros PNG da timeline técnica
	$(PY) -W ignore -c "import sys; sys.path.insert(0,'src'); from jurumirim import animation; animation.export_frames()"

video:           ## exporta MP4 da timeline (exige ffmpeg)
	$(PY) -W ignore -c "import sys; sys.path.insert(0,'src'); from jurumirim import animation; print(animation.export_mp4())"

clean:
	rm -rf outputs/frames .pytest_cache
