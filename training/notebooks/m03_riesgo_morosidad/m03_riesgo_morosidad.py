"""Entrenamiento del modelo M03 (riesgo de morosidad). Decisiones en README.md."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
RUTA_DATOS = RAIZ / "data" / "raw" / "M01-M02-M03.xlsx"
HOJA_ENTRENAMIENTO = "Mor Riesgo Ent"
RUTA_MODELO = RAIZ / "models" / "m03_riesgo_morosidad.joblib"

SEMILLA = 42
PROPORCION_PRUEBA = 0.2
PLIEGUES_CV = 5

CORTE_MEDIO = 0.33
CORTE_ALTO = 0.67
NIVELES = ("bajo", "medio", "alto")