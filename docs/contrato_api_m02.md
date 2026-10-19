# Contrato del API — M02: Presión arterial estimada

Especificación del endpoint del modelo M02 (Salud, regresión), según el "Contrato mínimo del API" del enunciado del proyecto: endpoint, método, parámetros, tipos, campos obligatorios, reglas de validación, valores permitidos, respuesta exitosa y respuesta de error.

Con la aplicación en ejecución (`uv run proyecto-pruebas-api`), la misma especificación se puede consultar en formato OpenAPI en <http://127.0.0.1:8000/docs> y <http://127.0.0.1:8000/openapi.json>.

## Endpoint

| Elemento | Valor |
|---|---|
| URL | `http://127.0.0.1:8000/predict/m02` |
| Método | `POST` |
| Encabezado | `Content-Type: application/json` |
| Cuerpo | Objeto JSON con los 13 parámetros del modelo |
| Autenticación | No aplica (sin autenticación, por lo que no se usa el código 401) |
| Predicción | Presión arterial sistólica (`sysBP`) estimada, en mmHg |

## Parámetros de entrada

Los **13 campos son obligatorios**. Los nombres coinciden con las columnas del conjunto de datos usado en el entrenamiento (`training/train_m02.py`).

| Campo | Tipo | Regla de validación | Valores permitidos | Descripción |
|---|---|---|---|---|
| `male` | entero | 0 ≤ valor ≤ 1 | `0` = femenino, `1` = masculino | Sexo del paciente |
| `age` | entero | 1 ≤ valor ≤ 120 | 1 a 120 | Edad en años |
| `education` | entero | 1 ≤ valor ≤ 4 | `1` = primaria, `2` = secundaria, `3` = técnico, `4` = universitario | Nivel educativo |
| `currentSmoker` | entero | 0 ≤ valor ≤ 1 | `0` = no, `1` = sí | Fumador actual |
| `cigsPerDay` | número | 0 ≤ valor ≤ 100 | 0 a 100 | Cigarrillos por día |
| `BPMeds` | entero | 0 ≤ valor ≤ 1 | `0` = no, `1` = sí | Toma medicamentos para la presión |
| `prevalentStroke` | entero | 0 ≤ valor ≤ 1 | `0` = no, `1` = sí | Derrame cerebral previo |
| `prevalentHyp` | entero | 0 ≤ valor ≤ 1 | `0` = no, `1` = sí | Hipertensión previa |
| `diabetes` | entero | 0 ≤ valor ≤ 1 | `0` = no, `1` = sí | Diabetes |
| `totChol` | número | 0 < valor ≤ 1000 | mayor que 0, hasta 1000 | Colesterol total (mg/dL) |
| `BMI` | número | 0 < valor ≤ 100 | mayor que 0, hasta 100 | Índice de masa corporal (kg/m²) |
| `heartRate` | número | 0 < valor ≤ 300 | mayor que 0, hasta 300 | Frecuencia cardíaca (lpm) |
| `glucose` | número | 0 < valor ≤ 1000 | mayor que 0, hasta 1000 | Glucosa (mg/dL) |

### Reglas generales de validación

- **Tipos estrictos:** no se convierten valores automáticamente. Una cadena (`"35"`), un booleano (`true`/`false`) o `null` se rechazan con 400 aunque representen un valor válido.
- **Enteros:** los campos de tipo entero no aceptan decimales (`50.5`). Los campos de tipo número aceptan enteros y decimales.
- **Campos adicionales:** cualquier campo que no esté en la tabla se rechaza con 400 (`"Campo no permitido"`).
- **Cuerpo:** debe ser un objeto JSON válido; un JSON mal formado, un cuerpo vacío o un arreglo se rechazan con 400.
- **`currentSmoker` y `cigsPerDay`:** la API no valida la combinación de ambos campos. Es la interfaz la que fija `cigsPerDay = 0` cuando `currentSmoker = 0`.

### Ejemplo de solicitud

```bash
curl -X POST http://127.0.0.1:8000/predict/m02 \
  -H "Content-Type: application/json" \
  -d '{
    "male": 1, "age": 50, "education": 2, "currentSmoker": 1, "cigsPerDay": 20,
    "BPMeds": 0, "prevalentStroke": 0, "prevalentHyp": 0, "diabetes": 0,
    "totChol": 240, "BMI": 26.5, "heartRate": 75, "glucose": 80
  }'
```

## Respuesta exitosa — 200 OK

```json
{
  "id_ejecucion": "e43a417d-9f19-4a08-ad1a-95b3347e17df",
  "fecha": "2026-10-18",
  "hora": "19:36:31",
  "modelo": "M02",
  "prediccion": 123.28,
  "unidad": "mmHg",
  "metrica": { "MAE": 10.8114, "RMSE": 14.3936, "R2": 0.5321 }
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `id_ejecucion` | cadena | Identificador único (UUID v4) de la ejecución |
| `fecha` | cadena | Fecha de la ejecución, formato `AAAA-MM-DD` |
| `hora` | cadena | Hora de la ejecución, formato `HH:MM:SS` |
| `modelo` | cadena | Identificador del modelo: `"M02"` |
| `prediccion` | número | Presión arterial sistólica estimada, redondeada a 2 decimales |
| `unidad` | cadena | Unidad de la predicción: `"mmHg"` (campo adicional) |
| `metrica` | objeto | Métricas del modelo sobre el conjunto de prueba (`MAE`, `RMSE`, `R2`) |

**Justificación de los cambios respecto al JSON de referencia:**

- `metrica` es un objeto y no un único número. El enunciado pide MAE, MSE/RMSE y R² para modelos de regresión, y ninguna de esas métricas basta por sí sola: MAE y RMSE miden el error en mmHg y R² mide qué proporción de la variabilidad explica el modelo. Son métricas del modelo calculadas sobre el 20 % de prueba en el entrenamiento, no una medida de confianza de cada predicción. Si se reentrena el modelo, deben actualizarse en `METRICAS_PRUEBA` (`src/proyecto_pruebas/models/m02.py`).
- `unidad` se agrega porque la predicción es un valor numérico y sin unidad no se puede interpretar.

## Respuestas de error

Todas las respuestas de error usan el formato de referencia del enunciado (`error`, `campo`, `detalle`). Ninguna expone stack traces, rutas internas ni credenciales.

| Situación | Código HTTP | `error` |
|---|---|---|
| Solicitud válida | 200 | — |
| Campo faltante, nulo, con tipo incorrecto, fuera de rango o no permitido | 400 | `"Parámetro inválido"` |
| JSON mal formado | 400 | `"JSON mal formado"` |
| Cuerpo vacío o que no es un objeto JSON | 400 | `"Cuerpo de la solicitud inválido"` |
| Ruta o modelo inexistente (por ejemplo `/predict/m99`) | 404 | `"Ruta no encontrada"` |
| Método distinto de `POST` en `/predict/m02` | 405 | `"Método no permitido"` |
| Fallo no controlado del servicio (por ejemplo, modelo no generado) | 500 | `"Error interno del servidor"` |

### 400 — Datos inválidos

| Campo | Tipo | Descripción |
|---|---|---|
| `error` | cadena | Tipo de error |
| `campo` | cadena o `null` | Primer campo con error; `null` si el error es del cuerpo completo |
| `detalle` | cadena | Explicación del primer error |
| `errores` | arreglo | Todos los errores de validación, cada uno con `campo` y `detalle` (campo adicional, para que la interfaz muestre todos los errores de una vez) |

Valor fuera de rango (`"age": 0`):

```json
{
  "error": "Parámetro inválido",
  "campo": "age",
  "detalle": "El valor debe ser mayor o igual que 1",
  "errores": [{ "campo": "age", "detalle": "El valor debe ser mayor o igual que 1" }]
}
```

JSON mal formado (`{"age": `):

```json
{
  "error": "JSON mal formado",
  "campo": null,
  "detalle": "El cuerpo de la solicitud no es un JSON válido",
  "errores": [{ "campo": null, "detalle": "El cuerpo de la solicitud no es un JSON válido" }]
}
```

Mensajes posibles en `detalle`:

| Caso | `detalle` |
|---|---|
| Campo faltante | `Campo requerido` |
| Cadena, booleano, `null` o decimal en un campo entero | `Debe ser un número entero` |
| Cadena, booleano o `null` en un campo numérico | `Debe ser un número` |
| Debajo del mínimo inclusivo | `El valor debe ser mayor o igual que <mínimo>` |
| Debajo o igual al mínimo exclusivo (`totChol`, `BMI`, `heartRate`, `glucose`) | `El valor debe ser mayor que 0` |
| Encima del máximo | `El valor debe ser menor o igual que <máximo>` |
| Campo que no forma parte del contrato | `Campo no permitido` |
| JSON mal formado | `El cuerpo de la solicitud no es un JSON válido` |
| Cuerpo vacío | `Se requiere un cuerpo JSON` |
| Cuerpo que no es un objeto (por ejemplo un arreglo) | `El cuerpo debe ser un objeto JSON` |

### 404, 405 y 500

Solo incluyen `error`:

```json
{ "error": "Ruta no encontrada" }
```

```json
{ "error": "Método no permitido" }
```

```json
{ "error": "Error interno del servidor" }
```
