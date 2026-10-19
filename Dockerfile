# Imagen de la API (FastAPI + Jinja2) con los modelos entrenados dentro.
# Los modelos no se versionan (training/models/ está en .gitignore), así que se entrenan aquí,
# en una etapa aparte, y solo los artefactos .joblib pasan a la imagen final.

# ---------- Etapa 1: entrenamiento de M01, M02 y M03 ----------
FROM python:3.13-slim AS entrenamiento
COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /bin/uv
ENV UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app

# Dependencias primero (capa en caché mientras uv.lock no cambie); el grupo jupyter trae
# openpyxl para leer los .xlsx y nbconvert para ejecutar el cuaderno de M01
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --group jupyter --no-install-project

COPY training/ training/
RUN uv run --no-sync python training/train_m02.py \
 && uv run --no-sync python training/notebooks/m03_riesgo_morosidad/entrenamiento.py \
 # El cuaderno usa rutas relativas a training/notebooks
 && cd training/notebooks \
 && uv run --no-sync jupyter nbconvert --to notebook --execute --output-dir /tmp \
      Aprobacion_de_curso_training_model.ipynb \
 && ls -l /app/training/models

# ---------- Etapa 2: aplicación ----------
FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /bin/uv
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

COPY README.md ./
COPY src/ src/
# Instalación editable: los modelos se buscan en <raíz del repo>/training/models
RUN uv sync --frozen --no-dev
COPY --from=entrenamiento /app/training/models/ training/models/

RUN useradd --create-home --uid 1000 app
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=4)"
CMD ["uvicorn", "proyecto_pruebas.app:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
