FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    gosu \
    ffmpeg \
    && python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt gunicorn \
    && apt-get purge -y --auto-remove build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app \
    && chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--log-level", "info"]

