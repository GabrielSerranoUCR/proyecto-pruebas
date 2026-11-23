# Evidencias de ejecución — Etapa 3

Ejecución local del 23 de noviembre de 2026 (macOS, Python 3.13, Chromium de Playwright), con los artefactos `.joblib` regenerados con los scripts de entrenamiento. Las mismas pruebas se ejecutan en cada cambio en GitHub Actions (`.github/workflows/ci.yml`).

| Archivo | Contenido | Resultado |
|---|---|---|
| [`pytest_bateria_principal.txt`](pytest_bateria_principal.txt) | Salida completa de `uv run pytest -v -rs --cov=src/proyecto_pruebas --cov-report=term-missing`: contrato API, seguridad, UI, integración, calidad predictiva ML y rendimiento, con tabla de cobertura. | `1072 passed, 35 skipped`, cobertura 91% |
| [`pytest_e2e.txt`](pytest_e2e.txt) | Salida de `uv run pytest --e2e tests/e2e -v --screenshot=on`. | `15 passed` |
| [`reporte-e2e.html`](reporte-e2e.html) | Reporte HTML autocontenido de la suite E2E (descargar y abrir en el navegador). | 15/15 |
| [`capturas_e2e/`](capturas_e2e/) | Captura final de cada prueba E2E. | 15 capturas |
| [`lint.txt`](lint.txt) | Pylint (`src`, `tests`, `training`), hadolint (`Dockerfile`) y actionlint (workflows). | 10.00/10 en los tres alcances; sin hallazgos |

Las 35 pruebas omitidas son las 15 E2E (solo corren con `--e2e`, ver `pytest_e2e.txt`) y 20 registros de M03 con valores nulos que la API rechaza por contrato.

## Capturas E2E por caso de prueba

| Caso | Prueba | Captura |
|---|---|---|
| CP-01 / F1 | Inicio lista los tres modelos y abre M01 | [`navegacion__inicio-lista-los-tres-modelos.png`](capturas_e2e/navegacion__inicio-lista-los-tres-modelos.png), [`navegacion__desde-inicio-se-abre-el-formulario-m01.png`](capturas_e2e/navegacion__desde-inicio-se-abre-el-formulario-m01.png), [`navegacion__volver-al-inicio-desde-un-formulario.png`](capturas_e2e/navegacion__volver-al-inicio-desde-un-formulario.png) |
| CP-03 / CP-08 | Flujo completo con resultado en pantalla (M01, M02, M03) | [`formularios__flujo-completo-m01.png`](capturas_e2e/formularios__flujo-completo-m01.png), [`formularios__flujo-completo-m02.png`](capturas_e2e/formularios__flujo-completo-m02.png), [`formularios__flujo-completo-m03.png`](capturas_e2e/formularios__flujo-completo-m03.png) |
| CP-04 / CP-05 | Campos obligatorios marcan error y bloquean el envío | [`formularios__campos-obligatorios-marcan-error-y-bloquean-el-envio.png`](capturas_e2e/formularios__campos-obligatorios-marcan-error-y-bloquean-el-envio.png) |
| CP-06 / CP-07 | Valor fuera de rango muestra el límite; el error desaparece al corregir | [`formularios__valor-fuera-de-rango-muestra-el-limite.png`](capturas_e2e/formularios__valor-fuera-de-rango-muestra-el-limite.png), [`formularios__error-desaparece-al-corregir-el-campo.png`](capturas_e2e/formularios__error-desaparece-al-corregir-el-campo.png) |
| CP-09 | Errores 400 y 500 de la API y API sin conexión | [`errores-ui__muestra-los-errores-de-validacion-de-la-api.png`](capturas_e2e/errores-ui__muestra-los-errores-de-validacion-de-la-api.png), [`errores-ui__muestra-un-error-interno-del-servidor.png`](capturas_e2e/errores-ui__muestra-un-error-interno-del-servidor.png), [`errores-ui__avisa-cuando-no-hay-conexion-con-la-api.png`](capturas_e2e/errores-ui__avisa-cuando-no-hay-conexion-con-la-api.png) |
| CP-28 (apoyo) | Interfaz móvil: pestañas, resultado en pantalla aparte, resumen | [`movil__pestanas-agrupan-las-secciones.png`](capturas_e2e/movil__pestanas-agrupan-las-secciones.png), [`movil__resultado-en-pantalla-aparte-y-recalculo.png`](capturas_e2e/movil__resultado-en-pantalla-aparte-y-recalculo.png), [`movil__el-resumen-refleja-los-datos-ingresados.png`](capturas_e2e/movil__el-resumen-refleja-los-datos-ingresados.png) |

## Pendiente de evidencia manual

- **CP-26 (consulta de registros en Supabase):** captura del panel de Supabase con filas recientes de `logs_m01`, `logs_m02` y `logs_m03`.
- **CP-28 (usabilidad con usuario nuevo):** registro de la sesión (participante, tarea, tiempo, ayudas requeridas, observaciones).
