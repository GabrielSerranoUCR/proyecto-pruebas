# Contrato del API — M01: Aprobación del curso

Especificación del endpoint del modelo M01 (Educación, clasificación binaria), según el "Contrato mínimo del API" del enunciado del proyecto: endpoint, método, parámetros, tipos, campos obligatorios, reglas de validación, valores permitidos, respuesta exitosa y respuesta de error.

Con la aplicación en ejecución (`uv run proyecto-pruebas-api`), la misma especificación se puede consultar en formato OpenAPI en <http://127.0.0.1:8000/docs> y <http://127.0.0.1:8000/openapi.json>.

## Endpoint

| Elemento | Valor |
|---|---|
| URL | `http://127.0.0.1:8000/predict/m01` |
| Método | `POST` |
| Encabezado | `Content-Type: application/json` |
| Cuerpo | Objeto JSON con los 17 parámetros del modelo |
| Autenticación | No aplica (sin autenticación, por lo que no se usa el código 401) |
| Predicción | Si el estudiante aprueba el curso (`1`) o no (`0`), sin usar sus notas |

## Parámetros de entrada

Los **17 campos son obligatorios**. Los nombres y la codificación coinciden con las columnas usadas en el entrenamiento (`training/notebooks/Aprobacion_de_curso_training_model.ipynb`).

| Campo | Tipo | Regla de validación | Valores permitidos | Descripción |
|---|---|---|---|---|
| `sex` | entero | 1 ≤ valor ≤ 2 | `1` = masculino, `2` = femenino | Sexo del estudiante |
| `age` | entero | 15 ≤ valor ≤ 22 | 15 a 22 | Edad en años |
| `famsize` | entero | 1 ≤ valor ≤ 2 | `1` = más de 3 miembros, `2` = 3 o menos | Tamaño de la familia |
| `Medu` | entero | 0 ≤ valor ≤ 4 | `0` = ninguna, `1` = primaria (4.º grado), `2` = primaria completa, `3` = secundaria, `4` = superior | Escolaridad de la madre |
| `Fedu` | entero | 0 ≤ valor ≤ 4 | Igual que `Medu` | Escolaridad del padre |
| `failures` | entero | 0 ≤ valor ≤ 3 | 0 a 3 (`3` = 3 o más) | Cursos reprobados anteriormente |
| `absences` | entero | 0 ≤ valor ≤ 93 | 0 a 93 | Cantidad de ausencias |
| `reason` | entero | 1 ≤ valor ≤ 4 | `1` = oferta de cursos, `2` = cercanía al hogar, `3` = reputación, `4` = otro | Motivo para elegir la escuela |
| `schoolsup` | entero | 1 ≤ valor ≤ 2 | `1` = sí, `2` = no | Apoyo educativo extra de la escuela |
| `famsup` | entero | 1 ≤ valor ≤ 2 | `1` = sí, `2` = no | Apoyo educativo de la familia |
| `nursery` | entero | 1 ≤ valor ≤ 2 | `1` = sí, `2` = no | Asistió a preescolar |
| `higher` | entero | 1 ≤ valor ≤ 2 | `1` = sí, `2` = no | Desea cursar estudios superiores |
| `internet` | entero | 1 ≤ valor ≤ 2 | `1` = sí, `2` = no | Acceso a internet en casa |
| `activities` | entero | 1 ≤ valor ≤ 2 | `1` = sí, `2` = no | Actividades extracurriculares |
| `freetime` | entero | 1 ≤ valor ≤ 5 | `1` = muy poco … `5` = mucho | Tiempo libre después de clases |
| `Dalc` | entero | 1 ≤ valor ≤ 5 | `1` = muy bajo … `5` = muy alto | Consumo de alcohol entre semana |
| `health` | entero | 1 ≤ valor ≤ 5 | `1` = muy malo … `5` = muy bueno | Estado de salud actual |

### Reglas generales de validación

- **Tipos estrictos:** no se convierten valores automáticamente. Una cadena (`"17"`, `"M"`, `"yes"`), un booleano (`true`/`false`) o `null` se rechazan con 400 aunque representen un valor válido.
- **Enteros:** todos los campos son enteros y no aceptan decimales (`17.5`).
- **Codificación:** las variables categóricas se envían con el código numérico del entrenamiento (por ejemplo `sí` = 1, `no` = 2), no con el texto original del conjunto de datos.
- **Edad:** se envía en años. La API la convierte internamente al mismo rango de edad que usó el entrenamiento (15–16, 17, 18, 19–22). El rango 15 a 22 corresponde a las edades presentes en el conjunto de datos.
- **Campos adicionales:** cualquier campo que no esté en la tabla se rechaza con 400 (`"Campo no permitido"`). Esto incluye las notas (`G1`, `G2`, `G3`, `Total`, ...), que el modelo no usa.
- **Cuerpo:** debe ser un objeto JSON válido; un JSON mal formado, un cuerpo vacío o un arreglo se rechazan con 400.

### Ejemplo de solicitud

```bash
curl -X POST http://127.0.0.1:8000/predict/m01 \
  -H "Content-Type: application/json" \
  -d '{
    "sex": 2, "age": 17, "famsize": 1, "Medu": 2, "Fedu": 1, "failures": 0,
    "absences": 4, "reason": 3, "schoolsup": 2, "famsup": 1, "nursery": 1,
    "higher": 1, "internet": 1, "activities": 2, "freetime": 3, "Dalc": 1, "health": 3
  }'
```

## Respuesta exitosa — 200 OK

```json
{
  "id_ejecucion": "a80467d6-8055-4f50-a619-05ff2682d0ed",
  "fecha": "2026-10-18",
  "hora": "20:22:07",
  "modelo": "M01",
  "prediccion": 0,
  "etiqueta": "No aprueba",
  "probabilidad": 0.4234,
  "descripcion_probabilidad": "Probabilidad de aprobar",
  "metrica": { "Accuracy": 0.6582, "Precision": 0.3333, "Recall": 0.6875, "F1": 0.449 }
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `id_ejecucion` | cadena | Identificador único (UUID v4) de la ejecución |
| `fecha` | cadena | Fecha de la ejecución, formato `AAAA-MM-DD` |
| `hora` | cadena | Hora de la ejecución, formato `HH:MM:SS` |
| `modelo` | cadena | Identificador del modelo: `"M01"` |
| `prediccion` | entero | Clase predicha: `1` = aprueba, `0` = no aprueba |
| `etiqueta` | cadena | Clase predicha en texto: `"Aprueba"` o `"No aprueba"` (campo adicional) |
| `probabilidad` | número | Probabilidad estimada de aprobar, de 0 a 1, redondeada a 4 decimales (campo adicional) |
| `descripcion_probabilidad` | cadena | Qué representa `probabilidad`: `"Probabilidad de aprobar"` (campo adicional) |
| `metrica` | objeto | Métricas del modelo sobre el conjunto de prueba (`Accuracy`, `Precision`, `Recall`, `F1`) |

**Justificación de los cambios respecto al JSON de referencia:**

- `metrica` es un objeto y no un único número. El enunciado pide Accuracy, Precision, Recall y F1 para modelos de clasificación. Con clases desbalanceadas (81 aprobados de 395) la exactitud sola engaña, por lo que se reportan las cuatro. Se leen del artefacto exportado por el cuaderno, por lo que se actualizan solas al reentrenar.
- `etiqueta` permite mostrar el resultado sin conocer la codificación de la clase.
- `probabilidad` indica qué tan seguro está el modelo; la clase es `1` cuando la probabilidad es 0.5 o más.
- `descripcion_probabilidad` permite que la interfaz muestre la probabilidad de cualquier modelo de clasificación sin conocer su significado de antemano.

## Respuestas de error

Las respuestas de error son las mismas que en M02 (`error`, `campo`, `detalle` y `errores`). Ver la sección "Respuestas de error" de [`contrato_api_m02.md`](contrato_api_m02.md) para el formato completo y la lista de mensajes de `detalle`.

| Situación | Código HTTP | `error` |
|---|---|---|
| Solicitud válida | 200 | — |
| Campo faltante, nulo, con tipo incorrecto, fuera de rango o no permitido | 400 | `"Parámetro inválido"` |
| JSON mal formado | 400 | `"JSON mal formado"` |
| Cuerpo vacío o que no es un objeto JSON | 400 | `"Cuerpo de la solicitud inválido"` |
| Ruta o modelo inexistente (por ejemplo `/predict/m99`) | 404 | `"Ruta no encontrada"` |
| Método distinto de `POST` en `/predict/m01` | 405 | `"Método no permitido"` |
| Fallo no controlado del servicio (por ejemplo, modelo no generado) | 500 | `"Error interno del servidor"` |

Edad fuera de rango (`"age": 30`):

```json
{
  "error": "Parámetro inválido",
  "campo": "age",
  "detalle": "El valor debe ser menor o igual que 22",
  "errores": [{ "campo": "age", "detalle": "El valor debe ser menor o igual que 22" }]
}
```

Texto en lugar del código (`"sex": "M"`):

```json
{
  "error": "Parámetro inválido",
  "campo": "sex",
  "detalle": "Debe ser un número entero",
  "errores": [{ "campo": "sex", "detalle": "Debe ser un número entero" }]
}
```
