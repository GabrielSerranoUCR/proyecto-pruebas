# M03 - Riesgo de morosidad

Clasificación multiclase: estima el nivel de riesgo (bajo, medio, alto) de una solicitud de préstamo.

## Decisiones de diseño

1. **Variable objetivo.** El conjunto no trae una etiqueta de morosidad ni de tres clases. La única variable objetivo es `Loan_Status` (Y/N), que registra si la solicitud fue aprobada. Se usa el rechazo como sustituto del riesgo: `rechazo` = 1 si `Loan_Status` = N, 0 en otro caso.
2. **Niveles de riesgo.** Se entrena un clasificador binario sobre `rechazo`. El nivel sale de la probabilidad estimada de rechazo `p` con cortes fijos: bajo si `p` < 0.33, medio si 0.33 ≤ `p` < 0.67, alto si `p` ≥ 0.67. Los cortes se fijan antes de entrenar y se guardan en el artefacto exportado.
3. **Limitación.** No hay etiquetas reales de tres clases, así que no se calcula una matriz de confusión de 3×3. Los niveles se evalúan con la proporción de rechazos reales en cada uno.
4. **Entradas.** Las columnas de la solicitud, excepto `Loan_ID` (identificador) y `Loan_Status` (objetivo). `Dependents` se convierte a número ("3+" pasa a 3).
5. **Faltantes.** Se imputan dentro del pipeline: mediana en las numéricas y valor más frecuente en las categóricas. La API no acepta campos vacíos y responde 400.
6. **Codificación.** One-hot de las categóricas dentro del pipeline exportado, para que la API reciba el mismo preprocesamiento que el entrenamiento.
7. **Partición y selección.** División 80/20 estratificada por `rechazo`. El modelo se escoge por el F1 de la validación cruzada sobre el entrenamiento; el conjunto de prueba se usa solo para la medición final.
8. **Hoja "Mor Riesgo Test".** No trae `Loan_Status`, así que no se usa para métricas. Se reserva como datos de entrada para las pruebas de la API.

## Ejecución

```bash
uv run python training/notebooks/m03_riesgo_morosidad/entrenamiento.py
```

- **Nota:** el modelo exportado no se versiona (`.gitignore`); hay que correr el script antes de levantar la API.
