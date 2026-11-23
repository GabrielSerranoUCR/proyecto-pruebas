# Proyecto Integrador — Pruebas de Software (CI0142)

**Universidad de Costa Rica** · Escuela de Ciencias de la Computación e Informática (ECCI)  
**Docente:** Minor Sandí Salazar · **Ciclo:** II-2026

---

## Descripción del Sistema Bajo Prueba (SUT)

Esta aplicación constituye el Sistema Bajo Prueba (SUT) desarrollado para el curso **Pruebas de Software (CI0142)**. Implementa una arquitectura web bajo el patrón **Modelo-Vista-Controlador (MVC)** utilizando **FastAPI**, plantillas **Jinja2**, modelos predictivos de **Machine Learning (`scikit-learn`)** y persistencia de registros de ejecución en **PostgreSQL (Supabase)**, con integración y despliegue continuo (**GitHub Actions + Docker + Coolify**).

### Modelos de Machine Learning Integrados

| ID | Sector | Modelo | Tipo y Algoritmo | Vista Web | Endpoint API | Contrato |
|---|---|---|---|---|---|---|
| **M01** | Educación | Aprobación de curso | Clasificación binaria (Regresión Logística) | `/m01` | `POST /predict/m01` | [`docs/contrato_api_m01.md`](docs/contrato_api_m01.md) |
| **M02** | Salud | Presión arterial estimada | Regresión (`Ridge Regression` con `StandardScaler`) | `/m02` | `POST /predict/m02` | [`docs/contrato_api_m02.md`](docs/contrato_api_m02.md) |
| **M03** | Finanzas | Riesgo de morosidad | Clasificación multiclase (Regresión Logística balanceada con umbrales: bajo, medio, alto) | `/m03` | `POST /predict/m03` | [`docs/contrato_api_m03.md`](docs/contrato_api_m03.md) |

---

## Integrantes del Equipo

- **Angel Mena Coudin** | C34789
- **Gabriel Serrano Rojas** | C17497
- **Juan José Víquez Ríos** | C38567
- **Josué Torres Sibaja** | C37853
- **Rolando Villavicencio González** | C28489

---

## Objetivo del Proyecto

Someter una solución mínima funcional con interfaz de usuario, API REST, modelos de Machine Learning y persistencia en base de datos a un proceso integral de pruebas de software. El proyecto abarca el análisis de riesgos, la planificación, el diseño mediante técnicas de caja negra (Partición de Equivalencia, Análisis de Valores Límite y Pruebas Basadas en Riesgo), la automatización multicapa con `pytest`, el análisis estático con `pylint`, la gestión del ciclo de vida de defectos en GitHub Issues, la matriz de trazabilidad y la emisión fundamentada de una decisión de liberación (**Go / No-Go**).

---

## Preparación del Ambiente

El proyecto utiliza **[uv](https://docs.astral.sh/uv/)** como gestor de paquetes y entornos de Python, garantizando reproducibilidad exacta mediante `pyproject.toml` y `uv.lock`.

1. **Instalar `uv`** (si no se encuentra instalado):
   - **Linux / macOS:**
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
   - **Windows (PowerShell):**
     ```powershell
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```
   - **Con `pip`:**
     ```bash
     pip install uv
     ```

2. **Clonar el repositorio y ubicarse en el directorio del proyecto:**
   ```bash
   git clone https://github.com/GabrielSerranoUCR/proyecto-pruebas.git
   cd proyecto-pruebas
   ```

3. **Sincronizar el ambiente virtual e instalar dependencias:**
   Descarga automáticamente la versión de Python indicada en `.python-version` (`3.13`), crea el entorno `.venv/` e instala las dependencias de producción, desarrollo y entrenamiento:
   ```bash
   uv sync --group jupyter
   ```

4. **Configurar las variables de entorno:**
   Copiar la plantilla `.env.example` (que no contiene secretos) a `.env` y completar las credenciales de Supabase si se desea persistencia en la nube:
   ```bash
   cp .env.example .env
   ```

---

## Instrucciones de Ejecución

### 1. Generar los artefactos de los modelos (`.joblib`)

Por buenas prácticas, los binarios entrenados en `training/models/` no se versionan en Git (están excluidos en `.gitignore`). Antes de iniciar la API o ejecutar las pruebas por primera vez en local, genere los tres modelos con los siguientes comandos:

```bash
# Modelo M01 (ejecuta el cuaderno de entrenamiento y exporta el artefacto)
cd training/notebooks && uv run jupyter nbconvert --to notebook --execute --output-dir /tmp Aprobacion_de_curso_training_model.ipynb && cd ../..

# Modelo M02 (entrena Ridge Regression y exporta blood_pressure_ridge_model.joblib)
uv run python training/train_m02.py

# Modelo M03 (compara Regresión Logística y Random Forest por F1, exporta m03_riesgo_morosidad.joblib)
uv run python training/notebooks/m03_riesgo_morosidad/entrenamiento.py
```

### 2. Levantar el servidor web y la API (FastAPI + Jinja2)

```bash
uv run proyecto-pruebas-api
```

Una vez iniciado en `http://127.0.0.1:8000`:
- **Interfaz de usuario:**
  - `http://127.0.0.1:8000/` — Página de inicio con selección de los tres modelos.
  - `http://127.0.0.1:8000/m01` — Formulario de aprobación de curso (M01).
  - `http://127.0.0.1:8000/m02` — Formulario de presión arterial estimada (M02).
  - `http://127.0.0.1:8000/m03` — Formulario de riesgo de morosidad (M03).
- **Documentación interactiva OpenAPI (Swagger UI):**
  - `http://127.0.0.1:8000/docs`

### 3. Ejecución mediante contenedor Docker

El `Dockerfile` multi-etapa entrena automáticamente los tres modelos durante la primera fase de construcción y empaqueta únicamente los artefactos `.joblib` y la aplicación en la imagen final:

```bash
docker build -t proyecto-pruebas .
docker run --rm -p 8000:8000 --env-file .env proyecto-pruebas
```

---

## Ejecución de Pruebas y Análisis de Calidad

### Batería de pruebas automatizadas (`pytest`)

La suite automatizada verifica las cuatro capas del sistema (Vistas HTML, Controladores de API, Modelos ML y Persistencia en Supabase) con **91% de cobertura de código**: 39 pruebas funcionales, de integración y no funcionales, 1,053 pruebas de calidad predictiva guiadas por los datos de prueba y **15 pruebas E2E** con Playwright:

```bash
# Ejecutar todas las pruebas con salida detallada y tabla de cobertura
uv run pytest -v --cov=src/proyecto_pruebas --cov-report=term-missing
```

| Módulo de prueba | Alcance y casos verificados |
|---|---|
| `tests/test_api_m01.py` | Contrato positivo (`CP-18`, `CP-19`), validación de campos faltantes, rangos de edad (`15–22`) y análisis de valores límite en ausencias (`0–93`). |
| `tests/test_api_m02.py` | Contrato positivo (`CP-08`), redondeo a 2 decimales (`CP-20`), rango fisiológico (`CP-21`), validaciones negativas (`CP-09` a `CP-13`), límites de edad (`1–120`) y cigarrillos (`0–100`), y valores clínicos extremos (`CP-24`). |
| `tests/test_api_m03.py` | Contrato multiclase (`CP-22`), alcance de las clases bajo/medio/alto (`CP-22a/b/c`), campo obligatorio faltante (`CP-05`), categoría no permitida, ingreso extremo (`CP-23`) e ingreso negativo. |
| `tests/test_integration.py` | Integración directa API $\to$ Modelo ML, despacho de registros de ejecución hacia Supabase (`CP-25`), resiliencia *fail-soft* ante caída de base de datos (`CP-27`) y fallback a terminal. |
| `tests/test_security_routes.py` | Rutas o modelos inexistentes HTTP 404 (`CP-14`), métodos no permitidos HTTP 405 (`CP-15`), inyección SQL rechazada sin efectos en la BD (`CP-16`) y no divulgación de *stack traces* ni rutas internas ante errores HTTP 500 (`CP-17`). |
| `tests/test_ui_views.py` | Renderizado de la página principal (`/`) y despliegue de los formularios específicos en `/m01` (`CP-01`), `/m02` (`CP-02`) y `/m03`. |
| `tests/test_rendimiento.py` | Tiempo de respuesta por endpoint: 20 solicitudes tras calentamiento, p95 `< 500 ms` (`CP-30`). |
| `tests/test_model_predictive_quality.py` | Envía cada fila de los CSV de prueba a la API y valida su salida (HTTP 200, clase válida, probabilidad en [0, 1]); luego exige umbrales mínimos de Accuracy/Recall/F1 (M01, M03) y MAE/RMSE/R² (M02) (`CP-29`). Los registros mal clasificados se reportan, pero no fallan: un modelo estadístico no acierta cada fila. |

Para ver las métricas y los registros de clasificación incorrectos en la terminal:

```bash
uv run pytest -s -rx tests/test_model_predictive_quality.py
```

M02 es un modelo de regresión; por ello se reportan MAE, RMSE y R² en lugar de métricas de clasificación. M03 requiere el artefacto `training/models/m03_riesgo_morosidad.joblib`; si no está disponible, su evaluación se marca como omitida. Los registros de M03 con variables faltantes se omiten porque el contrato actual de la API no acepta valores nulos.

### Pruebas de extremo a extremo (`Playwright`)

Las pruebas E2E abren la aplicación en un navegador real, llenan los formularios como lo haría una persona y verifican la predicción devuelta por la API. La suite sigue una separación en **tres capas**:

| Capa | Ubicación | Responsabilidad |
|---|---|---|
| **Core** | `tests/e2e/core/` | Infraestructura: levanta Uvicorn en un puerto libre y ofrece acciones primitivas de UI (localizar campos, elegir en el desplegable, enviar). |
| **Negocio** | `tests/e2e/pages/`, `tests/e2e/flows/` | *Page objects* (`InicioPage`, `ModeloPage`) y flujos (`FlujoPrediccion`): qué campos tiene cada formulario y cómo se obtiene una predicción. |
| **Test scripts** | `tests/e2e/test_*.py` | Casos de prueba legibles que solo usan flujos y datos; no contienen selectores. |
| **Datos** | `tests/e2e/data/payloads.py` | Factorías que devuelven copias nuevas de cargas útiles válidas (no se usa base de datos: Supabase queda desactivado). |

```bash
# Instalar el navegador una sola vez
uv run playwright install chromium

# Ejecutar las pruebas E2E
uv run pytest --e2e tests/e2e -v

# Ejecutar solo una capa o un archivo
uv run pytest --e2e tests/e2e/test_movil.py -v
```

Para generar el reporte HTML y las evidencias de una falla (traza, video y captura):

```bash
uv run pytest --e2e tests/e2e -v \
  --html=test-results/reporte-e2e.html --self-contained-html \
  --tracing=retain-on-failure --video=retain-on-failure \
  --screenshot=only-on-failure --output=test-results/playwright
```

En GitHub Actions, cada ejecución sube la carpeta `test-results/` como artifact **`reporte-e2e`** (retención de 14 días), incluso si las pruebas fallan. Se descarga desde la página del workflow → *Artifacts*, se descomprime y se abre `reporte-e2e.html`; las trazas se abren con `uv run playwright show-trace <carpeta>/trace.zip`. La carpeta `test-results/` está en `.gitignore`, así que nunca se sube al repositorio.

Sin el flag `--e2e`, las pruebas E2E se marcan como omitidas, de modo que `uv run pytest` sigue ejecutando únicamente la batería funcional. Las pruebas cubren: navegación y paneles, flujos completos de M01/M02/M03, validación en el navegador, interfaz móvil con pestañas y pantalla de resultado, y manejo de errores 400/500 y de red.

### Integración y despliegue continuo (`.github/workflows/ci.yml`)

Un único flujo **CI/CD** se ejecuta en cada `push` a `main`, `dev`, `feature/**` y `fix/**`, y en cada *pull request* hacia `main` o `dev`:

| Job | Depende de | Qué hace |
|---|---|---|
| `lint` | — | Pylint sobre `src`, `tests` y `training`; hadolint sobre el `Dockerfile`; actionlint sobre los workflows. |
| `models` | — | Entrena M01, M02 y M03 una sola vez y comparte los `.joblib` como artifact `modelos`. |
| `test` | `models` | Un paso por tipo de prueba: contrato API (positivas, negativas y límites), seguridad, vistas UI, integración, calidad predictiva ML y rendimiento. Publica `coverage.xml` combinado como artifact `cobertura`. Falla si un archivo `tests/test_*.py` nuevo no tiene paso asignado. |
| `e2e` | `models` | Pruebas Playwright en Chromium; publica el artifact `reporte-e2e`. |
| `build` | `lint`, `test`, `e2e` | Construye la imagen Docker en todo cambio (valida el `Dockerfile`); solo la publica en GHCR en `main`. |
| `deploy` | `build` | Solo en `push` a `main`: webhook `POST` a Coolify para actualizar el contenedor. |

Los pasos de un mismo job se ejecutan aunque uno anterior falle, de modo que cada ejecución reporta el estado de **todos** los tipos de prueba y de lint.

### Análisis estático de código (`pylint`, `hadolint`, `actionlint`)

```bash
uv run pylint src
uv run pylint tests --disable=redefined-outer-name,missing-function-docstring,duplicate-code
uv run pylint training/data_utils.py training/train_m02.py training/notebooks/m03_riesgo_morosidad/entrenamiento.py \
  --disable=invalid-name,too-many-locals,too-many-arguments,too-many-positional-arguments,wrong-import-position
docker run --rm -i hadolint/hadolint:v2.12.0 < Dockerfile
docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint:1.7.7
```

---

## Persistencia en Supabase y Diseño *Fail-Soft*

El middleware `LogMiddleware` intercepta cada consulta a `/predict/<modelo>` y registra en segundo plano (`BackgroundTask`) la entrada, la salida, el código HTTP, la duración en milisegundos y el `id_ejecucion` (UUID v4) en la tabla correspondiente de Supabase (`logs_m01`, `logs_m02` o `logs_m03`).

1. Ejecutar el script [`supabase/logs_modelos.sql`](supabase/logs_modelos.sql) en el *SQL Editor* de Supabase. El script crea las tablas, habilita *Row Level Security (RLS)* y restringe la clave pública `anon` exclusivamente a operaciones `INSERT` (`returning="minimal"`), protegiendo la confidencialidad de los registros históricos.
2. Definir en `.env`:
   ```env
   SUPABASE_URL=https://<proyecto>.supabase.co
   SUPABASE_KEY=<clave_anon_publica>
   SUPABASE_LOGS_ENABLED=true
   ```
3. **Comportamiento ante fallos (`CP-27`):** Si Supabase no está disponible, faltan las credenciales o `SUPABASE_LOGS_ENABLED=false`, la API **no interrumpe la predicción**: responde normalmente al usuario y vuelca el registro estructurado en la salida estándar del servidor.

---

## Estructura del Repositorio

```text
proyecto-pruebas/
├── .github/workflows/
│   └── ci.yml                  # CI/CD: lint + entrenamiento + pruebas por tipo + E2E + Docker (GHCR) + Coolify
├── docs/
│   ├── Informe_Etapa_1.md      # Informe de la Etapa 1 (Planificación y ambiente)
│   ├── Informe_Etapa_1.pdf     # Versión PDF del Informe de la Etapa 1
│   ├── Informe_Etapa_3.md      # Informe Final: Ejecución, Defectos, Trazabilidad y Decisión Go/No-Go
│   ├── contrato_api_m01.md     # Especificación del contrato REST para M01
│   ├── contrato_api_m02.md     # Especificación del contrato REST para M02
│   ├── contrato_api_m03.md     # Especificación del contrato REST para M03
│   ├── diseño_inicial_de_pruebas.md  # Casos de prueba (CP-01 a CP-28), datos y técnicas
│   └── plan_de_pruebas.md      # Alcance, riesgos, estrategia, recursos, cronograma y métricas
├── evidencias/                 # Capturas y evidencias de verificación de ambiente (Etapa 1)
├── src/proyecto_pruebas/
│   ├── controllers/            # Controladores FastAPI: api_m01.py, api_m02.py, api_m03.py, pages.py
│   ├── models/                 # Modelos MVC y contratos Pydantic: m01.py, m02.py, m03.py, errores.py
│   ├── views/                  # Plantillas Jinja2 (templates/) y activos CSS/JS/Imágenes (static/)
│   ├── app.py                  # Instancia FastAPI, ruteo y manejadores globales de errores HTTP
│   ├── logs_supabase.py        # Cliente Supabase y persistencia fail-soft
│   └── middleware_logs.py      # Middleware de auditoría de tiempos y resultados por solicitud
├── supabase/
│   └── logs_modelos.sql        # Esquema DDL de tablas de logs e índices con políticas RLS
├── tests/                      # Batería de API, integración, calidad predictiva, rendimiento y E2E
│   └── e2e/                    # Playwright: core/ (infra), pages/ + flows/ (negocio), data/ y test_*.py
├── training/                   # Datasets crudos, cuadernos Jupyter y scripts de entrenamiento ML
├── .env.example                # Plantilla de variables de entorno sin secretos
├── Dockerfile                  # Construcción multi-etapa (entrenamiento + servidor Uvicorn)
├── pyproject.toml              # Definición del proyecto y dependencias gestionadas con uv
└── uv.lock                     # Archivo de bloqueo de versiones exactas
```

---

## Documentación y Artefactos de Prueba

- **[Plan de Pruebas (`docs/plan_de_pruebas.md`)](docs/plan_de_pruebas.md)**
- **[Diseño de Casos de Prueba (`docs/diseño_inicial_de_pruebas.md`)](docs/diseño_inicial_de_pruebas.md)**
- **[Informe de la Etapa 1 (`docs/Informe_Etapa_1.md`)](docs/Informe_Etapa_1.md)**
- **[Informe Final — Etapa 3 (`docs/Informe_Etapa_3.md`)](docs/Informe_Etapa_3.md)** *(incluye Matriz de Trazabilidad, Ciclo de Defectos `DEF-001` a `DEF-006`, evidencia de CI, Métricas y Decisión Go/No-Go)*
- **[Registro de Defectos en GitHub Issues](https://github.com/GabrielSerranoUCR/proyecto-pruebas/issues?q=is%3Aissue)**
- **[Plan de Trabajo del Equipo (Google Sheets)](https://docs.google.com/spreadsheets/d/1IGmu08bjfda4OAQALcscwWfYLhLuleYi6xQ7R213txM/edit?usp=sharing)**
