import os
import joblib
import numpy as np
import pandas as pd
import pytest

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "training", "models", "m02_presion_arterial.joblib")

@pytest.fixture(scope="module")
def model_artifact():
    """Carga el artefacto del modelo entrenado M02."""
    assert os.path.exists(MODEL_PATH), f"El artefacto del modelo no existe en {MODEL_PATH}"
    artifact = joblib.load(MODEL_PATH)
    return artifact

@pytest.fixture
def sample_valid_input():
    """Muestra de paciente con valores típicos."""
    return pd.DataFrame([{
        "male": 1,
        "age": 45,
        "education": 3,
        "currentSmoker": 0,
        "cigsPerDay": 0,
        "BPMeds": 0,
        "prevalentStroke": 0,
        "prevalentHyp": 0,
        "diabetes": 0,
        "totChol": 210,
        "BMI": 25.0,
        "heartRate": 72,
        "glucose": 85,
    }])

def test_model_artifact_structure(model_artifact):
    """Verifica que el artefacto contenga las claves requeridas y metadatos."""
    assert "pipeline" in model_artifact
    assert "feature_names" in model_artifact
    assert "metrics" in model_artifact
    assert model_artifact["model_id"] == "M02"
    assert len(model_artifact["feature_names"]) == 13

def test_model_prediction_shape_and_type(model_artifact, sample_valid_input):
    """Verifica que la salida de la predicción sea un valor numérico flotante."""
    pipeline = model_artifact["pipeline"]
    prediction = pipeline.predict(sample_valid_input)
    assert isinstance(prediction, np.ndarray)
    assert len(prediction) == 1
    assert isinstance(float(prediction[0]), float)

def test_model_prediction_plausibility(model_artifact, sample_valid_input):
    """Verifica que la presión arterial estimada esté en un rango fisiológico verosímil."""
    pipeline = model_artifact["pipeline"]
    pred = float(pipeline.predict(sample_valid_input)[0])
    # La presión sistólica humana típica oscila entre 80 mmHg y 250 mmHg
    assert 80.0 <= pred <= 250.0, f"Predicción fuera de rango plausible: {pred} mmHg"

def test_model_quality_metrics(model_artifact):
    """Verifica que el modelo cumpla con umbrales mínimos de calidad de regresión."""
    metrics = model_artifact["metrics"]
    assert metrics["R2 Test"] > 0.40, f"R2 por debajo del umbral mínimo: {metrics['R2 Test']}"
    assert metrics["RMSE (mmHg)"] < 20.0, f"RMSE superior al umbral admisible: {metrics['RMSE (mmHg)']}"

def test_model_imputation_robustness(model_artifact):
    """Prueba de robustez: el pipeline debe manejar valores nulos sin caerse."""
    pipeline = model_artifact["pipeline"]
    input_with_nans = pd.DataFrame([{
        "male": 0,
        "age": 50,
        "education": np.nan,
        "currentSmoker": 0,
        "cigsPerDay": np.nan,
        "BPMeds": np.nan,
        "prevalentStroke": 0,
        "prevalentHyp": 0,
        "diabetes": 0,
        "totChol": np.nan,
        "BMI": np.nan,
        "heartRate": np.nan,
        "glucose": np.nan,
    }])
    pred = pipeline.predict(input_with_nans)
    assert len(pred) == 1
    assert not np.isnan(pred[0])
