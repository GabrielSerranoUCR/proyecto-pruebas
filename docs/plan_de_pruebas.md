# Plan de Pruebas

## 1. Alcance

**Qué se probará.** La solución mínima construida por el equipo, que integra los tres
modelos asignados:

- **M07 — Riesgo de diabetes** (Salud, clasificación binaria)
- **M08 — Monto de préstamo** (Finanzas, regresión)
- **M09 — Riesgo académico** (Educación, clasificación multiclase)

expuestos mediante una API que valida el contrato y orquesta la
predicción, una interfaz de usuario que captura los parámetros y
presenta el resultado, y persistencia de solicitudes/resultados en
Supabase/PostgreSQL.

### Funcionalidades objeto de prueba
- Captura y validación de parámetros de entrada por modelo.
- Invocación del modelo correspondiente según la ruta/endpoint solicitado.
- Cálculo y devolución de la predicción en el formato acordado.
- Almacenamiento de la ejecución y su resultado en la base de datos.
- Consulta del historial de ejecuciones almacenado.

### Fuera de alcance
- Pruebas de carga o rendimiento bajo volumen alto de solicitudes.
- Autenticación y autorización de usuarios.
- Despliegue en un ambiente de producción.
- Automatización de pruebas de UI end-to-end (por ahora se contemplan
  pruebas manuales de usabilidad).

### Limitaciones conocidas
- El desarrollo se encuentra en fase inicial: solo el esqueleto del
  repositorio y el ambiente están configurados. La API, el UI y los tres
  modelos aún no están implementados, por lo que este diseño es preliminar y
  se refinará en las siguientes etapas.

## 2. Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Supabase no disponible o mal configurado | Media | Alto | Verificar la conexión al inicio de cada sesión de trabajo; documentar el procedimiento de configuración |
| Cambios en el contrato de la API durante el desarrollo | Alta | Alto | Mantener el contrato documentado y bajo control de versiones; automatizar pruebas de contrato |
| Inconsistencia entre los tres tipos de modelo (binario, regresión, multiclase) en la respuesta de la API | Media | Medio | Definir un contrato de respuesta común y validar cada tipo por separado |
| Disponibilidad desigual de los integrantes del equipo | Media | Medio | Repartir tareas pequeñas y verificables (roles pendientes de asignar) |
| Tiempo insuficiente antes de la entrega final (20 de noviembre) | Media | Alto | Priorizar la automatización mínima exigida y avanzar de forma incremental por etapa |

## 3. Estrategia

La estrategia recorre los niveles de la **pirámide de pruebas**:
unitarias → integración → funcionales/sistema → aceptación, combinando
**Verificación** (revisiones, análisis estático, pruebas unitarias) y
**Validación** (pruebas funcionales y de aceptación) en cada fase.

Se aplicarán pruebas funcionales positivas y negativas en partes iguales,
siguiendo la **regla del 50/50**: la mitad de los casos valida que
el sistema haga lo que debe, la otra mitad que no haga lo que no debe. Se
complementan con pruebas de integración (UI→API, API→modelo, API→Supabase y
el flujo completo) y no funcionales básicas (usabilidad, confiabilidad,
seguridad).

El laboratorio de ML visto en clase añade dos categorías propias de
sistemas de ML: **pruebas de validez de datos** (que la entrada cumpla
formato, tipo y rango esperado, tanto antes del preprocesamiento como en
el contrato de la API) y **pruebas de calidad del modelo** (que las
métricas de cada modelo, sección 7, no se degraden por debajo de un
umbral mínimo aceptable).

Manuales y automatizadas se complementan, no compiten. Se
automatizarán con pytest las pruebas unitarias de cada modelo, las pruebas
de contrato de la API (positivas y negativas), la integración API→modelo,
la persistencia API→Supabase y al menos un caso de borde, cumpliendo el
mínimo de automatización exigido por el proyecto. Se ejecutarán de forma
manual las pruebas de usabilidad de la interfaz, la exploración del flujo
completo UI→API→modelo→Supabase y las pruebas no funcionales de
confiabilidad ante indisponibilidad y seguridad básica.

Como **prueba estática** se incluye análisis estático automatizado
(Pylint sobre `src/`). Cada caso de prueba del Diseño de Pruebas deberá declarar un **oráculo
explícito**, sin el cual no se puede concluir si la prueba pasó o falló.

### Técnicas de diseño aplicadas

1. **Partición de equivalencia**: agrupa valores válidos e inválidos de
   los parámetros de entrada de cada modelo (ej. edad, ingresos, notas).
2. **Análisis de valores límite**: prueba los límites de rangos numéricos
   relevantes (edad mínima/máxima, montos de préstamo, notas límite del
   riesgo académico).
3. **Pruebas basadas en riesgo**: prioriza, entre los tres modelos, los
   flujos con mayor probabilidad o impacto de fallo.