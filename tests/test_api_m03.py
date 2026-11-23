"""
Batería de pruebas automatizadas para la API del Modelo M03
(Riesgo de morosidad - Clasificación multiclase).
Cubre casos funcionales positivos para cada clase (bajo, medio, alto), negativos, valores extremos y
verificación de exclusión de la variable dominante Credit_History.
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
    - pesos relativos de las 10 variables (sin Credit_History) que sumen 1.0
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

    assert "pesos" in data
    assert isinstance(data["pesos"], dict)
    assert len(data["pesos"]) == 10
    assert "Credit_History" not in data["pesos"]
    assert abs(sum(data["pesos"].values()) - 1.0) < 0.01


def test_cp22a_cp22b_cp22c_tres_clases_alcanzables(client: TestClient):
    """
    CP-22a, CP-22b y CP-22c: Verifica que las tres clases de riesgo ('bajo', 'medio', 'alto')
    sean alcanzables a partir del perfil socioeconómico y financiero (sin Credit_History).
    """
    # CP-22a: Perfil de riesgo bajo (graduado, casado, semiurbana, buen ingreso, préstamo moderado)
    perfil_bajo = {
        "Gender": "Male", "Married": "Yes", "Dependents": 0, "Education": "Graduate",
        "Self_Employed": "No", "ApplicantIncome": 8000.0, "CoapplicantIncome": 3000.0,
        "LoanAmount": 80.0, "Loan_Amount_Term": 360.0, "Property_Area": "Semiurban",
    }
    res_bajo = client.post("/predict/m03", json=perfil_bajo)
    assert res_bajo.status_code == 200
    assert res_bajo.json()["prediccion"] == "bajo"

    # CP-22b: Perfil de riesgo medio (urbana, ingreso medio, sin codeudor)
    perfil_medio = {
        "Gender": "Male", "Married": "Yes", "Dependents": 1, "Education": "Graduate",
        "Self_Employed": "No", "ApplicantIncome": 4000.0, "CoapplicantIncome": 0.0,
        "LoanAmount": 130.0, "Loan_Amount_Term": 360.0, "Property_Area": "Urban",
    }
    res_medio = client.post("/predict/m03", json=perfil_medio)
    assert res_medio.status_code == 200
    assert res_medio.json()["prediccion"] == "medio"

    # CP-22c: Perfil de riesgo alto (no graduado, soltero, rural, ingreso bajo y monto alto)
    perfil_alto = {
        "Gender": "Female", "Married": "No", "Dependents": 3, "Education": "Not Graduate",
        "Self_Employed": "Yes", "ApplicantIncome": 1500.0, "CoapplicantIncome": 0.0,
        "LoanAmount": 450.0, "Loan_Amount_Term": 180.0, "Property_Area": "Rural",
    }
    res_alto = client.post("/predict/m03", json=perfil_alto)
    assert res_alto.status_code == 200
    assert res_alto.json()["prediccion"] == "alto"


def test_m03_credit_history_rechazada_por_dominancia(client: TestClient, valid_m03_payload: dict):
    """
    Verifica que Credit_History (descartada por acaparar la predicción) sea rechazada
    con HTTP 400 ('Campo no permitido') si se envía en el cuerpo JSON.
    """
    payload = valid_m03_payload.copy()
    payload["Credit_History"] = 1
    response = client.post("/predict/m03", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Parámetro inválido"
    assert data["campo"] == "Credit_History"


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
