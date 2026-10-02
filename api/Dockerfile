FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg nodejs ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# O contexto do build é a pasta api/. O código Django está em api/api/.
COPY api/ ./

ENV PORT=8080

CMD ["sh", "-c", "gunicorn video_downloader_api.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --timeout 900 --access-logfile - --error-logfile -"]
