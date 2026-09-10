# Pruebas de Software

## Descripción
La siguiente aplicación es un sistema de ...

## Integrantes del equipo
- Angel Mena Coudin | C34789
- Gabriel Serrano Rojas | C17497
- Juan José Víquez Ríos | C38567
- Josué Torres Sibaja | C37853
- Rolando Villavicencio Gonzales | C28489

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
- **Correr las pruebas (pytest):**
  ```bash
  uv run pytest
  ```
- **Correr el linter (pylint):**
  ```bash
  uv run pylint src
  ```

## Estructura del repositorio.

## Enlaces de interes
- [Plan de trabajo](https://docs.google.com/spreadsheets/d/1IGmu08bjfda4OAQALcscwWfYLhLuleYi6xQ7R213txM/edit?usp=sharing)
