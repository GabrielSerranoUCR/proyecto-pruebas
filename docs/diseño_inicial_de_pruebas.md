## Diseño inicial de Pruebas

El diseño inicial de pruebas se construye a partir de las funcionalidades identificadas en el Plan de Pruebas y busca establecer casos concretos, datos, técnicas y criterios de cobertura que puedan utilizarse posteriormente durante la implementación y ejecución.

### 8.1. Funcionalidades seleccionadas

| Código | Funcionalidad |
|---|---|
| F1 | Selección de modelo y despliegue de formulario (UI) |
| F2 | Validación de entradas en la UI |
| F3 | Presentación de resultado y de errores (UI) |
| F4 | Validación de contrato de entrada por modelo (API) |
| F5 | Enrutamiento e invocación del modelo correcto (API) |
| F6 | Estructura de respuesta y códigos HTTP (API) |
| F7 | Seguridad básica de rutas (API) |
| F8 | Cálculo de predicción — M07 (diabetes) |
| F9 | Cálculo de predicción — M08 (monto de préstamo), incluye redondeo |
| F10 | Cálculo de predicción — M09 (riesgo académico) |
| F11 | Manejo de valores extremos/inesperados (modelos) |
| F12 | Almacenamiento de ejecución/resultado (BD) |
| F13 | Consulta de historial de ejecuciones (BD) |
| F14 | Comportamiento ante BD no disponible |

### 8.2. Casos de prueba

Los parámetros de entrada considerados para cada modelo son los siguientes:

- **M07 (diabetes, binario):** embarazos, glucosa, presión arterial, grosor de piel, insulina, IMC, antecedente familiar (índice) y edad. La salida esperada corresponde a una clasificación 0/1 y una probabilidad.
- **M08 (préstamo, regresión):** ingreso mensual, puntaje de crédito, años de empleo, deuda existente y plazo solicitado (meses). La salida corresponde a un monto en colones/dólares, redondeado a 2 decimales.
- **M09 (riesgo académico, multiclase):** promedio general, porcentaje de asistencia, ausencias, horas de estudio semanales y materias reprobadas previas. La salida corresponde a una de las clases: bajo, medio o alto.

Para M07 se establece como regla de validación que la edad debe ser un entero entre 1 y 120, ambos inclusive. Los valores fuera de ese rango deben ser rechazados por la interfaz.

| ID | Funcionalidad | Descripción | Precondiciones | Datos de entrada | Procedimiento | Resultado esperado | Técnica | Tipo | Prioridad |
|---|---|---|---|---|---|---|---|---|---|
| CP-01 | F1 | Seleccionar M07 y ver el formulario correcto | UI cargada | N/A | 1. Abrir la página principal. 2. Clic en “Riesgo de diabetes”. | Se muestran los campos propios de M07 y no los de M08/M09. | Partición de equivalencia | Funcional | Alta |
| CP-02 | F1 | Seleccionar M08 y ver el formulario correcto | UI cargada | N/A | 1. Abrir la página principal. 2. Clic en “Monto de préstamo”. | Se muestran los campos propios de M08. | Partición de equivalencia | Funcional | Alta |
| CP-03 | F2 | Validación UI: edad dentro del rango válido | Formulario M07 abierto | edad = 35 | 1. Completar edad = 35 y el resto de campos con valores válidos. 2. Enviar. | El formulario permite el envío y no muestra mensaje de error. | Partición de equivalencia | Funcional | Alta |
| CP-04 | F2 | Validación UI: edad negativa | Formulario M07 abierto | edad = -5 | 1. Completar edad = -5. 2. Intentar enviar. | La UI bloquea el envío y muestra un mensaje de error, sin llamar a la API. | Partición de equivalencia | Negativa | Alta |
| CP-05 | F2 | Validación UI: campo obligatorio vacío | Formulario M08 abierto | ingreso mensual = vacío | 1. Dejar “ingreso mensual” vacío. 2. Completar el resto. 3. Intentar enviar. | La UI bloquea el envío y resalta el campo faltante. | Partición de equivalencia | Negativa | Alta |
| CP-06 | F2 | Validación UI: edad justo debajo del límite inferior permitido | Formulario M07 abierto | edad = 0 | 1. Completar edad = 0. 2. Intentar enviar. | La UI bloquea el envío y muestra un mensaje de error, sin llamar a la API. | Análisis de valores límite | Negativa | Media |
| CP-07 | F2 | Validación UI: edad en el límite superior permitido | Formulario M07 abierto | edad = 120 | 1. Completar edad = 120. 2. Enviar. | La UI permite el envío y no muestra mensaje de error. | Análisis de valores límite | Funcional | Media |
| CP-08 | F3 | Presentación de resultado exitoso | Formulario M07 válido completo | Payload válido de M07 | 1. Completar el formulario de M07. 2. Enviar. 3. Esperar respuesta 200 de la API. | La UI muestra modelo, predicción, métrica y marca de tiempo. | Basada en riesgo | Funcional | Alta |
| CP-09 | F3 | Presentación de error devuelto por la API | Se puede forzar una respuesta 400 | Entrada que la API rechaza | 1. Enviar una solicitud que produzca 400. 2. Observar la UI. | La UI muestra un mensaje de error comprensible y permanece operativa. | Basada en riesgo | Negativa | Alta |
| CP-10 | F4 | Contrato API válido — M07 | Endpoint /predict/m07 disponible | JSON con los 8 campos de M07 y tipos correctos | 1. Enviar POST a /predict/m07 con el payload completo. | 200 OK y estructura de respuesta según el contrato. | Partición de equivalencia | Funcional | Alta |
| CP-11 | F4 | Contrato API inválido — campo faltante | Endpoint /predict/m07 disponible | JSON sin el campo “glucosa” | 1. Enviar POST a /predict/m07 sin ese campo. | 400 Bad Request con detalle del campo faltante. | Partición de equivalencia | Negativa | Alta |
| CP-12 | F4 | Contrato API inválido — tipo de dato incorrecto | Endpoint /predict/m08 disponible | ingreso_mensual = “abc” | 1. Enviar POST a /predict/m08 con ese valor. | 400 Bad Request. | Partición de equivalencia | Negativa | Alta |
| CP-13 | F5 | Enrutamiento correcto por endpoint | API activa | Payload válido de M09 | 1. Enviar POST a /predict/m09. 2. Verificar mediante respuesta o logs el modelo invocado. | Se invoca el modelo M09 y no M07 ni M08. | Basada en riesgo | Funcional | Alta |
| CP-14 | F5 | Endpoint inexistente | API activa | N/A | 1. Enviar POST a /predict/m99. | 404 Not Found. | Partición de equivalencia | Negativa | Media |
| CP-15 | F6 | Estructura de respuesta completa | Solicitud válida | Payload válido de M07 | 1. Enviar solicitud válida. 2. Inspeccionar el JSON de respuesta. | La respuesta contiene fecha, hora, modelo, predicción, métrica e id_ejecucion. | Basada en riesgo | Funcional | Alta |
| CP-16 | F7 | Seguridad: entrada maliciosa en campo numérico | API activa | edad = “35; DROP TABLE usuarios;” | 1. Enviar el payload. 2. Verificar la respuesta y el estado de la BD. | 400 Bad Request y ningún cambio no autorizado en la base de datos. | Basada en riesgo | Negativa (seguridad) | Alta |
| CP-17 | F7 | Seguridad: no exposición de información sensible en error | API activa | Entrada que provoque un error interno | 1. Provocar el error. 2. Inspeccionar el cuerpo de la respuesta. | El error no revela stack trace, rutas internas del servidor ni credenciales. | Basada en riesgo | Negativa (seguridad) | Alta |
| CP-18 | F8 | Predicción M07 con caso positivo conocido | Modelo M07 cargado | Valores de entrada de un caso de alto riesgo | 1. Invocar el modelo con los valores definidos. | Predicción = 1 y probabilidad dentro del rango esperado. | Basada en riesgo | Funcional | Alta |
| CP-19 | F8 | Predicción M07 con caso negativo conocido | Modelo M07 cargado | Valores de entrada de un caso de bajo riesgo | 1. Invocar el modelo con los valores definidos. | Predicción = 0. | Basada en riesgo | Funcional | Alta |
| CP-20 | F9 | Predicción M08 — redondeo correcto | Modelo M08 cargado | Entrada que produzca un monto con más de 2 decimales | 1. Invocar el modelo. 2. Inspeccionar el monto devuelto. | El monto se devuelve redondeado a exactamente 2 decimales. | Basada en riesgo | Funcional | Alta |
| CP-21 | F9 | Predicción M08 — monto no negativo | Modelo M08 cargado | Entrada válida | 1. Invocar el modelo. | El monto devuelto es mayor o igual que 0. | Basada en riesgo | Funcional | Media |
| CP-22a | F10 | Predicción M09 — clase “bajo” alcanzable | Modelo M09 cargado | Entrada representativa de riesgo bajo | 1. Invocar el modelo con el conjunto definido. | Devuelve la clase “bajo”. | Partición de equivalencia | Funcional | Alta |
| CP-22b | F10 | Predicción M09 — clase “medio” alcanzable | Modelo M09 cargado | Entrada representativa de riesgo medio | 1. Invocar el modelo con el conjunto definido. | Devuelve la clase “medio”. | Partición de equivalencia | Funcional | Alta |
| CP-22c | F10 | Predicción M09 — clase “alto” alcanzable | Modelo M09 cargado | Entrada representativa de riesgo alto | 1. Invocar el modelo con el conjunto definido. | Devuelve la clase “alto”. | Partición de equivalencia | Funcional | Alta |
| CP-23 | F11 | Valor extremo — ingreso mensual muy alto | Modelo M08 cargado | ingreso_mensual = 999,999,999 | 1. Invocar el modelo con el valor. | Respuesta 200 con una predicción numérica; no se produce error 500 por el valor extremo. | Análisis de valores límite | Robustez | Media |
| CP-24 | F11 | Valor extremo — todos los campos en 0 | Modelo M07 cargado | Todos los parámetros numéricos = 0 | 1. Invocar el modelo con esos valores. | El sistema procesa la entrada sin provocar un error 500. | Análisis de valores límite | Robustez | Media |
| CP-25 | F12 | Almacenamiento de ejecución exitosa | Supabase disponible | Predicción válida | 1. Ejecutar una predicción válida. 2. Consultar la tabla correspondiente en Supabase. | El registro aparece en la tabla con los campos esperados. | Basada en riesgo | Funcional | Alta |
| CP-26 | F13 | Consulta del historial | Existen registros previos | N/A | 1. Solicitar el historial de ejecuciones. | Se listan las ejecuciones almacenadas en el orden definido por el sistema. | Basada en riesgo | Funcional | Media |
| CP-27 | F14 | Comportamiento con BD no disponible | Supabase desconectada intencionalmente | Solicitud de predicción válida | 1. Simular la indisponibilidad de Supabase. 2. Enviar una solicitud válida. 3. Observar respuesta y logs. | El comportamiento de la predicción y del guardado se maneja de acuerdo con la estrategia definida, sin caída no controlada del sistema. | Basada en riesgo | Negativa (confiabilidad) | Alta |
| CP-28 | Usabilidad | Formulario claro para usuario nuevo | UI cargada | N/A | 1. Solicitar a un usuario sin instrucciones previas que complete el flujo de M07. 2. Observar el proceso. | El usuario logra completar y enviar una solicitud válida sin ayuda externa. | Basada en riesgo | No funcional (usabilidad) | Media |

### 8.3. Datos de prueba

Para cada modelo se diseñarán datos siguiendo estas categorías:

- **Válidos y representativos:** valores típicos dentro del dominio.
- **Inválidos:** tipos incorrectos, campos vacíos o faltantes y caracteres no numéricos en campos numéricos.
- **Valores límite:** extremos exactos de los rangos permitidos y valores inmediatamente fuera de dichos rangos cuando corresponda.
- **Valores extremos:** valores técnicamente procesables pero poco habituales, utilizados para evaluar robustez.
- **Combinaciones relevantes:** conjuntos de entradas que permitan verificar comportamientos importantes de cada modelo, incluyendo las tres clases de salida de M09.

La selección de los datos se justifica mediante las técnicas de diseño aplicadas, priorizando los campos de mayor impacto en el resultado y evitando duplicar casos cuando una misma partición ya esté cubierta.

### 8.4. Técnicas utilizadas

1. **Partición de equivalencia.** Se utiliza para agrupar valores de entrada que deberían producir un comportamiento equivalente. Se aplica a valores válidos e inválidos, tipos de datos, presencia de campos y categorías de salida. Produce, entre otros, CP-01, CP-02, CP-03, CP-04, CP-05, CP-10, CP-11, CP-12, CP-14 y CP-22a/22b/22c.

2. **Análisis de valores límite.** Se utiliza para detectar errores asociados con límites de rangos y condiciones de frontera. Se aplica especialmente a edad y a valores extremos de entrada. Produce CP-06, CP-07, CP-23 y CP-24.

3. **Pruebas basadas en riesgo.** Se utilizan para priorizar funcionalidades cuyo fallo tendría un impacto relevante en la solución. Se aplican a contrato de API, seguridad, cálculo de los tres modelos, persistencia, historial y comportamiento ante indisponibilidad de la base de datos. Produce CP-08, CP-09, CP-13, CP-15 a CP-21 y CP-25 a CP-28.

### 8.5. Cobertura funcional

| Funcionalidad | Casos que la cubren | Estado |
|---|---|---|
| F1 — Selección de modelo | CP-01, CP-02 | Cubierta |
| F2 — Validación UI | CP-03, CP-04, CP-05, CP-06, CP-07 | Cubierta |
| F3 — Presentación de resultado/error | CP-08, CP-09 | Cubierta |
| F4 — Contrato de entrada API | CP-10, CP-11, CP-12 | Cubierta |
| F5 — Enrutamiento/invocación | CP-13, CP-14 | Cubierta |
| F6 — Estructura de respuesta | CP-15 | Cubierta |
| F7 — Seguridad básica | CP-16, CP-17 | Cubierta |
| F8 — Predicción M07 | CP-18, CP-19 | Cubierta |
| F9 — Predicción M08 | CP-20, CP-21 | Cubierta |
| F10 — Predicción M09 | CP-22a, CP-22b, CP-22c | Cubierta |
| F11 — Valores extremos | CP-23, CP-24 | Cubierta |
| F12 — Almacenamiento | CP-25 | Cubierta |
| F13 — Consulta de historial | CP-26 | Cubierta |
| F14 — BD no disponible | CP-27 | Cubierta |

Todas las funcionalidades identificadas en el alcance inicial tienen al menos un caso de prueba asociado.

### 8.6. Cobertura negativa

Los casos negativos verifican explícitamente que el sistema rechace o maneje de forma controlada situaciones incorrectas o excepcionales. Se consideran principalmente CP-04, CP-05, CP-06, CP-09, CP-11, CP-12, CP-14, CP-16, CP-17 y CP-27. Los casos CP-23 y CP-24 complementan esta cobertura desde la perspectiva de robustez, verificando que valores extremos no provoquen fallos no controlados.

La cobertura negativa contempla entradas inválidas, campos faltantes, tipos incorrectos, valores fuera de rango, endpoints inexistentes, entradas maliciosas, errores internos y condiciones de indisponibilidad.

### 8.7. Cobertura no funcional

| Categoría | ¿Aplica? | Justificación / caso asociado |
|---|---|---|
| Rendimiento | No, en esta etapa | Las pruebas de carga o rendimiento bajo volumen alto de solicitudes quedan fuera del alcance inicial. |
| Confiabilidad | Sí | CP-27 verifica el comportamiento ante indisponibilidad de la base de datos. |
| Seguridad | Sí | CP-16 y CP-17 verifican entradas maliciosas y exposición de información sensible. |
| Usabilidad | Sí | CP-28 evalúa manualmente la claridad del formulario para un usuario nuevo. |
| Mantenibilidad | Sí, de forma indirecta | El análisis estático con Pylint aporta evidencia sobre la calidad y mantenibilidad del código. |
| Compatibilidad | No, en esta etapa | No se han definido navegadores o dispositivos objetivo para pruebas de compatibilidad. |
