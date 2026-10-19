"""
Modelo (MVC) de M03: Riesgo de morosidad (Clasificación multiclase).
Contrato de entrada/salida y lógica de predicción.
"""

import os
import uuid
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

import joblib
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

MODELS_DIR = Path(__file__).resolve().parents[3] / "training" / "models"
DEFAULT_MODEL_PATH = MODELS_DIR / "m03_riesgo_morosidad.joblib"

# El artefacto guarda las métricas en minúscula; la respuesta usa los mismos nombres que M01
NOMBRES_METRICAS = {
    "accuracy": "Accuracy", "precision": "Precision", "recall": "Recall", "f1": "F1",
}

# Con strict=True, int no acepta bool (True/False) ni cadenas
Binary = Annotated[int, Field(ge=0, le=1)]
SiNo = Literal["Yes", "No"]


class M03Input(BaseModel):
    """Contrato de entrada del modelo M03 (mismas columnas y valores del conjunto de datos)."""

    # strict=True evita que cadenas como "5000" se conviertan silenciosamente a número
    model_config = ConfigDict(strict=True, extra="forbid", json_schema_extra={"examples": [{
        "Gender": "Male", "Married": "Yes", "Dependents": 0, "Education": "Graduate",
        "Self_Employed": "No", "ApplicantIncome": 5720, "CoapplicantIncome": 0,
        "LoanAmount": 110, "Loan_Amount_Term": 360, "Credit_History": 1,
        "Property_Area": "Urban",
    }]})

    Gender: Literal["Male", "Female"] = Field(
        description='Sexo del solicitante: "Male" o "Female".'
    )
    Married: SiNo = Field(description='Casado: "Yes" o "No".')
    Dependents: int = Field(ge=0, le=3, description="Cantidad de dependientes (3 = 3 o más).")
    Education: Literal["Graduate", "Not Graduate"] = Field(
        description='Educación: "Graduate" (graduado) o "Not Graduate" (no graduado).'
    )
    Self_Employed: SiNo = Field(description='Trabaja por cuenta propia: "Yes" o "No".')
    ApplicantIncome: float = Field(
        ge=0, le=100000, description="Ingreso mensual del solicitante, en dólares (USD)."
    )
    CoapplicantIncome: float = Field(
        ge=0, le=100000, description="Ingreso mensual del codeudor, en dólares (USD); 0 si no hay."
    )
    LoanAmount: float = Field(
        gt=0, le=1000, description="Monto del préstamo, en miles de dólares (USD)."
    )
    Loan_Amount_Term: float = Field(gt=0, le=480, description="Plazo del préstamo, en meses.")
    Credit_History: Binary = Field(
        description="Historial crediticio que cumple las pautas: 1 = sí, 0 = no."
    )
    Property_Area: Literal["Urban", "Semiurban", "Rural"] = Field(
        description='Zona de la propiedad: "Urban", "Semiurban" o "Rural".'
    )


class M03Metrica(BaseModel):
    """Métricas del clasificador de rechazo obtenidas sobre el conjunto de prueba."""

    Accuracy: float = Field(description="Proporción de solicitudes clasificadas correctamente.")
    Precision: float = Field(description="De las clasificadas como rechazo, cuántas lo son.")
    Recall: float = Field(description="De los rechazos reales, cuántos detecta el modelo.")
    F1: float = Field(description="Media armónica entre Precision y Recall.")


class M03Output(BaseModel):
    """Contrato de respuesta común: fecha, hora, modelo, predicción, métrica e id_ejecucion."""

    id_ejecucion: str = Field(description="Identificador único (UUID v4) de la ejecución.")
    fecha: str = Field(description="Fecha de la ejecución (AAAA-MM-DD).")
    hora: str = Field(description="Hora de la ejecución (HH:MM:SS).")
    modelo: str = Field(description='Identificador del modelo ("M03").')
    prediccion: Literal["bajo", "medio", "alto"] = Field(description="Nivel de riesgo predicho.")
    etiqueta: str = Field(description='Nivel de riesgo en texto (por ejemplo "Riesgo bajo").')
    probabilidad: float = Field(
        description="Probabilidad estimada de rechazo (0 a 1), con 4 decimales."
    )
    descripcion_probabilidad: str = Field(description="Qué representa el campo probabilidad.")
    metrica: M03Metrica = Field(description="Métricas del modelo sobre el conjunto de prueba.")


@lru_cache(maxsize=1)
def load_m03_artifact() -> dict:
    """Carga (una sola vez) el artefacto entrenado del modelo M03."""
    model_path = Path(os.environ.get("M03_MODEL_PATH", DEFAULT_MODEL_PATH))
    if not model_path.exists():
        raise FileNotFoundError(f"No se encontró el artefacto del modelo en: {model_path}")
    return joblib.load(model_path)


def nivel_riesgo(probabilidad: float, cortes: dict) -> str:
    """Convierte la probabilidad de rechazo en bajo, medio o alto (cortes del entrenamiento)."""
    if probabilidad < cortes["medio"]:
        return "bajo"
    if probabilidad < cortes["alto"]:
        return "medio"
    return "alto"


def predict(payload: M03Input) -> M03Output:
    """Clasifica el nivel de riesgo de morosidad de una solicitud de préstamo."""
    artifact = load_m03_artifact()
    features = pd.DataFrame([payload.model_dump()])[artifact["feature_names"]]
    # En el entrenamiento Credit_History es decimal (0.0 / 1.0)
    features["Credit_History"] = features["Credit_History"].astype(float)
    probability = float(artifact["pipeline"].predict_proba(features)[0][1])
    nivel = nivel_riesgo(probability, artifact["cortes"])

    now = datetime.now()
    return M03Output(
        id_ejecucion=str(uuid.uuid4()),
        fecha=now.strftime("%Y-%m-%d"),
        hora=now.strftime("%H:%M:%S"),
        modelo="M03",
        prediccion=nivel,
        etiqueta=f"Riesgo {nivel}",
        probabilidad=round(probability, 4),
        descripcion_probabilidad="Probabilidad de rechazo",
        metrica=M03Metrica(**{NOMBRES_METRICAS[k]: v for k, v in artifact["metrics"].items()}),
    )
