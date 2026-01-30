# builder stage
FROM python:3.11-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_PROJECT_ENVIRONMENT="/usr/local"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev


# final stage
FROM python:3.11-slim-bookworm

# setup
ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd -m appuser

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --chown=appuser:appuser src /app/src

# runtime config - 포트 변경: 8020 → 8030
ENV PORT=8030

USER appuser

EXPOSE 8030

# healthcheck - 포트와 경로 수정
HEALTHCHECK --start-period=20s --interval=30s --timeout=3s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; port=os.environ.get('PORT'); urllib.request.urlopen(f'http://localhost:{port}/health')"]

# CMD - 엔트리포인트 경로 수정: gm.main:app → state_db.main:app
CMD ["sh", "-c", "uvicorn state_db.main:app --host 0.0.0.0 --port $PORT"]
