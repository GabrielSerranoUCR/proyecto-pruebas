# Módulos de Entrenamiento y Modelos de Machine Learning

## Preparación del ambiente

Asegurarse de tener sincronizadas las dependencias para Jupyter y ciencia de datos:

```bash
uv sync --group jupyter
```

Se recomienda utilizar el kernel del entorno virtual `.venv` generado por `uv` al abrir los notebooks en VS Code.

---

## Modelo M02: Presión Arterial Estimada (Regresión)

- **Dataset:** `training/data/raw/m02_presion_arterial.csv`
- **Variable objetivo:** `sysBP` (Presión arterial sistólica en mmHg)
- **Métricas evaluadas:** MAE, MSE / RMSE, R² (con validación cruzada K-Fold de 5 pliegues).
- **Notebook interactivo:** `training/notebooks/M02_Blood_Pressure_model.ipynb`
- **Script CLI directo:**
  ```bash
  uv run python training/train_m02.py
  ```
- **Artefacto exportado:** `training/models/m02_presion_arterial.joblib` (incluye preprocesador de imputación/escalado y modelo entrenado).