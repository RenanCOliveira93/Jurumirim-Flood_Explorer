# NÃO TESTADO (sem Docker na máquina de desenvolvimento). Ver docs/DEPLOY.md.
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app/src STREAMLIT_SERVER_HEADLESS=true STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
EXPOSE 8501
CMD ["sh", "-c", "streamlit run app/Home.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]
