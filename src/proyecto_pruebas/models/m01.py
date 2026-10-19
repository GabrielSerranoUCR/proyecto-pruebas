"""
Modelo (MVC) de M01: Aprobación del curso (Clasificación binaria).
Contrato de entrada/salida y lógica de predicción.
"""

import os
import uuid
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

MODELS_DIR = Path(__file__).resolve().parents[3] / "training" / "models"
# El cuaderno de entrenamiento exporta el modelo con este nombre
DEFAULT_MODEL_PATH = MODELS_DIR / "m02_aprobacion_curso.joblib"

# Mismos rangos de edad que el cuaderno de entrenamiento (la edad se codifica por rango)
BINS_EDAD = [-np.inf, 14, 16, 17, 18, 22, np.inf]

# Con strict=True, int no acepta bool (True/False) ni cadenas
SiNo = Annotated[int, Field(ge=1, le=2)]
Escala = Annotated[int, Field(ge=1, le=5)]
Escolaridad = Annotated[int, Field(ge=0, le=4)]


class M01Input(BaseModel):
    """Contrato de entrada del modelo M01 (mismas variables y codificación del entrenamiento)."""

    # strict=True evita que cadenas como "17" se conviertan silenciosamente a número
    model_config = ConfigDict(strict=True, extra="forbid", json_schema_extra={"examples": [{
        "sex": 2, "age": 17, "famsize": 1, "Medu": 2, "Fedu": 1, "failures": 0,
        "absences": 4, "reason": 3, "schoolsup": 2, "famsup": 1, "nursery": 1,
        "higher": 1, "internet": 1, "activities": 2, "freetime": 3, "Dalc": 1, "health": 3,
    }]})

    sex: int = Field(ge=1, le=2, description="Sexo del estudiante: 1 = masculino, 2 = femenino.")
    age: int = Field(ge=15, le=22, description="Edad en años.")
    famsize: int = Field(
        ge=1, le=2, description="Tamaño de la familia: 1 = más de 3 miembros, 2 = 3 o menos."
    )
    Medu: Escolaridad = Field(
        description="Escolaridad de la madre: 0 = ninguna, 1 = primaria (4.º grado), "
                    "2 = primaria completa, 3 = secundaria, 4 = superior.",
    )
    Fedu: Escolaridad = Field(
        description="Escolaridad del padre: 0 = ninguna, 1 = primaria (4.º grado), "
                    "2 = primaria completa, 3 = secundaria, 4 = superior.",
    )
    failures: int = Field(ge=0, le=3, description="Cursos reprobados anteriormente (3 = 3 o más).")
    absences: int = Field(ge=0, le=93, description="Cantidad de ausencias.")
    reason: int = Field(
        ge=1, le=4,
        description="Motivo para elegir la escuela: 1 = oferta de cursos, 2 = cercanía al hogar, "
                    "3 = reputación, 4 = otro.",
    )
    schoolsup: SiNo = Field(description="Apoyo educativo extra de la escuela: 1 = sí, 2 = no.")
    famsup: SiNo = Field(description="Apoyo educativo de la familia: 1 = sí, 2 = no.")
    nursery: SiNo = Field(description="Asistió a preescolar: 1 = sí, 2 = no.")
    higher: SiNo = Field(description="Desea cursar estudios superiores: 1 = sí, 2 = no.")
    internet: SiNo = Field(description="Acceso a internet en casa: 1 = sí, 2 = no.")
    activities: SiNo = Field(description="Actividades extracurriculares: 1 = sí, 2 = no.")
    freetime: Escala = Field(
        description="Tiempo libre después de clases: 1 = muy poco a 5 = mucho."
    )
    Dalc: Escala = Field(
        description="Consumo de alcohol entre semana: 1 = muy bajo a 5 = muy alto."
    )
    health: Escala = Field(description="Estado de salud actual: 1 = muy malo a 5 = muy bueno.")


class M01Metrica(BaseModel):
    """Métricas del modelo obtenidas sobre el conjunto de prueba."""

    Accuracy: float = Field(description="Proporción de estudiantes clasificados correctamente.")
    Precision: float = Field(description="De los clasificados como aprobados, cuántos aprueban.")
    Recall: float = Field(description="De los que aprueban, cuántos detecta el modelo.")
    F1: float = Field(description="Media armónica entre Precision y Recall.")


class M01Output(BaseModel):
    """Contrato de respuesta común: fecha, hora, modelo, predicción, métrica e id_ejecucion."""

    id_ejecucion: str = Field(description="Identificador único (UUID v4) de la ejecución.")
    fecha: str = Field(description="Fecha de la ejecución (AAAA-MM-DD).")
    hora: str = Field(description="Hora de la ejecución (HH:MM:SS).")
    modelo: str = Field(description='Identificador del modelo ("M01").')
    prediccion: Literal[0, 1] = Field(description="Clase predicha: 1 = aprueba, 0 = no aprueba.")
    etiqueta: str = Field(description='Clase predicha en texto ("Aprueba" o "No aprueba").')
    probabilidad: float = Field(
        description="Probabilidad estimada de aprobar (0 a 1), con 4 decimales."
    )
    descripcion_probabilidad: str = Field(description="Qué representa el campo probabilidad.")
    metrica: M01Metrica = Field(description="Métricas del modelo sobre el conjunto de prueba.")


@lru_cache(maxsize=1)
def load_m01_artifact() -> dict:
    """Carga (una sola vez) el artefacto entrenado del modelo M01."""
    model_path = Path(os.environ.get("M01_MODEL_PATH", DEFAULT_MODEL_PATH))
    if not model_path.exists():
        raise FileNotFoundError(f"No se encontró el artefacto del modelo en: {model_path}")
    return joblib.load(model_path)


def predict(payload: M01Input) -> M01Output:
    """Estima si un estudiante aprobará el curso."""
    artifact = load_m01_artifact()
    features = pd.DataFrame([payload.model_dump()])
    # El modelo se entrenó con el código del rango de edad, no con la edad en años
    features["age"] = pd.cut(features["age"], bins=BINS_EDAD, labels=False)
    features = features[artifact["feature_names"]].astype(float)

    pipeline = artifact["pipeline"]
    prediction = int(pipeline.predict(features)[0])
    probability = float(pipeline.predict_proba(features)[0][1])

    now = datetime.now()
    return M01Output(
        id_ejecucion=str(uuid.uuid4()),
        fecha=now.strftime("%Y-%m-%d"),
        hora=now.strftime("%H:%M:%S"),
        modelo="M01",
        prediccion=prediction,
        etiqueta="Aprueba" if prediction == 1 else "No aprueba",
        probabilidad=round(probability, 4),
        descripcion_probabilidad="Probabilidad de aprobar",
        metrica=M01Metrica(**artifact["metrics"]),
    )
