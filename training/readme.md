# Módulos de Entrenamiento y Modelos de Machine Learning

## Preparación del ambiente

Asegurarse de tener sincronizadas las dependencias para Jupyter y ciencia de datos:

```bash
uv sync --group jupyter
```

Se recomienda utilizar el kernel del entorno virtual `.venv` generado por `uv` al abrir los notebooks en VS Code.

---

## Modelo M01: Aprobación de Curso (Clasificación Binaria)

- **Dataset:** `training/data/raw/M01-M02-M03.xlsx` (Hoja `Aprobación de curso`)
- **Variable objetivo:** `Aprobado` (0 = no aprobado, 1 = aprobado)
- **Métricas evaluadas:** Accuracy, Precision, Recall, F1.
- **Notebook interactivo:** `training/notebooks/Aprobacion_de_curso_training_model.ipynb`
- **Modelo exportado:** `training/models/approval_sgd_model.joblib`

---

## Modelo M02: Presión Arterial Estimada (Regresión)

- **Dataset:** `training/data/raw/M01-M02-M03.xlsx` (Hoja `Presión Arterial`)
- **Variable objetivo:** `sysBP` (Presión arterial sistólica continua en mmHg)
- **Métricas evaluadas:** MAE, MSE / RMSE, R² (con validación cruzada K-Fold de 5 pliegues).
- **Notebook interactivo:** `training/notebooks/Presion_arterial_training_model.ipynb`
- **Script CLI directo:**
  ```bash
  uv run python training/train_m02.py
  ```
- **Modelo exportado:** `training/models/blood_pressure_ridge_model.joblib` (incluye escalador + modelo para inferencia).