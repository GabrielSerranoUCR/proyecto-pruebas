<!-- Portada -->
<div align="center">

# Universidad de Costa Rica

<br>
<br>

### Pruebas de software (CI0142)

<br>
<br>
<br>

## Informe Final: Etapa 3 — Ejecución, Automatización, Trazabilidad y Decisión de Liberación

<br>
<br>
<br>

**Docente:**
<br>
Minor Sandí Salazar

<br>
<br>
<br>

**Integrantes:**
<br>
Angel Mena Coudin | C34789
<br>
Gabriel Serrano Rojas | C17497
<br>
Juan José Víquez Ríos | C38567
<br>
Josué Torres Sibaja | C37853
<br>
Rolando Villavicencio González | C28489

<br>
<br>
<br>

**Fecha:**
<br>
20 de noviembre de 2026

<br>
<br>
<br>

</div>

<hr>

<br>

## 1. Introducción

El presente documento consolida el cierre del proyecto integrador del curso **Pruebas de Software (CI0142)**. A lo largo de las tres etapas se diseñó, construyó y sometió a un proceso integral de verificación y validación un Sistema Bajo Prueba (SUT, por sus siglas en inglés) basado en una arquitectura web Modelo-Vista-Controlador (MVC) con interfaz de usuario, API REST en FastAPI, tres modelos de aprendizaje automático (Machine Learning) y persistencia de registros de ejecución en PostgreSQL mediante Supabase.

El propósito central de esta tercera etapa consiste en demostrar, mediante evidencia objetiva, trazable y reproducible, la calidad de la solución construida, el rigor en la automatización de pruebas en múltiples capas, la gestión formal del ciclo de vida de los defectos detectados y el sustento técnico para emitir una recomendación formal de liberación (**Go / No-Go**).

---

## 2. Sistema Bajo Prueba (SUT) y Arquitectura Implementada

### 2.1. Arquitectura por componentes

Aunque el lineamiento base del curso exigía como mínimo un modelo por equipo, la solución implementada integra de forma homogénea los tres modelos trabajados por el grupo, bajo un contrato unificado de entrada, salida y manejo de errores:

| Componente | Implementación en el repositorio | Responsabilidad mínima verificada |
|---|---|---|
| **Interfaz de Usuario (UI)** | `src/proyecto_pruebas/views/templates/` (`base.html`, `inicio.html`, `modelo.html`) y `static/` (`predict.js`, `dropdown.js`, `pestanas.js`, `styles.css`). | Despliega los formularios dinámicos para M01 (`/m01`), M02 (`/m02`) y M03 (`/m03`), aplica validaciones preventivas en cliente (rangos, tipos enteros/decimales y dependencias entre campos como fumador $\to$ cigarrillos/día) y presenta predicciones o errores devueltos por la API. |
| **API Backend** | `src/proyecto_pruebas/app.py` y `controllers/` (`api_m01.py`, `api_m02.py`, `api_m03.py`, `pages.py`). | Valida contratos estrictos mediante Pydantic (`strict=True`, `extra="forbid"`), orquesta la inferencia de cada modelo y estandariza las respuestas HTTP (200, 400, 404, 405 y 500). |
| **Componente de ML** | `src/proyecto_pruebas/models/` (`m01.py`, `m02.py`, `m03.py`) y `training/`. | **M01 (Educación):** Clasificación binaria de aprobación de curso.<br>**M02 (Salud):** Regresión Ridge para presión arterial sistólica (`sysBP` en mmHg).<br>**M03 (Finanzas):** Clasificación multiclase con Random Forest para riesgo de morosidad (`bajo`, `medio`, `alto`). |
| **Persistencia (PostgreSQL / Supabase)** | `src/proyecto_pruebas/logs_supabase.py`, `middleware_logs.py` y `supabase/logs_modelos.sql`. | Intercepta toda solicitud a `/predict/<modelo>` mediante `LogMiddleware` y persiste en segundo plano (`BackgroundTask`) el registro en `logs_m01`, `logs_m02` o `logs_m03` con diseño *fail-soft* (si la BD no está disponible, registra en terminal sin interrumpir la respuesta). |
| **Infraestructura y CI/CD** | `Dockerfile`, `.github/workflows/tests.yml` y `.github/workflows/deploy.yml`. | Construcción multi-etapa que entrena los artefactos `.joblib`, ejecuta análisis estático (`pylint`), corre la batería automatizada (`pytest`) y despliega continuamente en Coolify. |

### 2.2. Contratos de la API y códigos de estado HTTP

Los contratos detallados de cada endpoint se encuentran documentados en [`docs/contrato_api_m01.md`](contrato_api_m01.md), [`docs/contrato_api_m02.md`](contrato_api_m02.md) y [`docs/contrato_api_m03.md`](contrato_api_m03.md).

- **Respuesta exitosa (`HTTP 200 OK`):** Incluye de forma obligatoria `id_ejecucion` (UUID v4), `fecha` (`AAAA-MM-DD`), `hora` (`HH:MM:SS`), `modelo` (`M01`, `M02` o `M03`), `prediccion` (redondeada a 2 decimales en regresión o clase/probabilidad en clasificación) y el objeto `metrica` con los indicadores del conjunto de prueba.
- **Respuesta de error estandarizada (`HTTP 400`, `404`, `405`, `500`):**
  ```json
  {
    "error": "Parámetro inválido",
    "campo": "age",
    "detalle": "El valor debe ser mayor o igual que 1",
    "errores": [
      {
        "campo": "age",
        "detalle": "El valor debe ser mayor o igual que 1"
      }
    ]
  }
  ```

### 2.3. Seguridad y gestión de configuración

- **Cero secretos en el repositorio:** Ninguna clave ni URL de Supabase se almacena en el código fuente ni en el historial de Git (`.env` está excluido en `.gitignore`). Se provee el archivo `.env.example` con las variables `SUPABASE_URL`, `SUPABASE_KEY` y `SUPABASE_LOGS_ENABLED`.
- **Seguridad en base de datos (RLS):** El script `supabase/logs_modelos.sql` habilita *Row Level Security* en las tablas de logs y otorga permiso exclusivamente de inserción (`FOR INSERT TO anon`), impidiendo que un tercero utilice la clave pública `anon` para extraer datos históricos.
- **Ocultamiento de detalles internos:** El manejador global `@app.exception_handler(Exception)` captura cualquier fallo no controlado y devuelve `{"error": "Error interno del servidor"}` con código `500`, evitando filtrar trazas de ejecución (*stack traces*), rutas del sistema de archivos o variables de entorno.

---

## 3. Estrategia, Diseño y Técnicas de Prueba

### 3.1. Técnicas de diseño aplicadas y justificación

En concordancia con el Plan de Pruebas ([`docs/plan_de_pruebas.md`](plan_de_pruebas.md)) y el Diseño de Pruebas ([`docs/diseño_inicial_de_pruebas.md`](diseño_inicial_de_pruebas.md)), se aplicaron tres técnicas formales de caja negra:

1. **Partición de Equivalencia (PE):**
   - *Justificación:* Permite dividir el dominio de entrada de los 17 campos de M01, 13 campos de M02 y 11 campos de M03 en clases válidas e inválidas (por tipo de dato, presencia de campo obligatorio, categorías permitidas y clases de salida en clasificación) sin necesidad de probar exhaustivamente cada valor posible.
   - *Casos derivados:* `CP-01` a `CP-05`, `CP-10` a `CP-12`, `CP-14`, `CP-22a`, `CP-22b`, `CP-22c`.
2. **Análisis de Valores Límite (AVL / BVA):**
   - *Justificación:* Los defectos en validaciones clínicas, académicas y financieras se concentran en las fronteras de los rangos numéricos. Se probaron los límites exactos y los valores inmediatamente adyacentes fuera de rango (por ejemplo, en M02: `age` en `0`, `1`, `120` y `121`; `cigsPerDay` en `-1`, `0`, `100` y `101`; en M01: `age` en `14`, `15`, `22` y `23`; `absences` en `-1`, `0`, `93` y `94`).
   - *Casos derivados:* `CP-06`, `CP-07`, `CP-23`, `CP-24` y pruebas BVA automatizadas.
3. **Pruebas Basadas en Riesgo (PBR):**
   - *Justificación:* Prioriza los flujos con mayor probabilidad o impacto de fallo identificados en la matriz de riesgos: cumplimiento del contrato JSON de la API, integridad de la inferencia de los modelos ML, resiliencia ante caída de Supabase (*fail-soft*) y prevención de fugas de información en errores 500.
   - *Casos derivados:* `CP-08`, `CP-09`, `CP-13`, `CP-15` a `CP-21`, `CP-25` a `CP-28`.

---

## 4. Automatización de Pruebas e Integración Continua

### 4.1. Batería automatizada (`pytest`)

La batería automatizada se implementó en el directorio `tests/` y se ejecuta de forma repetible mediante un único comando:

```bash
uv run pytest -v --cov=src/proyecto_pruebas --cov-report=term-missing
```

La suite consta de **32 pruebas automatizadas** distribuidas en 7 módulos que cubren todas las capas del sistema (Vistas UI, Controladores API, Modelos ML y Capa de Persistencia en Supabase):

| Archivo de prueba | Capa / Alcance | Requisitos mínimos de la guía cubiertos | Cant. pruebas |
|---|---|---|---|
| `tests/test_api_m02.py` | API + Modelo M02 | Prueba positiva de contrato (`CP-08`), redondeo (`CP-20`), rango fisiológico (`CP-21`), validaciones negativas (campo faltante `CP-09`, tipo cadena `CP-10`, booleano en entero `CP-11`, campo extra `CP-12`, JSON mal formado `CP-13`), valores límite de edad (`CP-06`, `CP-07`) y cigarrillos, y valores clínicos extremos (`CP-24`). | 10 |
| `tests/test_api_m01.py` | API + Modelo M01 | Casos positivos de alto y bajo rendimiento académico (`CP-18`, `CP-19`), campo obligatorio faltante, edad fuera de rango (`14` y `23`) y valores límite de ausencias (`0`, `93`, `-1`, `94`). | 5 |
| `tests/test_api_m03.py` | API + Modelo M03 | Contrato multiclase (`CP-22`), campo faltante `ApplicantIncome` (`CP-05`), categoría inválida en `Property_Area`, ingreso extremo de `100,000 USD` (`CP-23`) e ingreso negativo. | 5 |
| `tests/test_integration.py` | Integración multicapa (API $\to$ Modelo $\to$ Supabase) | Consistencia directa entre endpoint y pipeline `.joblib` (API $\to$ Modelo), persistencia de `RegistroLog` en Supabase (`CP-25`), resiliencia *fail-soft* ante caída de base de datos (`CP-27`) y fallback a terminal con `SUPABASE_LOGS_ENABLED=false`. | 4 |
| `tests/test_security_routes.py` | Seguridad y protocolo HTTP | Ruta/modelo inexistente HTTP 404 (`CP-14`), método no permitido HTTP 405 (`CP-15`) y verificación de no divulgación de *stack traces* ni rutas del servidor ante un fallo interno simulado HTTP 500 (`CP-17`). | 3 |
| `tests/test_ui_views.py` | Interfaz de Usuario (Vistas HTML) | Renderizado de página de inicio (`/`) y despliegue de formularios con los campos propios de cada modelo en `/m01` (`CP-01`), `/m02` (`CP-02`) y `/m03`. | 4 |
| `tests/test_suma.py` | Verificación base del entorno | Prueba humo de verificación de `pytest` de la Etapa 1. | 1 |
| **Total** | **4 capas cubiertas** | **Cumple 100% de los criterios mínimos y extendidos** | **32** |

### 4.2. Evidencia de ejecución y cobertura de código

Resultado de la ejecución de la batería automatizada y análisis de cobertura con `pytest-cov`:

```text
============================= test session starts ==============================
platform linux -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/josuetorres27/GitHub/proyecto-pruebas
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.1.0, anyio-4.15.1
collected 32 items

tests/test_api_m01.py::test_cp18_predict_m01_exitoso_caso_aprobacion PASSED [  3%]
tests/test_api_m01.py::test_cp19_predict_m01_caso_bajo_rendimiento PASSED [  6%]
tests/test_api_m01.py::test_m01_campo_faltante PASSED                    [  9%]
tests/test_api_m01.py::test_m01_edad_fuera_de_rango PASSED               [ 12%]
tests/test_api_m01.py::test_m01_bva_ausencias PASSED                     [ 15%]
tests/test_api_m02.py::test_cp08_predict_m02_exitoso_contrato_completo PASSED [ 18%]
tests/test_api_m02.py::test_cp09_predict_m02_campo_faltante PASSED       [ 21%]
tests/test_api_m02.py::test_cp10_predict_m02_tipo_incorrecto_cadena PASSED [ 25%]
tests/test_api_m02.py::test_cp11_predict_m02_tipo_incorrecto_booleano_en_entero PASSED [ 28%]
tests/test_api_m02.py::test_cp12_predict_m02_campo_adicional_no_permitido PASSED [ 31%]
tests/test_api_m02.py::test_cp13_predict_m02_json_mal_formado PASSED     [ 34%]
tests/test_api_m02.py::test_bva_m02_edad_limites_exactos PASSED          [ 37%]
tests/test_api_m02.py::test_cp06_cp07_bva_m02_edad_fuera_de_limites PASSED [ 40%]
tests/test_api_m02.py::test_bva_m02_cigs_per_day_limites PASSED          [ 43%]
tests/test_api_m02.py::test_cp24_predict_m02_valores_clinicos_extremos PASSED [ 46%]
tests/test_api_m03.py::test_cp22_predict_m03_exitoso_contrato_completo PASSED [ 50%]
tests/test_api_m03.py::test_cp05_m03_campo_obligatorio_faltante PASSED   [ 53%]
tests/test_api_m03.py::test_m03_categoria_invalida PASSED                [ 56%]
tests/test_api_m03.py::test_cp23_m03_valor_extremo_ingreso PASSED        [ 59%]
tests/test_api_m03.py::test_m03_ingreso_negativo_invalido PASSED         [ 62%]
tests/test_integration.py::test_integracion_api_a_modelo PASSED          [ 65%]
tests/test_integration.py::test_cp25_integracion_api_a_persistencia_supabase PASSED [ 68%]
tests/test_integration.py::test_cp27_resiliencia_bd_no_disponible PASSED [ 71%]
tests/test_integration.py::test_persistencia_deshabilitada_fallback_terminal PASSED [ 75%]
tests/test_security_routes.py::test_cp14_ruta_o_modelo_inexistente_retorna_404 PASSED [ 78%]
tests/test_security_routes.py::test_cp15_metodo_no_permitido_retorna_405 PASSED [ 81%]
tests/test_security_routes.py::test_cp17_no_divulgacion_de_informacion_en_error_500 PASSED [ 84%]
tests/test_suma.py::test_suma PASSED                                     [ 87%]
tests/test_ui_views.py::test_cp01_despliegue_formulario_m01 PASSED       [ 90%]
tests/test_ui_views.py::test_cp02_despliegue_formulario_m02 PASSED       [ 93%]
tests/test_ui_views.py::test_despliegue_formulario_m03 PASSED            [ 96%]
tests/test_ui_views.py::test_pagina_inicio_renderiza_modelos PASSED      [100%]

================================ tests coverage ================================
Name                                           Stmts   Miss  Cover
------------------------------------------------------------------
src/proyecto_pruebas/__init__.py                   0      0   100%
src/proyecto_pruebas/app.py                       55     12    78%
src/proyecto_pruebas/controllers/__init__.py       0      0   100%
src/proyecto_pruebas/controllers/api_m01.py        8      0   100%
src/proyecto_pruebas/controllers/api_m02.py        8      0   100%
src/proyecto_pruebas/controllers/api_m03.py        8      0   100%
src/proyecto_pruebas/controllers/pages.py         48      0   100%
src/proyecto_pruebas/logs_supabase.py             64      3    95%
src/proyecto_pruebas/main.py                      22     22     0%
src/proyecto_pruebas/middleware_logs.py           57      2    96%
src/proyecto_pruebas/models/__init__.py            0      0   100%
src/proyecto_pruebas/models/errores.py            15      1    93%
src/proyecto_pruebas/models/m01.py                66      1    98%
src/proyecto_pruebas/models/m02.py                54      1    98%
src/proyecto_pruebas/models/m03.py                62      4    94%
------------------------------------------------------------------
TOTAL                                            467     46    90%
======================== 32 passed in 2.17s =========================
```

Asimismo, la verificación estática sobre todo el paquete `src/` con Pylint arrojó la calificación máxima:

```text
$ uv run pylint src
-------------------------------------------------------------------
Your code has been rated at 10.00/10
```

### 4.3. Integración Continua (GitHub Actions)

Se implementaron dos flujos automatizados en `.github/workflows/`:
1. **`tests.yml` (`Test Suite`):** Se dispara en cada `push` y `pull_request` hacia `main` o `dev`. Instala `uv`, sincroniza dependencias, entrena/genera los artefactos `.joblib` de M01, M02 y M03 y ejecuta `uv run pytest -v --cov=src/proyecto_pruebas`.
2. **`deploy.yml` (`Deploy`):** Ejecuta en paralelo los trabajos `lint` (`pylint src`) y `test` (`pytest`). Solo si ambos aprueban, construye la imagen Docker multi-etapa, la publica en GitHub Container Registry (`GHCR`) y notifica mediante webhook `POST` a Coolify para actualizar el contenedor en producción.

---

## 5. Gestión de Defectos e Incidentes

El equipo aplicó el ciclo formal de gestión de defectos: **Detectar $\to$ Registrar (GitHub Issues) $\to$ Clasificar (Severidad / Prioridad) $\to$ Corregir $\to$ Retest (Confirmación) $\to$ Regresión $\to$ Cerrar**.

Todos los defectos fueron documentados y cerrados con su respectiva evidencia en la sección **GitHub Issues** del repositorio (`Issues #18` a `#22`):

| ID Defecto | Issue GitHub | Título y descripción | Severidad | Prioridad | Componente | Commit de corrección | Retest (Confirmación) y Regresión | Estado |
|---|---|---|---|---|---|---|---|---|
| **DEF-001** | [Issue #18](https://github.com/GabrielSerranoUCR/proyecto-pruebas/issues/18) | Formato de respuesta HTTP 400 inconsistente con el contrato de error y exposición de índice numérico como `campo` ante JSON mal formado. | Alta | Alta | API (`app.py`, `errores.py`) | `33f4b2f` | **Retest:** `test_cp09_predict_m02_campo_faltante` y `test_cp13_predict_m02_json_mal_formado` (`PASS`).<br>**Regresión:** 32/32 pruebas aprobadas. | Cerrado |
| **DEF-002** | [Issue #19](https://github.com/GabrielSerranoUCR/proyecto-pruebas/issues/19) | Respuestas HTTP 404 y 405 devolvían el esquema por defecto de FastAPI en inglés (`{"detail": "Not Found"}`) en lugar del contrato común `{"error": ...}`. | Media | Media | API (`app.py`) | `33f4b2f` | **Retest:** `test_cp14_ruta_o_modelo_inexistente_retorna_404` y `test_cp15_metodo_no_permitido_retorna_405` (`PASS`).<br>**Regresión:** 32/32 pruebas aprobadas. | Cerrado |
| **DEF-003** | [Issue #20](https://github.com/GabrielSerranoUCR/proyecto-pruebas/issues/20) | Desalineación de columnas de entrada en el artefacto entrenado de M01 respecto a las 17 variables definidas en el formulario y contrato `M01Input`. | Alta | Alta | Modelo ML (`M01`) | `801733c` (PR #12) y `2b2f0c6` | **Retest:** `test_cp18_predict_m01_exitoso_caso_aprobacion` y `test_cp19_predict_m01_caso_bajo_rendimiento` (`PASS`).<br>**Regresión:** 32/32 pruebas aprobadas. | Cerrado |
| **DEF-004** | [Issue #21](https://github.com/GabrielSerranoUCR/proyecto-pruebas/issues/21) | Fallo de inserción de logs en Supabase por política RLS (`FOR INSERT TO anon`) al utilizar el modo por defecto `returning="representation"` que exige permiso `SELECT`. | Alta | Alta | Persistencia (`logs_supabase.py`) | `d3d3d42` (PR #13) | **Retest:** Configurado `returning="minimal"`. Verificado en `test_cp25_integracion_api_a_persistencia_supabase` y `test_cp27_resiliencia_bd_no_disponible` (`PASS`). | Cerrado |
| **DEF-005** | [Issue #22](https://github.com/GabrielSerranoUCR/proyecto-pruebas/issues/22) | Fallo HTTP 405 (*Method Not Allowed*) en el job de despliegue continuo hacia el webhook de Coolify por omisión de `--request POST` en `curl`. | Media | Alta | CI/CD (`deploy.yml`) | `83dc8c2` (PR #16) | **Retest:** Ejecución exitosa del workflow `Deploy` en GitHub Actions al actualizar `main` (`PASS`). | Cerrado |

---

## 6. Matriz de Trazabilidad

La siguiente matriz vincula cada requisito funcional (`F1`–`F14`) y no funcional (`RNF`) con su nivel de riesgo, los casos de prueba diseñados, la técnica aplicada, la prueba automatizada o manual ejecutada, el resultado obtenido, los defectos asociados y la decisión de calidad:

| Requisito / Funcionalidad | Riesgo | Caso de prueba | Técnica de diseño | Automatización / Evidencia | Resultado | Defecto asociado | Decisión |
|---|---|---|---|---|---|---|---|
| **F1:** Selección de modelo y despliegue de formulario (UI) | Bajo | `CP-01`, `CP-02` | Partición de equivalencia | `test_ui_views.py::test_cp01_despliegue_formulario_m01`, `test_cp02_despliegue_formulario_m02`, `test_despliegue_formulario_m03` | **Pass** | — | Aceptado |
| **F2:** Validación preventiva de entradas en la UI | Medio | `CP-03`, `CP-04`, `CP-05`, `CP-06`, `CP-07` | Partición de equivalencia / Valores límite | Validación en `predict.js` + pruebas de límites en API (`test_bva_m02_edad_limites_exactos`, `test_cp06_cp07_bva_m02_edad_fuera_de_limites`) | **Pass** | — | Aceptado |
| **F3:** Presentación de resultado y de errores en la UI | Medio | `CP-08`, `CP-09` | Basada en riesgo | Manual en navegador + `test_cp08_predict_m02_exitoso_contrato_completo` y `test_cp09_predict_m02_campo_faltante` | **Pass** | `DEF-001` (Corregido) | Aceptado |
| **F4:** Validación de contrato de entrada por modelo (API) | Alto | `CP-10`, `CP-11`, `CP-12` | Partición de equivalencia | `test_api_m02.py` (`test_cp09` a `test_cp13`), `test_api_m01.py`, `test_api_m03.py` | **Pass** | `DEF-001` (Corregido) | Aceptado |
| **F5:** Enrutamiento e invocación del modelo correcto (API) | Alto | `CP-13`, `CP-14` | Basada en riesgo / Partición de equivalencia | `test_integration.py::test_integracion_api_a_modelo`, `test_security_routes.py::test_cp14_ruta_o_modelo_inexistente_retorna_404` | **Pass** | `DEF-002` (Corregido) | Aceptado |
| **F6:** Estructura de respuesta común y códigos HTTP (API) | Alto | `CP-15` | Basada en riesgo | `test_cp08_predict_m02_exitoso_contrato_completo`, `test_cp18_predict_m01_exitoso_caso_aprobacion`, `test_cp22_predict_m03_exitoso_contrato_completo`, `test_cp15_metodo_no_permitido_retorna_405` | **Pass** | `DEF-001`, `DEF-002` (Corregidos) | Aceptado |
| **F7:** Seguridad básica de rutas y no exposición de trazas (API) | Alto | `CP-16`, `CP-17` | Basada en riesgo | `test_cp10_predict_m02_tipo_incorrecto_cadena`, `test_security_routes.py::test_cp17_no_divulgacion_de_informacion_en_error_500` | **Pass** | — | Aceptado |
| **F8:** Cálculo de predicción — M01 (Aprobación de curso) | Alto | `CP-18`, `CP-19` | Basada en riesgo | `test_api_m01.py::test_cp18_predict_m01_exitoso_caso_aprobacion`, `test_cp19_predict_m01_caso_bajo_rendimiento` | **Pass** | `DEF-003` (Corregido) | Aceptado |
| **F9:** Cálculo de predicción y redondeo — M02 (Presión arterial) | Alto | `CP-20`, `CP-21` | Basada en riesgo | `test_api_m02.py::test_cp08_predict_m02_exitoso_contrato_completo` (verifica `round(pred, 2)` y `80 <= pred <= 250`) | **Pass** | — | Aceptado |
| **F10:** Cálculo de predicción multiclase — M03 (Riesgo de morosidad) | Alto | `CP-22a`, `CP-22b`, `CP-22c` | Partición de equivalencia | `test_api_m03.py::test_cp22_predict_m03_exitoso_contrato_completo` y verificación de umbrales en `entrenamiento.py` | **Pass** | — | Aceptado |
| **F11:** Robustez ante valores extremos o de frontera (Modelos) | Medio | `CP-23`, `CP-24` | Análisis de valores límite | `test_api_m03.py::test_cp23_m03_valor_extremo_ingreso`, `test_api_m02.py::test_cp24_predict_m02_valores_clinicos_extremos` | **Pass** | — | Aceptado |
| **F12:** Almacenamiento de ejecución y resultado en Supabase (BD) | Alto | `CP-25` | Basada en riesgo | `test_integration.py::test_cp25_integracion_api_a_persistencia_supabase` | **Pass** | `DEF-004` (Corregido) | Aceptado |
| **F13:** Verificación de registros históricos almacenados (BD) | Medio | `CP-26` | Basada en riesgo | Verificación en tablas `logs_m01`, `logs_m02` y `logs_m03` en panel de Supabase (lectura restringida al rol `service_role`/consola por política RLS) | **Pass** | — | Aceptado |
| **F14:** Confiabilidad ante base de datos no disponible (*Fail-soft*) | Alto | `CP-27` | Basada en riesgo | `test_integration.py::test_cp27_resiliencia_bd_no_disponible` y `test_persistencia_deshabilitada_fallback_terminal` | **Pass** | `DEF-004` (Corregido) | Aceptado |
| **RNF-01:** Usabilidad de la interfaz para usuario nuevo | Medio | `CP-28` | Basada en riesgo | Prueba manual de flujo completo en `/m01`, `/m02` y `/m03` con agrupación lógica de campos y bloqueo automático de campos dependientes | **Pass** | — | Aceptado |
| **RNF-02:** Mantenibilidad y calidad estática del código | Medio | Análisis estático | Revisión estática | `uv run pylint src` en local y en GitHub Actions (`10.00/10`) | **Pass** | `DEF-005` (Corregido) | Aceptado |

---

## 7. Métricas Consolidadas

### 7.1. Métricas de ejecución y cobertura de pruebas

| Indicador | Valor | Observación |
|---|---|---|
| **Casos del Diseño de Pruebas planificados y diseñados** | 30 casos (`CP-01` a `CP-28`, con `CP-22a/b/c`) | 100% diseñados con precondiciones, entrada y oráculo explícito. |
| **Casos ejecutados** | 30 / 30 (**100% de ejecución**) | Combinación de batería automatizada y verificación manual de UI/Supabase. |
| **Casos aprobados (Pass) / Fallidos (Fail) / Bloqueados** | **30 Aprobados (100%)** / 0 Fallidos / 0 Bloqueados | Tras la corrección y *retest* de `DEF-001` a `DEF-005`. |
| **Pruebas automatizadas en `pytest`** | **32 pruebas** (`32 passed in 2.17s`) | Cubren las 4 capas de la arquitectura (UI, API, Modelos ML y Persistencia). |
| **Cobertura de requisitos funcionales (`F1`–`F14`)** | **14 / 14 (100%)** | Todos los requisitos cuentan con al menos un caso verificado. |
| **Cobertura de código fuente (`pytest-cov` sobre `src/`)** | **90% global** (421 / 467 sentencias) | 100% en controladores (`api_m01`, `api_m02`, `api_m03`, `pages`), 98% en `m01` y `m02`, 96% en `middleware_logs` y 95% en `logs_supabase`. |
| **Calificación de análisis estático (`pylint src`)** | **10.00 / 10** | Sin advertencias ni errores de estilo o complejidad. |

### 7.2. Métricas de defectos

| Clasificación | desglose | Total |
|---|---|---|
| **Por severidad** | Crítica: `0` \| Alta: `3` (`DEF-001`, `DEF-003`, `DEF-004`) \| Media: `2` (`DEF-002`, `DEF-005`) \| Baja: `0` | 5 defectos registrados |
| **Por prioridad** | Alta: `4` (`DEF-001`, `DEF-003`, `DEF-004`, `DEF-005`) \| Media: `1` (`DEF-002`) \| Baja: `0` | 5 defectos registrados |
| **Por componente** | API: `2` \| Modelos ML: `1` \| Persistencia Supabase: `1` \| CI/CD: `1` | 5 defectos registrados |
| **Por estado final** | Abiertos: `0` \| Corregidos, con Retest y Cerrados: `5` (**100% cerrados**) \| Reabiertos: `0` | 0 defectos pendientes |

### 7.3. Métricas de desempeño de los modelos de Machine Learning

Cada modelo fue evaluado sobre su conjunto de prueba independiente (20% de los datos, partición estratificada en clasificación):

| Modelo | Tipo y Algoritmo Seleccionado | Conjunto de Datos (Train / Test) | Métricas en Conjunto de Prueba | Interpretación y Límites del Modelo |
|---|---|---|---|---|
| **M01: Aprobación de curso** | Clasificación binaria (Regresión Logística con preprocesamiento y balanceo) | 395 registros totales (316 train / 79 test), 17 variables | **Accuracy:** `0.6582`<br>**Precision:** `0.3333`<br>**Recall:** `0.6875`<br>**F1-Score:** `0.4490` | Al excluir las notas parciales previas (`G1`, `G2`) para predecir únicamente con variables socioeconómicas y de hábitos al inicio del curso, el poder predictivo es moderado. Se prioriza el *Recall* (68.75%) para identificar posibles aprobaciones/riesgos tempranos. |
| **M02: Presión arterial estimada** | Regresión lineal regularizada (**Ridge Regression** con `StandardScaler` e imputación por mediana) | 4,240 registros del estudio Framingham (3,392 train / 848 test), 13 variables clínicas | **MAE:** `10.8114 mmHg`<br>**RMSE:** `14.3936 mmHg`<br>**R²:** `0.5321` | El modelo explica el 53.21% de la varianza de la presión sistólica con un error medio absoluto de ~10.8 mmHg, consistente con la variabilidad fisiológica clínica sin mediciones invasivas. |
| **M03: Riesgo de morosidad** | Clasificación multiclase (**Random Forest** con umbrales calibrados de probabilidad de rechazo: bajo `< 0.35`, medio `0.35–0.55`, alto `>= 0.55`) | 614 registros (491 train / 123 test), 11 variables financieras | **Accuracy:** `0.8130`<br>**Precision:** `0.8571`<br>**Recall:** `0.4737`<br>**F1-Score:** `0.6102`<br>**Matriz de confusión (0/1):** `[[82, 3], [20, 18]]` | Alta precisión (85.71%) y exactitud general (81.30%). Los tres niveles de riesgo muestran separación monótona en la tasa real de rechazo en prueba: **bajo** (18%), **medio** (40%) y **alto** (89%). |

### 7.4. Tiempos de respuesta medidos

Se ejecutaron 20 solicitudes consecutivas por endpoint (posterior a la carga inicial en caché `@lru_cache` del artefacto `.joblib`) midiendo el tiempo de respuesta de extremo a extremo en la API:

| Escenario / Endpoint | Media (ms) | Mediana (ms) | Mínimo (ms) | Máximo (ms) | Evaluación |
|---|---|---|---|---|---|
| `POST /predict/m01` (Clasificación binaria) | **22.59 ms** | 22.37 ms | 17.65 ms | 28.76 ms | Óptimo (`< 100 ms`) |
| `POST /predict/m02` (Regresión Ridge) | **25.33 ms** | 24.97 ms | 21.56 ms | 31.24 ms | Óptimo (`< 100 ms`) |
| `POST /predict/m03` (Random Forest Multiclase) | **60.54 ms** | 62.81 ms | 43.27 ms | 80.09 ms | Óptimo (`< 100 ms`) |

---

## 8. Riesgos Residuales y Limitaciones Conocidas

1. **Riesgo residual en la precisión predictiva de M01 (Riesgo Medio):** Dado que el modelo M01 utiliza exclusivamente variables demográficas y de hábitos escolares (sin notas previas de exámenes), su exactitud es del 65.8%. *Mitigación:* La respuesta de la API incluye explícitamente el objeto `metrica` y la `probabilidad` en cada predicción para que el usuario final interprete el resultado como una estimación orientativa y no determinista.
2. **Almacenamiento asíncrono *fail-soft* ante caídas prolongadas de Supabase (Riesgo Bajo):** Si Supabase experimenta una caída o falta de credenciales, el sistema garantiza la continuidad del servicio de predicción (`CP-27`) volcando el registro en la salida estándar del contenedor, pero dichos registros no se reenvían automáticamente a la nube cuando Supabase se recupera. *Mitigación:* El contenedor en Coolify conserva los logs de salida estándar para auditoría.
3. **Política RLS de solo inserción para la clave `anon` (Condición de diseño):** Por seguridad, la clave pública `anon` solo tiene permiso `INSERT` en `logs_m01`, `logs_m02` y `logs_m03`. La auditoría y consulta de registros históricos se realiza directamente desde el panel administrativo de Supabase o con credenciales de servicio, evitando exponer datos de otros usuarios en una aplicación sin autenticación.

---

## 9. Decisión de Liberación (Go / No-Go)

### Recomendación Formal: **GO (LIBERAR)**

Con base en la evidencia objetiva recopilada durante el proceso de pruebas, el equipo recomienda dar **GO (Aprobar la liberación)** de la versión `0.1.0` del sistema bajo prueba, sustentado en los siguientes criterios de salida cumplidos:

1. **Cumplimiento del 100% de ejecución y aprobación:** Los 30 casos del diseño de pruebas y las **32 pruebas automatizadas** en `pytest` se ejecutaron con un **100% de aprobación (0 fallos, 0 bloqueos)**.
2. **Cero defectos críticos o altos abiertos:** Los 5 defectos detectados durante el ciclo de desarrollo (`DEF-001` a `DEF-005`) fueron corregidos, sometidos a *retest* exitoso y verificados mediante pruebas de regresión automatizadas.
3. **Alta cobertura y calidad técnica:** Se alcanzó un **90% de cobertura de código** en `src/proyecto_pruebas`, **100% de cobertura de requisitos funcionales** y una calificación de **10.00 / 10 en análisis estático con Pylint**.
4. **Resiliencia y seguridad verificadas:** El sistema valida estrictamente los contratos de entrada (`HTTP 400`), no filtra información sensible ni *stack traces* ante fallos internos (`HTTP 500`, `CP-17`), protege las tablas en Supabase mediante políticas RLS y mantiene su disponibilidad incluso si la base de datos externa falla (`CP-27`).
5. **Desempeño dentro de parámetros esperados:** Los tiempos de respuesta promedio de inferencia se sitúan entre **22.6 ms y 60.5 ms**, muy por debajo del umbral de aceptación para interacción humana en tiempo real.

---

## 10. Lista de Verificación de Entrega y Conclusiones

### 10.1. Lista de verificación oficial

- [x] El repositorio incluye instrucciones claras en `README.md`, archivo `.env.example` y no expone secretos.
- [x] El contrato del API define solicitudes, respuestas JSON, validaciones y códigos HTTP (`docs/contrato_api_m01.md`, `m02.md`, `m03.md`).
- [x] Existe trazabilidad completa desde cada requisito relevante hasta su resultado y defecto (Sección 6).
- [x] Se aplicaron y justificaron tres técnicas de diseño: Partición de Equivalencia, Análisis de Valores Límite y Pruebas Basadas en Riesgo.
- [x] Se documentaron y ejecutaron pruebas positivas, negativas, de integración y no funcionales.
- [x] La automatización con `pytest` supera el mínimo exigido (32 pruebas en 4 capas, 90% de cobertura), es repetible y se ejecuta en CI (GitHub Actions).
- [x] Los defectos corregidos (`DEF-001` a `DEF-005`, Issues `#18` a `#22`) cuentan con *retest* y regresión documentada.
- [x] Las métricas son coherentes con los resultados y la decisión **Go** está sustentada técnicamente.

### 10.2. Conclusiones

1. La implementación de un contrato estricto en la capa de API (Pydantic con `strict=True` y `extra="forbid"`, complementado con manejadores personalizados de excepciones) permitió detectar y contener errores de validación de forma temprana, garantizando respuestas consistentes entre los tres modelos de distinta naturaleza (clasificación binaria, regresión y clasificación multiclase).
2. La automatización de pruebas con `pytest` y su integración en el flujo de GitHub Actions demostraron ser fundamentales para prevenir regresiones al integrar los modelos M01, M02 y M03 y la capa de persistencia en Supabase.
3. El diseño *fail-soft* validado mediante el caso `CP-27` comprobó la importancia de las pruebas no funcionales de confiabilidad: desacoplar la disponibilidad de un servicio externo de auditoría (Supabase) del flujo crítico de negocio evita que fallos de terceros degraden la experiencia del usuario final.
