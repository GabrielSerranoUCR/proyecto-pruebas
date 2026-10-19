# Contrato del API — M03: Riesgo de morosidad

Especificación del endpoint del modelo M03 (Finanzas, clasificación multiclase), según el "Contrato mínimo del API" del enunciado del proyecto: endpoint, método, parámetros, tipos, campos obligatorios, reglas de validación, valores permitidos, respuesta exitosa y respuesta de error.

Con la aplicación en ejecución (`uv run proyecto-pruebas-api`), la misma especificación se puede consultar en formato OpenAPI en <http://127.0.0.1:8000/docs> y <http://127.0.0.1:8000/openapi.json>.

## Endpoint

| Elemento | Valor |
|---|---|
| URL | `http://127.0.0.1:8000/predict/m03` |
| Método | `POST` |
| Encabezado | `Content-Type: application/json` |
| Cuerpo | Objeto JSON con los 11 parámetros del modelo |
| Autenticación | No aplica (sin autenticación, por lo que no se usa el código 401) |
| Predicción | Nivel de riesgo de la solicitud de préstamo: `bajo`, `medio` o `alto` |

## Parámetros de entrada

Los **11 campos son obligatorios**. Los nombres y los valores coinciden con las columnas del conjunto de datos usado en el entrenamiento (`training/notebooks/m03_riesgo_morosidad/entrenamiento.py`). A diferencia de M01 y M02, las variables categóricas se envían **como texto**, con los mismos valores del conjunto de datos, porque el modelo exportado hace su propia codificación. Así las filas de la hoja "Mor Riesgo Test" se pueden enviar al API sin transformarlas (salvo `Dependents` = `"3+"`, que se envía como `3`).

| Campo | Tipo | Regla de validación | Valores permitidos | Descripción |
|---|---|---|---|---|
| `Gender` | cadena | Uno de los valores permitidos | `"Male"`, `"Female"` | Sexo del solicitante |
| `Married` | cadena | Uno de los valores permitidos | `"Yes"`, `"No"` | Casado |
| `Dependents` | entero | 0 ≤ valor ≤ 3 | 0 a 3 (`3` = 3 o más) | Cantidad de dependientes |
| `Education` | cadena | Uno de los valores permitidos | `"Graduate"`, `"Not Graduate"` | Educación |
| `Self_Employed` | cadena | Uno de los valores permitidos | `"Yes"`, `"No"` | Trabaja por cuenta propia |
| `ApplicantIncome` | número | 0 ≤ valor ≤ 100000 | 0 a 100000 | Ingreso mensual del solicitante, en dólares (USD) |
| `CoapplicantIncome` | número | 0 ≤ valor ≤ 100000 | 0 a 100000 (0 si no hay codeudor) | Ingreso mensual del codeudor, en dólares (USD) |
| `LoanAmount` | número | 0 < valor ≤ 1000 | mayor que 0, hasta 1000 | Monto del préstamo, en miles de dólares (USD) |
| `Loan_Amount_Term` | número | 0 < valor ≤ 480 | mayor que 0, hasta 480 | Plazo del préstamo, en meses |
| `Credit_History` | entero | 0 ≤ valor ≤ 1 | `1` = cumple las pautas, `0` = no | Historial crediticio |
| `Property_Area` | cadena | Uno de los valores permitidos | `"Urban"`, `"Semiurban"`, `"Rural"` | Zona de la propiedad |

### Reglas generales de validación

- **Tipos estrictos:** no se convierten valores automáticamente. Una cadena en un campo numérico (`"5000"`), un número en un campo de texto, un booleano (`true`/`false`) o `null` se rechazan con 400.
- **Valores de texto:** distinguen mayúsculas y minúsculas (`"male"` o `"yes"` se rechazan). El modelo ignoraría en silencio una categoría desconocida, por eso la API la rechaza.
- **Enteros:** `Dependents` y `Credit_History` no aceptan decimales. Los campos de tipo número aceptan enteros y decimales.
- **Faltantes:** aunque el modelo puede imputar valores faltantes, la API no acepta campos vacíos ni `null` y responde 400.
- **Campos adicionales:** cualquier campo que no esté en la tabla se rechaza con 400 (`"Campo no permitido"`). Esto incluye `Loan_ID` y `Loan_Status`.
- **Cuerpo:** debe ser un objeto JSON válido; un JSON mal formado, un cuerpo vacío o un arreglo se rechazan con 400.
- **`CoapplicantIncome`:** la API no pregunta si hay codeudor. La interfaz muestra una pregunta propia ("¿Tiene codeudor?") que no se envía, y fija `CoapplicantIncome = 0` cuando la respuesta es "No".

### Ejemplo de solicitud

```bash
curl -X POST http://127.0.0.1:8000/predict/m03 \
  -H "Content-Type: application/json" \
  -d '{
    "Gender": "Male", "Married": "Yes", "Dependents": 0, "Education": "Graduate",
    "Self_Employed": "No", "ApplicantIncome": 5720, "CoapplicantIncome": 0,
    "LoanAmount": 110, "Loan_Amount_Term": 360, "Credit_History": 1,
    "Property_Area": "Urban"
  }'
```

## Respuesta exitosa — 200 OK

```json
{
  "id_ejecucion": "d1ba0576-ecd2-46cf-ab47-e4b6da6f5709",
  "fecha": "2026-10-18",
  "hora": "20:22:07",
  "modelo": "M03",
  "prediccion": "bajo",
  "etiqueta": "Riesgo bajo",
  "probabilidad": 0.185,
  "descripcion_probabilidad": "Probabilidad de rechazo",
  "metrica": { "Accuracy": 0.813, "Precision": 0.8571, "Recall": 0.4737, "F1": 0.6102 }
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `id_ejecucion` | cadena | Identificador único (UUID v4) de la ejecución |
| `fecha` | cadena | Fecha de la ejecución, formato `AAAA-MM-DD` |
| `hora` | cadena | Hora de la ejecución, formato `HH:MM:SS` |
| `modelo` | cadena | Identificador del modelo: `"M03"` |
| `prediccion` | cadena | Nivel de riesgo: `"bajo"`, `"medio"` o `"alto"` |
| `etiqueta` | cadena | Nivel de riesgo en texto: `"Riesgo bajo"`, `"Riesgo medio"` o `"Riesgo alto"` (campo adicional) |
| `probabilidad` | número | Probabilidad estimada de rechazo, de 0 a 1, redondeada a 4 decimales (campo adicional) |
| `descripcion_probabilidad` | cadena | Qué representa `probabilidad`: `"Probabilidad de rechazo"` (campo adicional) |
| `metrica` | objeto | Métricas del clasificador de rechazo sobre el conjunto de prueba (`Accuracy`, `Precision`, `Recall`, `F1`) |

### Cómo se obtiene el nivel

El conjunto de datos no trae una etiqueta de tres clases; se usa el rechazo del préstamo (`Loan_Status` = N) como sustituto del riesgo (ver `training/notebooks/m03_riesgo_morosidad/readme.md`). El modelo estima la probabilidad de rechazo `p` y el nivel sale de cortes fijos guardados en el artefacto:

| Probabilidad de rechazo | `prediccion` |
|---|---|
| `p` < 0.33 | `"bajo"` |
| 0.33 ≤ `p` < 0.67 | `"medio"` |
| `p` ≥ 0.67 | `"alto"` |

**Justificación de los cambios respecto al JSON de referencia:**

- `metrica` es un objeto con Accuracy, Precision, Recall y F1, que el enunciado pide para clasificación. Corresponden al clasificador binario de rechazo, porque sin etiquetas reales de tres clases no se pueden calcular métricas por nivel. Se leen del artefacto exportado, por lo que se actualizan solas al reentrenar.
- `probabilidad` se agrega porque el nivel se deriva de ella; permite ver qué tan cerca está una solicitud de un corte.
- `etiqueta` y `descripcion_probabilidad` tienen el mismo propósito que en M01: que la interfaz muestre el resultado sin conocer el modelo.

## Respuestas de error

Las respuestas de error son las mismas que en M02 (`error`, `campo`, `detalle` y `errores`). Ver la sección "Respuestas de error" de [`contrato_api_m02.md`](contrato_api_m02.md) para el formato completo y la lista de mensajes de `detalle`. M03 agrega dos mensajes por sus campos de texto:

| Caso | `detalle` |
|---|---|
| Valor de texto fuera de los permitidos, o un número en un campo de texto | `Valor no permitido; valores válidos: <valores>` |
| Valor que no es texto donde se espera una cadena | `Debe ser una cadena de texto` |

| Situación | Código HTTP | `error` |
|---|---|---|
| Solicitud válida | 200 | — |
| Campo faltante, nulo, con tipo incorrecto, fuera de rango o no permitido | 400 | `"Parámetro inválido"` |
| JSON mal formado | 400 | `"JSON mal formado"` |
| Cuerpo vacío o que no es un objeto JSON | 400 | `"Cuerpo de la solicitud inválido"` |
| Ruta o modelo inexistente (por ejemplo `/predict/m99`) | 404 | `"Ruta no encontrada"` |
| Método distinto de `POST` en `/predict/m03` | 405 | `"Método no permitido"` |
| Fallo no controlado del servicio (por ejemplo, modelo no generado) | 500 | `"Error interno del servidor"` |

Categoría no permitida (`"Gender": "X"`):

```json
{
  "error": "Parámetro inválido",
  "campo": "Gender",
  "detalle": "Valor no permitido; valores válidos: 'Male' o 'Female'",
  "errores": [{ "campo": "Gender", "detalle": "Valor no permitido; valores válidos: 'Male' o 'Female'" }]
}
```
