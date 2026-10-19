"""
Modelo (MVC) de M02: Presión Arterial Estimada (Regresión).
Contrato de entrada/salida y lógica de predicción.
"""

import os
import uuid
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Annotated

import joblib
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

MODELS_DIR = Path(__file__).resolve().parents[3] / "training" / "models"
DEFAULT_MODEL_PATH = MODELS_DIR / "blood_pressure_ridge_model.joblib"

# Métricas sobre el conjunto de prueba (20 %) reportadas por training/train_m02.py para Ridge.
# El modelo exportado no las incluye, por lo que deben actualizarse si se reentrena con otros datos.
METRICAS_PRUEBA = {"MAE": 10.8114, "RMSE": 14.3936, "R2": 0.5321}

# Con strict=True, int no acepta bool (True/False) ni cadenas
Binary = Annotated[int, Field(ge=0, le=1)]


class M02Input(BaseModel):
    """Contrato de entrada del modelo M02 (mismas variables usadas en el entrenamiento)."""

    # strict=True evita que cadenas como "35" se conviertan silenciosamente a número
    model_config = ConfigDict(strict=True, extra="forbid")

    male: Binary
    age: int = Field(ge=1, le=120)
    education: int = Field(ge=1, le=4)
    currentSmoker: Binary
    cigsPerDay: float = Field(ge=0, le=100)
    BPMeds: Binary
    prevalentStroke: Binary
    prevalentHyp: Binary
    diabetes: Binary
    totChol: float = Field(gt=0, le=1000)
    BMI: float = Field(gt=0, le=100)
    heartRate: float = Field(gt=0, le=300)
    glucose: float = Field(gt=0, le=1000)


class M02Metrica(BaseModel):
    """Métricas del modelo obtenidas sobre el conjunto de prueba."""

    MAE: float
    RMSE: float
    R2: float


class M02Output(BaseModel):
    """Contrato de respuesta común: fecha, hora, modelo, predicción, métrica e id_ejecucion."""

    id_ejecucion: str
    fecha: str
    hora: str
    modelo: str
    prediccion: float
    unidad: str
    metrica: M02Metrica


@lru_cache(maxsize=1)
def load_m02_artifact():
    """Carga (una sola vez) el pipeline entrenado del modelo M02."""
    model_path = Path(os.environ.get("M02_MODEL_PATH", DEFAULT_MODEL_PATH))
    if not model_path.exists():
        raise FileNotFoundError(f"No se encontró el artefacto del modelo en: {model_path}")
    return joblib.load(model_path)


def predict(payload: M02Input) -> M02Output:
    """Estima la presión arterial sistólica (sysBP, en mmHg) de un paciente."""
    pipeline = load_m02_artifact()
    features = pd.DataFrame([payload.model_dump()])
    # El pipeline exportado conserva el orden de columnas con el que se entrenó
    if hasattr(pipeline, "feature_names_in_"):
        features = features[list(pipeline.feature_names_in_)]
    prediction = float(pipeline.predict(features)[0])

    now = datetime.now()
    return M02Output(
        id_ejecucion=str(uuid.uuid4()),
        fecha=now.strftime("%Y-%m-%d"),
        hora=now.strftime("%H:%M:%S"),
        modelo="M02",
        prediccion=round(prediction, 2),
        unidad="mmHg",
        metrica=M02Metrica(**METRICAS_PRUEBA),
    )
