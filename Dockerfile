FROM python:3.14-slim

# uv desde la imagen oficial de Astral; versión fija (nunca :latest)
COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /code

# 1) Solo los archivos de dependencias → esta capa se cachea mientras no cambien
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# 2) Código
COPY app/ ./app
COPY alembic/ ./alembic
COPY alembic.ini ./

ENV PATH="/code/.venv/bin:$PATH"

# Usuario sin privilegios
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
# Un solo worker: un proceso = un dispatcher (con --workers N habría N dispatchers llamando)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
