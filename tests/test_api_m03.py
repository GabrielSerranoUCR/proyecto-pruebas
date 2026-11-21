"""
Batería de pruebas automatizadas para la API del Modelo M03 (Riesgo de morosidad - Clasificación multiclase).
Cubre casos funcionales positivos para cada clase, negativos y valores extremos.
Curso: Pruebas de Software (CI0142)
"""

import uuid
from fastapi.testclient import TestClient


def test_cp22_predict_m03_exitoso_contrato_completo(client: TestClient, valid_m03_payload: dict):
    """
    CP-22: Solicitud válida a /predict/m03.
    Verifica que responda 200 y que cumpla el contrato de multiclase:
    - prediccion en ('bajo', 'medio', 'alto')
    - probabilidad entre 0 y 1
    - métricas presentes (Accuracy, Precision, Recall, F1)
    """
    response = client.post("/predict/m03", json=valid_m03_payload)
    assert response.status_code == 200, f"Error: {response.text}"

    data = response.json()
    assert "id_ejecucion" in data
    uuid.UUID(data["id_ejecucion"])
    assert data["modelo"] == "M03"
    assert data["prediccion"] in ("bajo", "medio", "alto")
    assert 0.0 <= data["probabilidad"] <= 1.0

    metrica = data["metrica"]
    for k in ("Accuracy", "Precision", "Recall", "F1"):
        assert k in metrica
        assert 0.0 <= metrica[k] <= 1.0


def test_cp05_m03_campo_obligatorio_faltante(client: TestClient, valid_m03_payload: dict):
    """
    CP-05: Solicitud sin 'ApplicantIncome'.
    """
    payload = valid_m03_payload.copy()
    del payload["ApplicantIncome"]
    response = client.post("/predict/m03", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Parámetro inválido"
    assert data["campo"] == "ApplicantIncome"


def test_m03_categoria_invalida(client: TestClient, valid_m03_payload: dict):
    """Categoría no permitida para Property_Area ('Suburban' en lugar de Urban/Semiurban/Rural)."""
    payload = valid_m03_payload.copy()
    payload["Property_Area"] = "Suburban"
    response = client.post("/predict/m03", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Parámetro inválido"
    assert data["campo"] == "Property_Area"


def test_cp23_m03_valor_extremo_ingreso(client: TestClient, valid_m03_payload: dict):
    """
    CP-23: Robustez con ingreso muy alto (límite superior permitido: 100,000 USD).
    No debe provocar un error 500.
    """
    payload = valid_m03_payload.copy()
    payload["ApplicantIncome"] = 100000.0
    payload["Credit_History"] = 1
    response = client.post("/predict/m03", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediccion"] in ("bajo", "medio", "alto")


def test_m03_ingreso_negativo_invalido(client: TestClient, valid_m03_payload: dict):
    """Ingreso negativo rechazado."""
    payload = valid_m03_payload.copy()
    payload["ApplicantIncome"] = -500.0
    response = client.post("/predict/m03", json=payload)
    assert response.status_code == 400
