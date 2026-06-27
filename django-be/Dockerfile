# Stage 1: Builder
FROM python:3.11.9-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --upgrade pip --no-cache-dir

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Stage 2: Production
FROM python:3.11.9-slim

RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser:appuser /app

COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

WORKDIR /app

COPY --chown=appuser:appuser . .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WEB_CONCURRENCY=4

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "gunicorn config.asgi:application -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"]