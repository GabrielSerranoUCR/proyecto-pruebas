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
| **Componente de ML** | `src/proyecto_pruebas/models/` (`m01.py`, `m02.py`, `m03.py`) y `training/`. | **M01 (Educación):** Clasificación binaria de aprobación de curso.<br>**M02 (Salud):** Regresión Ridge para presión arterial sistólica (`sysBP` en mmHg).<br>**M03 (Finanzas):** Clasificación multiclase de riesgo de morosidad (`bajo`, `medio`, `alto`): regresión logística balanceada elegida por F1 en validación cruzada frente a Random Forest, con umbrales sobre la probabilidad de rechazo. |
| **Persistencia (PostgreSQL / Supabase)** | `src/proyecto_pruebas/logs_supabase.py`, `middleware_logs.py` y `supabase/logs_modelos.sql`. | Intercepta toda solicitud a `/predict/<modelo>` mediante `LogMiddleware` y persiste en segundo plano (`BackgroundTask`) el registro en `logs_m01`, `logs_m02` o `logs_m03` con diseño *fail-soft* (si la BD no está disponible, registra en terminal sin interrumpir la respuesta). |
| **Infraestructura y CI/CD** | `Dockerfile` y `.github/workflows/ci.yml`. | Construcción multi-etapa que entrena los artefactos `.joblib`, ejecuta análisis estático (`pylint`), corre la batería automatizada (`pytest`) y despliega continuamente en Coolify. |

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

La batería se organiza en tres grupos que cubren todas las capas del sistema (Vistas UI, Controladores API, Modelos ML y Capa de Persistencia en Supabase):

| Archivo de prueba | Capa / Alcance | Requisitos mínimos de la guía cubiertos | Cant. pruebas |
|---|---|---|---|
| `tests/test_api_m02.py` | API + Modelo M02 | Prueba positiva de contrato (`CP-08`), redondeo (`CP-20`), rango fisiológico (`CP-21`), validaciones negativas (campo faltante `CP-09`, tipo cadena `CP-10`, booleano en entero `CP-11`, campo extra `CP-12`, JSON mal formado `CP-13`), valores límite de edad (`CP-06`, `CP-07`) y cigarrillos, y valores clínicos extremos (`CP-24`). | 10 |
| `tests/test_api_m01.py` | API + Modelo M01 | Casos positivos de alto y bajo rendimiento académico (`CP-18`, `CP-19`), campo obligatorio faltante, edad fuera de rango (`14` y `23`) y valores límite de ausencias (`0`, `93`, `-1`, `94`). | 5 |
| `tests/test_api_m03.py` | API + Modelo M03 | Contrato multiclase (`CP-22`), alcance de las tres clases `bajo`/`medio`/`alto` (`CP-22a/b/c`), pesos de variables, campo faltante `ApplicantIncome` (`CP-05`), categoría inválida en `Property_Area`, ingreso extremo (`CP-23`) e ingreso negativo. | 7 |
| `tests/test_integration.py` | Integración multicapa (API $\to$ Modelo $\to$ Supabase) | Consistencia directa entre endpoint y pipeline `.joblib` (API $\to$ Modelo), persistencia de `RegistroLog` en Supabase (`CP-25`), resiliencia *fail-soft* ante caída de base de datos (`CP-27`) y fallback a terminal con `SUPABASE_LOGS_ENABLED=false`. | 4 |
| `tests/test_security_routes.py` | Seguridad y protocolo HTTP | Ruta/modelo inexistente HTTP 404 (`CP-14`), método no permitido HTTP 405 (`CP-15`), inyección SQL en campos numéricos y categóricos rechazada con HTTP 400 sin invocar el modelo y con la BD tocada solo por la inserción parametrizada del log (`CP-16`), y no divulgación de *stack traces* ni rutas del servidor ante un fallo interno simulado HTTP 500 (`CP-17`). | 6 |
| `tests/test_ui_views.py` | Interfaz de Usuario (Vistas HTML) | Renderizado de página de inicio (`/`) y despliegue de formularios con los campos propios de cada modelo en `/m01` (`CP-01`), `/m02` (`CP-02`) y `/m03`. | 4 |
| `tests/test_rendimiento.py` | No funcional: rendimiento | Tiempo de respuesta de `/predict/m01`, `/m02` y `/m03` (20 repeticiones tras calentamiento) con percentil 95 `< 500 ms` (`CP-30`, `RNF-03`). | 3 |
| **Subtotal: pruebas funcionales, integración y no funcionales** | | | **39** |
| `tests/test_model_predictive_quality.py` | Componente ML (guiada por datos) | Envía por la API cada registro del conjunto de prueba independiente (79 de M01, 848 de M02 y 123 de M03; 20 registros de M03 con nulos se omiten por contrato) y valida su salida; luego calcula Accuracy/Precision/Recall/F1 y matriz de confusión (clasificación) o MAE/RMSE/R² (regresión) y los compara contra umbrales mínimos de aceptación (`CP-29`). | 1,053 (1,050 parametrizadas por registro + 3 de métricas globales) |
| `tests/e2e/` (Playwright, `--e2e`) | Flujo completo UI $\to$ API $\to$ Modelo en navegador Chromium | Navegación (3), flujos completos M01/M02/M03 y validación en cliente de campos obligatorios y rangos (6), errores de API 400/500 y API sin conexión (3), vista móvil con pestañas y resumen (3). Cubre `CP-03` a `CP-09` y `CP-28`, antes ejecutados de forma manual. | 15 |

La prueba de humo `tests/test_suma.py` de la Etapa 1 se retiró al quedar superada por la batería real.

Comandos de ejecución:

```bash
# Batería principal (unitaria, integración, ML, rendimiento) con cobertura
uv run pytest -v --cov=src/proyecto_pruebas --cov-report=term-missing

# Pruebas E2E en navegador (requiere una vez: uv run playwright install chromium)
uv run pytest --e2e tests/e2e -v
```

### 4.2. Evidencia de ejecución y cobertura de código

Resultado de la ejecución de la batería automatizada y análisis de cobertura con `pytest-cov` (ejecución local del 23 de noviembre de 2026, artefactos `.joblib` regenerados con los scripts de entrenamiento). La salida completa, el reporte HTML de la suite E2E, una captura por prueba E2E y la salida del análisis estático están en [`evidencias/ejecucion_etapa_3/`](../evidencias/ejecucion_etapa_3/README.md):

```text
$ uv run pytest -q --cov=src/proyecto_pruebas --cov-report=term
...
Name                                           Stmts   Miss  Cover
------------------------------------------------------------------
src/proyecto_pruebas/__init__.py                   0      0   100%
src/proyecto_pruebas/app.py                       55     12    78%
src/proyecto_pruebas/controllers/__init__.py       0      0   100%
src/proyecto_pruebas/controllers/api_m01.py        8      0   100%
src/proyecto_pruebas/controllers/api_m02.py        8      0   100%
src/proyecto_pruebas/controllers/api_m03.py        8      0   100%
src/proyecto_pruebas/controllers/pages.py         56      0   100%
src/proyecto_pruebas/logs_supabase.py             64      3    95%
src/proyecto_pruebas/main.py                      22     22     0%
src/proyecto_pruebas/middleware_logs.py           57      2    96%
src/proyecto_pruebas/models/__init__.py            0      0   100%
src/proyecto_pruebas/models/errores.py            15      1    93%
src/proyecto_pruebas/models/m01.py                70      1    99%
src/proyecto_pruebas/models/m02.py                59      1    98%
src/proyecto_pruebas/models/m03.py                63      1    98%
------------------------------------------------------------------
TOTAL                                            485     43    91%
=============== 1072 passed, 35 skipped, 1 warning in 5.59s ===============

$ uv run pytest --e2e tests/e2e -q
=============== 15 passed, 1 warning in 16.68s ===============
```

Las 35 pruebas omitidas corresponden a las 15 pruebas E2E (se ejecutan solo con `--e2e`) y a los 20 registros de M03 con valores nulos, que la API rechaza por contrato y por ello no se evalúan. `main.py` (0%) es el punto de entrada de Uvicorn y no se ejecuta dentro de `TestClient`.

Asimismo, la verificación estática sobre todo el paquete `src/` con Pylint arrojó la calificación máxima:

```text
$ uv run pylint src
-------------------------------------------------------------------
Your code has been rated at 10.00/10
```

### 4.3. Integración Continua (GitHub Actions)

Los flujos originales `tests.yml` (`Test Suite`) y `deploy.yml` (`Deploy`) se unificaron en un único flujo, `.github/workflows/ci.yml` (`CI/CD`), para que ningún despliegue ocurra sin haber pasado **todos** los tipos de prueba y de análisis estático:

| Job | Depende de | Responsabilidad |
|---|---|---|
| `lint` | — | Pylint sobre `src` (sin excepciones), `tests` y `training` (con excepciones justificadas propias de pytest y de scripts de ML); hadolint sobre el `Dockerfile` y actionlint sobre el workflow. |
| `models` | — | Entrena M01, M02 y M03 una vez y comparte los artefactos `.joblib` con `test` y `e2e`. |
| `test` | `models` | Un paso por tipo de prueba: contrato API (positivas, negativas, valores límite), seguridad, vistas UI, integración (API $\to$ modelo $\to$ Supabase y *fail-soft*), calidad predictiva ML (`CP-29`) y rendimiento (`CP-30`). Combina la cobertura y la publica como artifact. Un paso de control falla si un archivo de pruebas nuevo no quedó asignado a ningún tipo. |
| `e2e` | `models` | Suite Playwright en Chromium; publica reporte HTML, trazas, videos y capturas (`reporte-e2e`). |
| `build` | `lint`, `test`, `e2e` | Construye la imagen Docker multi-etapa en todo cambio; solo la publica en GHCR desde `main`. |
| `deploy` | `build` | Solo en `push` a `main`: webhook `POST` a Coolify. |

Los pasos dentro de `lint` y `test` continúan aunque uno anterior falle, por lo que cada ejecución informa el resultado de todos los tipos de prueba. Las ejecuciones citadas abajo corresponden a los flujos previos a la unificación.

Flujos anteriores a la unificación:
1. **`tests.yml` (`Test Suite`):** Se dispara en cada `push` y `pull_request` hacia `main` o `dev`. Instala `uv`, sincroniza dependencias, entrena/genera los artefactos `.joblib` de M01, M02 y M03, ejecuta `uv run pytest -v --cov=src/proyecto_pruebas`, instala Chromium, ejecuta la suite E2E de Playwright y publica el reporte HTML con trazas, videos y capturas de fallos como *artifact* `reporte-e2e`.
2. **`deploy.yml` (`Deploy`):** Ejecuta en paralelo los trabajos `lint` (`pylint src`) y `test` (`pytest`). Solo si ambos aprueban, construye la imagen Docker multi-etapa, la publica en GitHub Container Registry (`GHCR`) y notifica mediante webhook `POST` a Coolify para actualizar el contenedor en producción.

#### Evidencia de ejecuciones exitosa y fallida

| Ejecución | Rama / commit | Resultado | Explicación |
|---|---|---|---|
| [Run 45113205725](https://github.com/GabrielSerranoUCR/proyecto-pruebas/actions/runs/45113205725) (`Test Suite`) | `main`, merge del PR #25 (E2E Playwright) | **Exitosa** | `34 passed, 15 skipped` en la batería principal y `15 passed` en la suite E2E; el job `Deploy` también finalizó con éxito y publicó la imagen. |
| [Run 45119527362](https://github.com/GabrielSerranoUCR/proyecto-pruebas/actions/runs/45119527362) (`Test Suite`) y [45119527231](https://github.com/GabrielSerranoUCR/proyecto-pruebas/actions/runs/45119527231) (`Deploy`) | `main`, merge del PR #26 (pruebas de calidad predictiva) | **Fallida** | La nueva prueba `test_model_predictive_quality.py` exigía que la predicción de **cada** registro coincidiera con su etiqueta real. Con una exactitud esperada de ~62–66%, unas 64 filas fallan por diseño. El pipeline cumplió su función: bloqueó el despliegue (`Deploy` no publica si `test` falla). Se registró como `DEF-006` y se corrigió el oráculo de la prueba (ver sección 5). |
| [Run 39200352604](https://github.com/GabrielSerranoUCR/proyecto-pruebas/actions/runs/39200352604) (`Deploy`) | `main`, PR #15 | **Fallida** | Webhook de Coolify invocado sin `--request POST` (HTTP 405). Registrado como `DEF-005` y corregido en el PR #16 (run 39202132998 exitoso). |

---

## 5. Gestión de Defectos e Incidentes

El equipo aplicó el ciclo formal de gestión de defectos: **Detectar $\to$ Registrar (GitHub Issues) $\to$ Clasificar (Severidad / Prioridad) $\to$ Corregir $\to$ Retest (Confirmación) $\to$ Regresión $\to$ Cerrar**.

Los defectos fueron documentados con su respectiva evidencia en la sección **GitHub Issues** del repositorio (`Issues #18` a `#22` y `#27`):

| ID Defecto | Issue GitHub | Título y descripción | Severidad | Prioridad | Componente | Commit de corrección | Retest (Confirmación) y Regresión | Estado |
|---|---|---|---|---|---|---|---|---|
| **DEF-001** | [Issue #18](https://github.com/GabrielSerranoUCR/proyecto-pruebas/issues/18) | Formato de respuesta HTTP 400 inconsistente con el contrato de error y exposición de índice numérico como `campo` ante JSON mal formado. | Alta | Alta | API (`app.py`, `errores.py`) | `33f4b2f` | **Retest:** `test_cp09_predict_m02_campo_faltante` y `test_cp13_predict_m02_json_mal_formado` (`PASS`).<br>**Regresión:** 32/32 pruebas aprobadas. | Cerrado |
| **DEF-002** | [Issue #19](https://github.com/GabrielSerranoUCR/proyecto-pruebas/issues/19) | Respuestas HTTP 404 y 405 devolvían el esquema por defecto de FastAPI en inglés (`{"detail": "Not Found"}`) en lugar del contrato común `{"error": ...}`. | Media | Media | API (`app.py`) | `33f4b2f` | **Retest:** `test_cp14_ruta_o_modelo_inexistente_retorna_404` y `test_cp15_metodo_no_permitido_retorna_405` (`PASS`).<br>**Regresión:** 32/32 pruebas aprobadas. | Cerrado |
| **DEF-003** | [Issue #20](https://github.com/GabrielSerranoUCR/proyecto-pruebas/issues/20) | Desalineación de columnas de entrada en el artefacto entrenado de M01 respecto a las 17 variables definidas en el formulario y contrato `M01Input`. | Alta | Alta | Modelo ML (`M01`) | `801733c` (PR #12) y `2b2f0c6` | **Retest:** `test_cp18_predict_m01_exitoso_caso_aprobacion` y `test_cp19_predict_m01_caso_bajo_rendimiento` (`PASS`).<br>**Regresión:** 32/32 pruebas aprobadas. | Cerrado |
| **DEF-004** | [Issue #21](https://github.com/GabrielSerranoUCR/proyecto-pruebas/issues/21) | Fallo de inserción de logs en Supabase por política RLS (`FOR INSERT TO anon`) al utilizar el modo por defecto `returning="representation"` que exige permiso `SELECT`. | Alta | Alta | Persistencia (`logs_supabase.py`) | `d3d3d42` (PR #13) | **Retest:** Configurado `returning="minimal"`. Verificado en `test_cp25_integracion_api_a_persistencia_supabase` y `test_cp27_resiliencia_bd_no_disponible` (`PASS`). | Cerrado |
| **DEF-005** | [Issue #22](https://github.com/GabrielSerranoUCR/proyecto-pruebas/issues/22) | Fallo HTTP 405 (*Method Not Allowed*) en el job de despliegue continuo hacia el webhook de Coolify por omisión de `--request POST` en `curl`. | Media | Alta | CI/CD (`deploy.yml`) | `83dc8c2` (PR #16) | **Retest:** Ejecución exitosa del workflow `Deploy` en GitHub Actions al actualizar `main` (`PASS`). | Cerrado |
| **DEF-006** | [Issue #27](https://github.com/GabrielSerranoUCR/proyecto-pruebas/issues/27) | Oráculo incorrecto en `tests/test_model_predictive_quality.py`: se exigía `prediccion == etiqueta` en cada registro del conjunto de prueba, lo que es imposible para un modelo estadístico (~35% de filas fallan por diseño). Las pruebas de métricas globales solo imprimían valores sin compararlos con un umbral, por lo que no detectaban una degradación real. Provocó la falla de CI en `main` (run 45119527362) y bloqueó el despliegue. | Alta | Alta | Batería automatizada (pruebas de ML) | Corrección de esta entrega | **Retest:** las pruebas por registro validan contrato de salida (HTTP 200, clase en dominio, probabilidad en $[0,1]$) y las globales exigen los umbrales de `CP-29`: `1053 passed, 20 skipped`.<br>**Regresión:** `1072 passed, 35 skipped` en la batería principal y `15 passed` en E2E. | Corregido (pendiente de confirmación en CI) |

---

## 6. Matriz de Trazabilidad

La siguiente matriz vincula cada requisito funcional (`F1`–`F14`) y no funcional (`RNF`) con su nivel de riesgo, los casos de prueba diseñados, la técnica aplicada, la prueba automatizada o manual ejecutada, el resultado obtenido, los defectos asociados y la decisión de calidad:

| Requisito / Funcionalidad | Riesgo | Caso de prueba | Técnica de diseño | Automatización / Evidencia | Resultado | Defecto asociado | Decisión |
|---|---|---|---|---|---|---|---|
| **F1:** Selección de modelo y despliegue de formulario (UI) | Bajo | `CP-01`, `CP-02` | Partición de equivalencia | `test_ui_views.py::test_cp01_despliegue_formulario_m01`, `test_cp02_despliegue_formulario_m02`, `test_despliegue_formulario_m03` | **Pass** | — | Aceptado |
| **F2:** Validación preventiva de entradas en la UI | Medio | `CP-03`, `CP-04`, `CP-05`, `CP-06`, `CP-07` | Partición de equivalencia / Valores límite E2E: `test_campos_obligatorios_marcan_error_y_bloquean_el_envio`, `test_valor_fuera_de_rango_muestra_el_limite`, `test_error_desaparece_al_corregir_el_campo` + límites en API (`test_bva_m02_edad_limites_exactos`, `test_cp06_cp07_bva_m02_edad_fuera_de_limites`) | **Pass** | — | Aceptado |
| **F3:** Presentación de resultado y de errores en la UI | Medio | `CP-08`, `CP-09` | Basada en riesgo E2E: `test_flujo_completo_m01/m02/m03`, `test_muestra_los_errores_de_validacion_de_la_api`, `test_muestra_un_error_interno_del_servidor`, `test_avisa_cuando_no_hay_conexion_con_la_api` + `test_cp08`, `test_cp09` | **Pass** | `DEF-001` (Corregido) | Aceptado |
| **F4:** Validación de contrato de entrada por modelo (API) | Alto | `CP-10`, `CP-11`, `CP-12` | Partición de equivalencia | `test_api_m02.py` (`test_cp09` a `test_cp13`), `test_api_m01.py`, `test_api_m03.py` | **Pass** | `DEF-001` (Corregido) | Aceptado |
| **F5:** Enrutamiento e invocación del modelo correcto (API) | Alto | `CP-13`, `CP-14` | Basada en riesgo / Partición de equivalencia | `test_integration.py::test_integracion_api_a_modelo`, `test_security_routes.py::test_cp14_ruta_o_modelo_inexistente_retorna_404` | **Pass** | `DEF-002` (Corregido) | Aceptado |
| **F6:** Estructura de respuesta común y códigos HTTP (API) | Alto | `CP-15` | Basada en riesgo | `test_cp08_predict_m02_exitoso_contrato_completo`, `test_cp18_predict_m01_exitoso_caso_aprobacion`, `test_cp22_predict_m03_exitoso_contrato_completo`, `test_cp15_metodo_no_permitido_retorna_405` | **Pass** | `DEF-001`, `DEF-002` (Corregidos) | Aceptado |
| **F7:** Seguridad básica de rutas y no exposición de trazas (API) | Alto | `CP-16`, `CP-17` | Basada en riesgo | `test_security_routes.py::test_cp16_entrada_maliciosa_rechazada_sin_efectos_en_bd` (3 variantes), `test_cp17_no_divulgacion_de_informacion_en_error_500` | **Pass** | — | Aceptado |
| **F8:** Cálculo de predicción — M01 (Aprobación de curso) | Alto | `CP-18`, `CP-19` | Basada en riesgo | `test_api_m01.py::test_cp18_predict_m01_exitoso_caso_aprobacion`, `test_cp19_predict_m01_caso_bajo_rendimiento` | **Pass** | `DEF-003` (Corregido) | Aceptado |
| **F9:** Cálculo de predicción y redondeo — M02 (Presión arterial) | Alto | `CP-20`, `CP-21` | Basada en riesgo | `test_api_m02.py::test_cp08_predict_m02_exitoso_contrato_completo` (verifica `round(pred, 2)` y `80 <= pred <= 250`) | **Pass** | — | Aceptado |
| **F10:** Cálculo de predicción multiclase — M03 (Riesgo de morosidad) | Alto | `CP-22a`, `CP-22b`, `CP-22c` | Partición de equivalencia | `test_api_m03.py::test_cp22_predict_m03_exitoso_contrato_completo` y `test_cp22a_cp22b_cp22c_tres_clases_alcanzables` | **Pass** | — | Aceptado |
| **F11:** Robustez ante valores extremos o de frontera (Modelos) | Medio | `CP-23`, `CP-24` | Análisis de valores límite | `test_api_m03.py::test_cp23_m03_valor_extremo_ingreso`, `test_api_m02.py::test_cp24_predict_m02_valores_clinicos_extremos` | **Pass** | — | Aceptado |
| **F12:** Almacenamiento de ejecución y resultado en Supabase (BD) | Alto | `CP-25` | Basada en riesgo | `test_integration.py::test_cp25_integracion_api_a_persistencia_supabase` | **Pass** | `DEF-004` (Corregido) | Aceptado |
| **F13:** Verificación de registros históricos almacenados (BD) | Medio | `CP-26` | Basada en riesgo | Verificación en tablas `logs_m01`, `logs_m02` y `logs_m03` en panel de Supabase (lectura restringida al rol `service_role`/consola por política RLS) | **Pass** | — | Aceptado |
| **F14:** Confiabilidad ante base de datos no disponible (*Fail-soft*) | Alto | `CP-27` | Basada en riesgo | `test_integration.py::test_cp27_resiliencia_bd_no_disponible` y `test_persistencia_deshabilitada_fallback_terminal` | **Pass** | `DEF-004` (Corregido) | Aceptado |
| **RNF-01:** Usabilidad de la interfaz para usuario nuevo | Medio | `CP-28` | Basada en riesgo | Prueba manual de flujo completo en `/m01`, `/m02` y `/m03` + E2E móvil (`test_pestanas_agrupan_las_secciones`, `test_resultado_en_pantalla_aparte_y_recalculo`, `test_el_resumen_refleja_los_datos_ingresados`) | **Pass** | — | Aceptado |
| **RNF-02:** Mantenibilidad y calidad estática del código | Medio | Análisis estático | Revisión estática | `uv run pylint src` en local y en GitHub Actions (`10.00/10`) | **Pass** | `DEF-005` (Corregido) | Aceptado |
| **RNF-03:** Respuesta oportuna de la API | Medio | `CP-30` | Basada en riesgo | `test_rendimiento.py::test_cp30_tiempo_de_respuesta[m01/m02/m03]` (p95 `< 500 ms`) | **Pass** | — | Aceptado |
| **RNF-04:** Calidad predictiva mínima de los modelos ML | Alto | `CP-29` | Basada en riesgo / Partición de equivalencia (clases de salida) | `test_model_predictive_quality.py::test_m01/m02/m03_metricas_globales` contra umbrales | **Pass** | `DEF-006` (Corregido) | Aceptado con limitación (ver riesgo residual 4) |

---

## 7. Métricas Consolidadas

### 7.1. Métricas de ejecución y cobertura de pruebas

| Indicador | Valor | Observación |
|---|---|---|
| **Casos del Diseño de Pruebas planificados y diseñados** | 32 casos (`CP-01` a `CP-30`, con `CP-22a/b/c`) | 100% diseñados con precondiciones, entrada y oráculo explícito. |
| **Casos ejecutados** | 32 / 32 (**100% de ejecución**) | 30 automatizados (pytest + Playwright); `CP-26` (consulta en panel de Supabase) y `CP-28` (usabilidad con usuario nuevo) con verificación manual, `CP-28` complementado con E2E. |
| **Casos aprobados (Pass) / Fallidos (Fail) / Bloqueados** | **32 Aprobados (100%)** / 0 Fallidos / 0 Bloqueados | Tras la corrección y *retest* de `DEF-001` a `DEF-006`. |
| **Pruebas automatizadas** | **1,087 ejecutadas**: 39 funcionales/integración/no funcionales + 1,033 de calidad predictiva (20 omitidas por nulos) + 15 E2E | Cubren las 4 capas de la arquitectura (UI, API, Modelos ML y Persistencia). |
| **Cobertura de requisitos (`F1`–`F14`, `RNF-01`–`RNF-04`)** | **18 / 18 (100%)** | Todos los requisitos cuentan con al menos un caso verificado. |
| **Cobertura de código fuente (`pytest-cov` sobre `src/`)** | **91% global** (442 / 485 sentencias) | 100% en controladores (`api_m01`, `api_m02`, `api_m03`, `pages`), 98–99% en `m01`, `m02` y `m03`, 96% en `middleware_logs` y 95% en `logs_supabase`. |
| **Calificación de análisis estático (`pylint src`)** | **10.00 / 10** | Sin advertencias ni errores de estilo o complejidad. |

### 7.2. Métricas de defectos

| Clasificación | desglose | Total |
|---|---|---|
| **Por severidad** | Crítica: `0` \| Alta: `4` (`DEF-001`, `DEF-003`, `DEF-004`, `DEF-006`) \| Media: `2` (`DEF-002`, `DEF-005`) \| Baja: `0` | 6 defectos registrados |
| **Por prioridad** | Alta: `5` (`DEF-001`, `DEF-003`, `DEF-004`, `DEF-005`, `DEF-006`) \| Media: `1` (`DEF-002`) \| Baja: `0` | 6 defectos registrados |
| **Por componente** | API: `2` \| Modelos ML: `1` \| Persistencia Supabase: `1` \| CI/CD: `1` \| Batería de pruebas ML: `1` | 6 defectos registrados |
| **Por estado final** | Abiertos: `0` \| Cerrados con retest: `5` \| Corregido, pendiente de confirmar en CI: `1` (`DEF-006`) \| Reabiertos: `0` | 0 defectos abiertos |

**Tendencia de defectos por fecha de detección/corrección:**

| Periodo | Detectados | Corregidos | Acumulado abiertos | Defectos |
|---|---|---|---|---|
| 18–19 oct 2026 (integración de M01–M03, persistencia y despliegue) | 5 | 5 | 0 | `DEF-001` a `DEF-005` |
| 20–22 nov 2026 (ampliación de batería E2E y de calidad ML) | 1 | 1 | 0 | `DEF-006` |

La tendencia es decreciente: el grueso de los defectos se concentró en la integración inicial de componentes, y la ampliación posterior de la batería solo reveló un defecto en las propias pruebas, no en el producto.

### 7.3. Métricas de desempeño de los modelos de Machine Learning

Cada modelo fue evaluado sobre su conjunto de prueba independiente (20% de los datos, partición estratificada en clasificación):

| Modelo | Tipo y Algoritmo Seleccionado | Conjunto de Datos (Train / Test) | Métricas en Conjunto de Prueba | Interpretación y Límites del Modelo |
|---|---|---|---|---|
| **M01: Aprobación de curso** | Clasificación binaria (Regresión Logística con preprocesamiento y balanceo) | 395 registros totales (316 train / 79 test), 17 variables | **Accuracy:** `0.6582`<br>**Precision:** `0.3333`<br>**Recall:** `0.6875`<br>**F1-Score:** `0.4490` | Al excluir las notas parciales previas (`G1`, `G2`) para predecir únicamente con variables socioeconómicas y de hábitos al inicio del curso, el poder predictivo es moderado. Se prioriza el *Recall* (68.75%) para identificar posibles aprobaciones/riesgos tempranos. |
| **M02: Presión arterial estimada** | Regresión lineal regularizada (**Ridge Regression** con `StandardScaler` e imputación por mediana) | 4,240 registros del estudio Framingham (3,392 train / 848 test), 13 variables clínicas | **MAE:** `10.8114 mmHg`<br>**RMSE:** `14.3936 mmHg`<br>**R²:** `0.5321` | El modelo explica el 53.21% de la varianza de la presión sistólica con un error medio absoluto de ~10.8 mmHg, consistente con la variabilidad fisiológica clínica sin mediciones invasivas. |
| **M03: Riesgo de morosidad** | Clasificación multiclase (**Regresión Logística Balanceada** con umbrales de probabilidad de rechazo: bajo `< 0.33`, medio `0.33–0.67`, alto `>= 0.67`) | 614 registros (491 train / 123 test), 10 variables financieras (excluida la variable dominante `Credit_History` que acaparaba el 73.7% de la información mutua) | **Accuracy:** `0.6179`<br>**Precision:** `0.4000`<br>**Recall:** `0.4737`<br>**F1-Score:** `0.4337`<br>**Matriz de confusión (0/1):** `[[58, 27], [20, 18]]` | Al retirar `Credit_History` (que monopolizaba más del 53% del peso e ignoraba ingresos y montos), el modelo evalúa genuinamente el perfil socioeconómico y del préstamo. Los tres niveles de riesgo muestran separación monótona en la tasa real de rechazo en prueba: **bajo** (27%), **medio** (31%) y **alto** (40%). |

**Verificación independiente vía API (`CP-29`):** `test_model_predictive_quality.py` reproduce estas métricas enviando cada registro del conjunto de prueba a la API: M01 obtiene Accuracy `0.6582`, Recall `0.6875` y F1 `0.4490`; M02 obtiene MAE `10.81 mmHg`, RMSE `14.39 mmHg` y R² `0.5320`, idénticos a los de entrenamiento. En M03 se evalúan solo los 103 registros completos (la API no acepta nulos, mientras que el entrenamiento imputa), con Accuracy `0.6408`, Recall `0.5000` y F1 `0.4308`.

**Límite de la métrica en M01:** el conjunto de prueba está desbalanceado (16 de 79 registros aprueban). Un clasificador trivial que siempre predijera "No aprueba" tendría Accuracy `0.797`, superior al `0.658` del modelo. Por eso Accuracy no es la métrica adecuada para M01: el modelo se justifica por su Recall (`0.69`), es decir, por identificar 11 de 16 aprobaciones. Precision (`0.33`) indica que dos de cada tres "Aprueba" son falsos positivos.

### 7.3.1. Limpieza de variables dominantes y pesos relativos (`pesos`) en cada modelo

En los tres modelos se realizó un análisis de información mutua y pesos para evitar que variables redundantes o dominantes "se tragaran" la predicción, exponiendo además el diccionario `pesos` tanto en la respuesta JSON de la API como en el panel lateral **"Pesos de las variables (%)"** de la interfaz web:

- **M01 (Aprobación de curso):** Se descartaron las columnas de calificaciones (`G1`, `G2`, `G3`, `Homework`, `Quizzes`, `Test`, `Total`) y las 13 variables con información mutua `0.000`. En las 17 variables seleccionadas los pesos están distribuidos de forma equilibrada: `schoolsup` (15.4%), `Dalc` (12.6%), `higher` (12.6%), `failures` (11.6%), `absences` (9.0%), `Medu` (7.1%), `famsup` (4.8%), `sex` (4.6%) y resto `< 4.1%`.
- **M02 (Presión arterial estimada):** Se descartó `diaBP` (presión diastólica, `MI = 0.5693`, `r = 0.7840`) por ser una medición invasiva simultánea que absorbía el modelo. Entre las 13 variables clínicas y demográficas seleccionadas ($R^2 = 0.5321$), los pesos estandarizados principales son: `prevalentHyp` (48.2%), `age` (14.9%), `BMI` (9.4%), `heartRate` (7.0%), `BPMeds` (6.1%), `glucose` (3.5%), `male` (3.1%), `education` (2.8%) y `totChol` (2.8%).
- **M03 (Riesgo de morosidad):** Se identificó y descartó `Credit_History` (`MI = 0.1462`, 73.7% de toda la información mutua y 53.0% de importancia en árboles), ya que determinaba por sí sola el resultado ignorando los ingresos y el monto del préstamo. Con las 10 variables limpias, los pesos quedan distribuidos en: `Married` (25.8%), `Property_Area` (23.1%), `Education` (20.3%), `LoanAmount` (10.3%), `CoapplicantIncome` (5.8%), `Self_Employed` (5.1%), `Gender` (3.4%), `Loan_Amount_Term` (3.2%), `Dependents` (2.0%) y `ApplicantIncome` (1.0%).

### 7.4. Tiempos de respuesta medidos

**Medición automatizada y repetible (`CP-30`, `tests/test_rendimiento.py`):** 20 solicitudes consecutivas por endpoint tras una solicitud de calentamiento (carga del artefacto `.joblib` en `@lru_cache`), dentro del proceso con `TestClient` y la persistencia simulada. Mide API + validación + modelo, sin red:

| Escenario / Endpoint | Media (ms) | Mediana (ms) | Mínimo (ms) | Máximo (ms) | p95 (ms) | Evaluación (umbral p95 `< 500 ms`) |
|---|---|---|---|---|---|---|
| `POST /predict/m01` (Regresión logística, binaria) | **2.08** | 2.00 | 1.89 | 2.59 | 2.39 | Pass |
| `POST /predict/m02` (Regresión Ridge) | **2.16** | 2.14 | 2.06 | 2.39 | 2.28 | Pass |
| `POST /predict/m03` (Regresión logística, multiclase por umbrales) | **2.50** | 2.43 | 2.30 | 3.13 | 2.79 | Pass |

**Medición de extremo a extremo sobre HTTP** (servidor Uvicorn local, 20 solicitudes por endpoint, Etapa 3), incluye red local, serialización y el registro en segundo plano en Supabase:

| Escenario / Endpoint | Media (ms) | Mediana (ms) | Mínimo (ms) | Máximo (ms) | Evaluación |
|---|---|---|---|---|---|
| `POST /predict/m01` | **22.59 ms** | 22.37 ms | 17.65 ms | 28.76 ms | Óptimo (`< 100 ms`) |
| `POST /predict/m02` | **25.33 ms** | 24.97 ms | 21.56 ms | 31.24 ms | Óptimo (`< 100 ms`) |
| `POST /predict/m03` | **60.54 ms** | 62.81 ms | 43.27 ms | 80.09 ms | Óptimo (`< 100 ms`) |

La diferencia entre ambas tablas (~2 ms frente a 22–60 ms) corresponde al costo de red y de transporte HTTP, no a la inferencia. Las pruebas de carga concurrente quedan fuera de alcance (ver plan de pruebas).

---

## 8. Riesgos Residuales y Limitaciones Conocidas

1. **Riesgo residual en la precisión predictiva de M01 (Riesgo Medio):** Dado que el modelo M01 utiliza exclusivamente variables demográficas y de hábitos escolares (sin notas previas de exámenes), su exactitud es del 65.8%. *Mitigación:* La respuesta de la API incluye explícitamente el objeto `metrica` y la `probabilidad` en cada predicción para que el usuario final interprete el resultado como una estimación orientativa y no determinista.
2. **Almacenamiento asíncrono *fail-soft* ante caídas prolongadas de Supabase (Riesgo Bajo):** Si Supabase experimenta una caída o falta de credenciales, el sistema garantiza la continuidad del servicio de predicción (`CP-27`) volcando el registro en la salida estándar del contenedor, pero dichos registros no se reenvían automáticamente a la nube cuando Supabase se recupera. *Mitigación:* El contenedor en Coolify conserva los logs de salida estándar para auditoría.
3. **Política RLS de solo inserción para la clave `anon` (Condición de diseño):** Por seguridad, la clave pública `anon` solo tiene permiso `INSERT` en `logs_m01`, `logs_m02` y `logs_m03`. La auditoría y consulta de registros históricos se realiza directamente desde el panel administrativo de Supabase o con credenciales de servicio, evitando exponer datos de otros usuarios en una aplicación sin autenticación.
4. **Calidad predictiva limitada y desbalance de clases (Riesgo Medio):** M01 tiene Precision de `0.33` y una Accuracy inferior a la de la clase mayoritaria (`0.658` frente a `0.797`). M03 tiene Recall de `0.47–0.50` sobre rechazos. Los umbrales de `CP-29` detectan degradaciones respecto a esta línea base, pero no la vuelven aceptable para decisiones automáticas. *Mitigación:* la UI y la API presentan la probabilidad, la métrica y los pesos, y el sistema se libera como herramienta orientativa, no como decisor.
5. **Desalineación de rutas de los datos de prueba exportados (Riesgo Bajo):** `training/data_utils.py` exporta a `training/data/clean/<modelo>/test_data.csv`, mientras que la prueba `CP-29` y `training/readme.md` leen `training/data/clean/<modelo>/1_curso/test_data.csv`. Además, el CSV de M02 regenerado por `train_m02.py` conserva valores nulos, mientras que la versión versionada en `1_curso/` contiene valores imputados. *Mitigación:* la prueba usa los CSV versionados, que reproducen exactamente las métricas reportadas. Se recomienda unificar la ruta antes de un nuevo reentrenamiento.

---

## 9. Decisión de Liberación (Go / No-Go)

### Recomendación Formal: **GO (LIBERAR)**

Con base en la evidencia objetiva recopilada durante el proceso de pruebas, el equipo recomienda dar **GO (Aprobar la liberación)** de la versión `0.1.0` del sistema bajo prueba, sustentado en los siguientes criterios de salida cumplidos:

1. **Cumplimiento del 100% de ejecución y aprobación:** Los 32 casos del diseño de pruebas y las **1,087 pruebas automatizadas** (39 funcionales/integración/no funcionales, 1,033 de calidad predictiva y 15 E2E) se ejecutaron con un **100% de aprobación (0 fallos, 0 bloqueos)**. Las 20 omisiones son registros de M03 con nulos que la API rechaza por contrato.
2. **Cero defectos críticos o altos abiertos:** Los 6 defectos detectados (`DEF-001` a `DEF-006`) fueron corregidos y sometidos a *retest* y regresión automatizada. `DEF-006` era un defecto de la batería de pruebas, no del producto.
3. **Alta cobertura y calidad técnica:** Se alcanzó un **91% de cobertura de código** en `src/proyecto_pruebas`, **100% de cobertura de requisitos (18/18)** y una calificación de **10.00 / 10 en análisis estático con Pylint**.
4. **Resiliencia y seguridad verificadas:** El sistema valida estrictamente los contratos de entrada (`HTTP 400`), no filtra información sensible ni *stack traces* ante fallos internos (`HTTP 500`, `CP-17`), protege las tablas en Supabase mediante políticas RLS y mantiene su disponibilidad incluso si la base de datos externa falla (`CP-27`).
5. **Desempeño dentro de parámetros esperados:** El p95 automatizado es menor que **3 ms** por endpoint en proceso y la media de extremo a extremo sobre HTTP se sitúa entre **22.6 ms y 60.5 ms**, muy por debajo del umbral de `500 ms`.

**Condiciones de la liberación:** (a) confirmar en GitHub Actions que la corrección de `DEF-006` deja `main` en verde antes de desplegar; (b) presentar las predicciones como orientativas, por la calidad predictiva limitada de M01 y M03 (riesgo residual 4); (c) unificar la ruta de exportación de los datos de prueba antes del próximo reentrenamiento (riesgo residual 5).

---

## 10. Lista de Verificación de Entrega y Conclusiones

### 10.1. Lista de verificación oficial

- [x] El repositorio incluye instrucciones claras en `README.md`, archivo `.env.example` y no expone secretos.
- [x] El contrato del API define solicitudes, respuestas JSON, validaciones y códigos HTTP (`docs/contrato_api_m01.md`, `m02.md`, `m03.md`).
- [x] Existe trazabilidad completa desde cada requisito relevante hasta su resultado y defecto (Sección 6).
- [x] Se aplicaron y justificaron tres técnicas de diseño: Partición de Equivalencia, Análisis de Valores Límite y Pruebas Basadas en Riesgo.
- [x] Se documentaron y ejecutaron pruebas positivas, negativas, de integración y no funcionales (usabilidad, rendimiento, confiabilidad y seguridad).
- [x] La automatización con `pytest` y Playwright supera el mínimo exigido (4 capas, 91% de cobertura), es repetible y se ejecuta en CI (GitHub Actions) con evidencia de ejecuciones exitosas y fallidas (sección 4.3).
- [x] Los defectos corregidos (`DEF-001` a `DEF-006`) cuentan con *retest* y regresión documentada.
- [x] Las métricas son coherentes con los resultados y la decisión **Go** está sustentada técnicamente.

### 10.2. Conclusiones

1. La implementación de un contrato estricto en la capa de API (Pydantic con `strict=True` y `extra="forbid"`, complementado con manejadores personalizados de excepciones) permitió detectar y contener errores de validación de forma temprana, garantizando respuestas consistentes entre los tres modelos de distinta naturaleza (clasificación binaria, regresión y clasificación multiclase).
2. La automatización de pruebas con `pytest` y su integración en el flujo de GitHub Actions demostraron ser fundamentales para prevenir regresiones al integrar los modelos M01, M02 y M03 y la capa de persistencia en Supabase. La falla de CI por `DEF-006` mostró que el pipeline bloquea el despliegue ante una batería roja.
4. Probar un componente de ML exige un oráculo estadístico: no se puede afirmar que cada predicción individual sea "correcta". El oráculo adecuado combina la validación del contrato de salida por registro con umbrales sobre métricas agregadas. Esas métricas deben interpretarse frente a una línea base, como lo muestra el caso de M01 frente a la clase mayoritaria.
3. El diseño *fail-soft* validado mediante el caso `CP-27` comprobó la importancia de las pruebas no funcionales de confiabilidad: desacoplar la disponibilidad de un servicio externo de auditoría (Supabase) del flujo crítico de negocio evita que fallos de terceros degraden la experiencia del usuario final.
