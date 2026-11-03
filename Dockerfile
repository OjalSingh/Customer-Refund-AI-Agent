# Small image for Cloud Run / Fly.io. Uses a hosted model or the offline mode,
# since Ollama runs outside the container.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv export --frozen --no-dev --extra hosted --no-emit-project -o requirements.lock \
    && pip install --no-cache-dir -r requirements.lock

COPY . .
RUN useradd --create-home app
USER app

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
