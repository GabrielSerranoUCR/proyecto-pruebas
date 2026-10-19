# Pruebas de Software

## Descripción
La siguiente aplicación es un sistema de ...

## Integrantes del equipo
- Angel Mena Coudin | C34789
- Gabriel Serrano Rojas | C17497
- Juan José Víquez Ríos | C38567
- Josué Torres Sibaja | C37853
- Rolando Villavicencio González | C28489

## Objetivo del proyecto
El objetivo del proyecto es someter la aplicación a un proceso de pruebas, aplicando de forma práctica los conocimientos, estándares, modelos y herramientas de las pruebas de software. Esto incluye principios de pruebas, gestión del proceso de pruebas, verificación y validación, entre otros conceptos clave para evaluar y garantizar la calidad del sistema.

## Preparación del ambiente

El proyecto usa UV como python/package manager, por lo que no es necesario instalar Python ni crear el virtual enviroment ya que UV lo hace automáticamente.

1. Instalar uv:

   - Con pip (cualquier sistema operativo, requiere tener Python instalado):
     ```bash
     pip install uv
     ```
   - macOS/Linux:
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
   - Windows:
     ```powershell
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```

2. Clonar el repositorio y ubicarse en la carpeta del proyecto:
   ```bash
   git clone https://github.com/GabrielSerranoUCR/proyecto-pruebas.git
   cd proyecto-pruebas
   ```
3. Sincronizar el ambiente. Esto descarga la versión de Python indicada en `.python-version`, crea el ambiente virtual en `.venv/` e instala todas las dependencias (incluidas las de desarrollo) definidas en `pyproject.toml`/`uv.lock`:
   ```bash
   uv sync
   ```
4. Copiar `.env.example` a `.env` y completar las variables de entorno necesarias:
   ```bash
   cp .env.example .env
   ```

## Instrucciones para ejecutar el proyecto

Todos los comandos se ejecutan con `uv run`, que automáticamente usa el ambiente virtual del proyecto sin necesidad de activarlo manualmente.

- **Correr la aplicación:**
  ```bash
  uv run proyecto-pruebas
  ```
- **Levantar la aplicación web (FastAPI + Jinja2, en http://127.0.0.1:8000):**

  Los modelos entrenados no se versionan (`training/models/` está en `.gitignore`), por lo que primero se debe generar el modelo de M02:
  ```bash
  uv run --group jupyter python training/train_m02.py
  uv run proyecto-pruebas-api
  ```
  - Interfaz: `/` (inicio con los tres modelos), `/m02` (formulario de M02) y `/m01`, `/m03` (vistas previas, aún sin campos).
  - API: `POST /predict/m02` (presión arterial sistólica estimada). Entradas inválidas devuelven `400` con el detalle de cada campo. El contrato completo está en [`docs/contrato_api_m02.md`](docs/contrato_api_m02.md) y la documentación interactiva en `/docs`.
- **Correr las pruebas (pytest):**
  ```bash
  uv run pytest
  ```
- **Correr el linter (pylint):**
  ```bash
  uv run pylint src
  ```

## Estructura del repositorio.
- `README.md`: documentación del proyecto.
- `pyproject.toml` / `uv.lock`: dependencias del proyecto (ver nota abajo).
- `src/`: código fuente de la aplicación, organizado en MVC:
  - `src/proyecto_pruebas/models/`: modelos (contratos de entrada/salida y lógica de predicción).
  - `src/proyecto_pruebas/views/`: vistas (plantillas Jinja2 y archivos estáticos).
  - `src/proyecto_pruebas/controllers/`: controladores (rutas de la API y de las páginas).
  - `src/proyecto_pruebas/app.py`: aplicación FastAPI que conecta los controladores.
- `tests/`: pruebas automatizadas (pytest).
- `docs/`: documentación adicional del proyecto.
- `evidencias/`: evidencia del plan de pruebas, diseño de pruebas, instalación y verificación del ambiente.

**Nota sobre requirements.txt:** el proyecto usa `uv` como gestor de dependencias, por lo que no se incluye un `requirements.txt`. Las dependencias se declaran en `pyproject.toml` y quedan fijadas en `uv.lock`, que cumple el mismo propósito.

## Enlaces de interes
- [Plan de trabajo](https://docs.google.com/spreadsheets/d/1IGmu08bjfda4OAQALcscwWfYLhLuleYi6xQ7R213txM/edit?usp=sharing)
