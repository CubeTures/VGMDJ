FROM ghcr.io/astral-sh/uv:0.11.3-python3.13-trixie-slim

WORKDIR /app

RUN pip uninstall -y pip

COPY pyproject.toml uv.lock ./
COPY pykhinsider/ ./pykhinsider/
RUN uv sync --frozen --no-dev --no-cache

COPY src/ ./src/
COPY frontend/build/ ./frontend/build/

ENV CONFIG_DIR=/config TMP_DIR=/tmp MUSIC_DIR=/music

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
