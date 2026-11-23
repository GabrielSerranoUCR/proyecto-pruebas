"""Evaluacion predictiva de cada modelo con sus datos de prueba CSV."""

# Pytest fixtures are injected as function arguments.
# pylint: disable=redefined-outer-name

import os
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)

from proyecto_pruebas.app import app
from proyecto_pruebas.models import m03

DATA_DIR = Path(__file__).resolve().parents[1] / "training" / "data" / "clean"
M01_CSV = DATA_DIR / "m01" / "1_curso" / "test_data.csv"
M02_CSV = DATA_DIR / "m02" / "1_curso" / "test_data.csv"
M03_CSV = DATA_DIR / "m03" / "1_curso" / "test_data.csv"


@dataclass(frozen=True)
class Prediction:
    """Respuesta obtenida para una fila del conjunto de evaluación."""

    actual: int | float
    status_code: int | None
    response: dict | None
    skip_reason: str | None = None

def _record_ids(csv_path: Path) -> list[str]:
    return [f"registro_{index + 1}" for index in range(len(pd.read_csv(csv_path)))]

def _report_classification(
    model_name: str,
    actual: list[int],
    predicted: list[int],
    incorrect_records: list[str],
) -> None:
    metrics = {
        "Accuracy": accuracy_score(actual, predicted),
        "Precision": precision_score(actual, predicted, zero_division=0),
        "Recall": recall_score(actual, predicted, zero_division=0),
        "F1-score": f1_score(actual, predicted, zero_division=0),
    }
    matrix = confusion_matrix(actual, predicted, labels=[0, 1])
    print(f"\n{model_name} ({len(actual)} registros): {metrics}")
    print(f"Matriz de confusion [0, 1]=\n{matrix}")
    print(f"Registros incorrectos: {incorrect_records}")

@pytest.fixture(scope="module")
def client():
    """Cliente HTTP compartido; evita efectos de logging externos."""
    with patch("proyecto_pruebas.middleware_logs.registrar_log"):
        with TestClient(app) as test_client:
            yield test_client

@pytest.fixture(scope="module")
def m01_test_data() -> pd.DataFrame:
    """CSV de evaluación del modelo de aprobación de curso."""
    return pd.read_csv(M01_CSV)

@pytest.fixture(scope="module")
def m02_test_data() -> pd.DataFrame:
    """CSV de evaluación del modelo de presión arterial."""
    return pd.read_csv(M02_CSV)

@pytest.fixture(scope="module")
def m03_test_data() -> pd.DataFrame:
    """CSV de evaluación del modelo de riesgo de morosidad."""
    return pd.read_csv(M03_CSV)

@pytest.fixture(scope="module")
def m01_predictions(client: TestClient, m01_test_data: pd.DataFrame) -> list[Prediction]:
    """Obtiene una vez las predicciones M01 para reutilizarlas en sus tests."""
    edades_representativas = {1: 15, 2: 17, 3: 18, 4: 19}
    predictions = []

    for _, row in m01_test_data.iterrows():
        expected = int(row["Aprobado"])
        payload = row.drop(labels="Aprobado").to_dict()
        edad_categoria = int(payload["age"])
        assert edad_categoria in edades_representativas
        payload["age"] = edades_representativas[edad_categoria]
        payload = {name: int(value) for name, value in payload.items()}
        assert "Aprobado" not in payload

        response = client.post("/predict/m01", json=payload)
        predictions.append(Prediction(
            actual=expected,
            status_code=response.status_code,
            response=response.json(),
        ))

    return predictions

@pytest.fixture(scope="module")
def m02_predictions(client: TestClient, m02_test_data: pd.DataFrame) -> list[Prediction]:
    """Obtiene una vez las predicciones M02 para reutilizarlas en sus tests."""
    feature_columns = [
        "male", "age", "education", "currentSmoker", "cigsPerDay", "BPMeds",
        "prevalentStroke", "prevalentHyp", "diabetes", "totChol", "BMI",
        "heartRate", "glucose",
    ]
    integer_columns = {
        "male", "age", "education", "currentSmoker", "BPMeds", "prevalentStroke",
        "prevalentHyp", "diabetes",
    }
    predictions = []

    for _, row in m02_test_data.iterrows():
        expected = float(row["sysBP"])
        payload = {
            column: int(row[column]) if column in integer_columns else float(row[column])
            for column in feature_columns
        }
        assert "sysBP" not in payload

        response = client.post("/predict/m02", json=payload)
        predictions.append(Prediction(
            actual=expected,
            status_code=response.status_code,
            response=response.json(),
        ))

    return predictions

@pytest.fixture(scope="module")
def m03_predictions(client: TestClient, m03_test_data: pd.DataFrame) -> list[Prediction]:
    """Obtiene una vez las predicciones M03 y conserva el tratamiento de filas incompletas."""
    model_path = Path(os.environ.get("M03_MODEL_PATH", m03.DEFAULT_MODEL_PATH))
    if not model_path.is_file():
        pytest.skip(f"No se encontro el artefacto del modelo M03: {model_path}")

    feature_columns = [
        "Gender", "Married", "Dependents", "Education", "Self_Employed",
        "ApplicantIncome", "CoapplicantIncome", "LoanAmount",
        "Loan_Amount_Term", "Property_Area",
    ]
    numeric_columns = (
        "ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term",
    )
    predictions = []

    for _, row in m03_test_data.iterrows():
        expected = int(row["rechazo"])
        if row[feature_columns].isna().any():
            predictions.append(Prediction(
                actual=expected,
                status_code=None,
                response=None,
                skip_reason="Registro incompleto; la API no acepta valores nulos.",
            ))
            continue

        payload = {column: row[column] for column in feature_columns}
        payload["Dependents"] = int(payload["Dependents"])
        for column in numeric_columns:
            payload[column] = float(payload[column])
        assert "rechazo" not in payload

        response = client.post("/predict/m03", json=payload)
        predictions.append(Prediction(
            actual=expected,
            status_code=response.status_code,
            response=response.json(),
        ))

    return predictions

@pytest.mark.parametrize(
    "record_index",
    range(len(pd.read_csv(M01_CSV))),
    ids=_record_ids(M01_CSV),
)
def test_m01_prediccion_individual(
    m01_predictions: list[Prediction],
    record_index: int,
) -> None:
    """Compara la predicción de aprobación con la etiqueta de cada registro."""
    result = m01_predictions[record_index]
    record_id = f"M01 registro {record_index + 1}"

    assert result.status_code == 200, (
        f"{record_id}: HTTP {result.status_code}, respuesta={result.response}"
    )
    assert result.response is not None
    assert "prediccion" in result.response, f"{record_id}: falta la predicción"
    assert result.response["modelo"] == "M01", f"{record_id}: modelo inesperado"
    assert result.response["prediccion"] in (0, 1), f"{record_id}: clase inválida"
    assert result.response["prediccion"] == result.actual, (
        f"{record_id}: real={result.actual}, predicho={result.response['prediccion']}"
    )

def test_m01_metricas_globales(m01_predictions: list[Prediction]) -> None:
    """Calcula métricas binarias M01 con las respuestas individuales ya obtenidas."""
    for record_index, result in enumerate(m01_predictions):
        assert result.status_code == 200, (
            f"M01 registro {record_index + 1}: HTTP {result.status_code}"
        )
        assert result.response is not None

    actual = [int(result.actual) for result in m01_predictions]
    predicted = [int(result.response["prediccion"]) for result in m01_predictions]
    incorrect_records = [
        f"registro_{index + 1}"
        for index, (expected, prediction) in enumerate(zip(actual, predicted))
        if expected != prediction
    ]
    _report_classification("M01", actual, predicted, incorrect_records)

@pytest.mark.parametrize(
    "record_index",
    range(len(pd.read_csv(M02_CSV))),
    ids=_record_ids(M02_CSV),
)
def test_m02_prediccion_individual(
    m02_predictions: list[Prediction],
    record_index: int,
) -> None:
    """Comprueba que cada predicción de presión arterial sea válida y finita."""
    result = m02_predictions[record_index]
    record_id = f"M02 registro {record_index + 1}"

    assert result.status_code == 200, (
        f"{record_id}: HTTP {result.status_code}, respuesta={result.response}"
    )
    assert result.response is not None
    assert "prediccion" in result.response, f"{record_id}: falta la predicción"
    assert result.response["modelo"] == "M02", f"{record_id}: modelo inesperado"
    assert np.isfinite(result.response["prediccion"]), f"{record_id}: predicción no finita"

def test_m02_metricas_globales(m02_predictions: list[Prediction]) -> None:
    """Calcula métricas de regresión M02 con las predicciones reutilizadas."""
    for record_index, result in enumerate(m02_predictions):
        assert result.status_code == 200, (
            f"M02 registro {record_index + 1}: HTTP {result.status_code}"
        )
        assert result.response is not None

    actual = np.asarray([result.actual for result in m02_predictions])
    predicted = np.asarray([
        float(result.response["prediccion"]) for result in m02_predictions
    ])
    errors = np.abs(actual - predicted)
    metrics = {
        "MAE": mean_absolute_error(actual, predicted),
        "RMSE": float(np.sqrt(mean_squared_error(actual, predicted))),
        "R2": r2_score(actual, predicted),
    }
    print(f"\nM02 ({len(actual)} registros): {metrics}")
    print(f"Error absoluto maximo: {errors.max():.2f} mmHg")

@pytest.mark.parametrize(
    "record_index",
    range(len(pd.read_csv(M03_CSV))),
    ids=_record_ids(M03_CSV),
)
def test_m03_prediccion_individual(
    m03_predictions: list[Prediction],
    record_index: int,
) -> None:
    """Compara la clasificación de rechazo para cada registro completo de M03."""
    result = m03_predictions[record_index]
    record_id = f"M03 registro {record_index + 1}"
    if result.skip_reason:
        pytest.skip(f"{record_id}: {result.skip_reason}")

    assert result.status_code == 200, (
        f"{record_id}: HTTP {result.status_code}, respuesta={result.response}"
    )
    assert result.response is not None
    assert "probabilidad" in result.response, f"{record_id}: falta probabilidad"
    assert result.response["modelo"] == "M03", f"{record_id}: modelo inesperado"
    predicted = int(float(result.response["probabilidad"]) >= 0.5)
    assert predicted == result.actual, (
        f"{record_id}: rechazo real={result.actual}, "
        f"probabilidad={result.response['probabilidad']}, rechazo predicho={predicted}"
    )

def test_m03_metricas_globales(m03_predictions: list[Prediction]) -> None:
    """Calcula métricas M03 con predicciones válidas ya obtenidas."""
    valid_predictions = [
        result for result in m03_predictions if result.skip_reason is None
    ]
    assert valid_predictions, "M03 no tiene registros completos que se puedan evaluar"
    for record_index, result in enumerate(m03_predictions):
        if result.skip_reason:
            continue
        assert result.status_code == 200, (
            f"M03 registro {record_index + 1}: HTTP {result.status_code}"
        )
        assert result.response is not None

    actual = [int(result.actual) for result in valid_predictions]
    predicted = [
        int(float(result.response["probabilidad"]) >= 0.5)
        for result in valid_predictions
    ]
    incorrect_records = [
        f"registro_{index + 1}"
        for index, result in enumerate(m03_predictions)
        if result.skip_reason is None
        and int(result.response["probabilidad"] >= 0.5) != int(result.actual)
    ]
    _report_classification("M03", actual, predicted, incorrect_records)
    skipped_records = [
        f"registro_{index + 1}"
        for index, result in enumerate(m03_predictions)
        if result.skip_reason is not None
    ]
    if skipped_records:
        print(f"M03 registros omitidos por datos faltantes: {skipped_records}")
