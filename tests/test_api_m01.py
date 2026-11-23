"""
Batería de pruebas automatizadas para la API del Modelo M01
(Aprobación del curso - Clasificación binaria).
Cubre casos funcionales positivos, negativos y análisis de límites.
Curso: Pruebas de Software (CI0142)
"""

import uuid
from fastapi.testclient import TestClient


def test_cp18_predict_m01_exitoso_caso_aprobacion(client: TestClient, valid_m01_payload: dict):
    """
    CP-18: Solicitud válida con perfil de estudiante de alto rendimiento.
    Debe retornar HTTP 200, prediccion binaria (0 o 1), probabilidad entre 0 y 1,
    y métricas (Accuracy, Precision, Recall, F1).
    """
    payload = valid_m01_payload.copy()
    payload.update({
        "failures": 0,
        "absences": 1,
        "freetime": 2,
        "Dalc": 1,
        "higher": 1,
    })
    response = client.post("/predict/m01", json=payload)
    assert response.status_code == 200, f"Error: {response.text}"

    data = response.json()
    assert "id_ejecucion" in data
    uuid.UUID(data["id_ejecucion"])
    assert data["modelo"] == "M01"
    assert data["prediccion"] in (0, 1)
    assert data["etiqueta"] in ("Aprueba", "No aprueba")
    assert 0.0 <= data["probabilidad"] <= 1.0

    metrica = data["metrica"]
    for k in ("Accuracy", "Precision", "Recall", "F1"):
        assert k in metrica
        assert 0.0 <= metrica[k] <= 1.0

    assert "pesos" in data
    assert isinstance(data["pesos"], dict)
    assert len(data["pesos"]) == 17
    assert abs(sum(data["pesos"].values()) - 1.0) < 0.01


def test_cp19_predict_m01_caso_bajo_rendimiento(client: TestClient, valid_m01_payload: dict):
    """
    CP-19: Solicitud con perfil de estudiante de bajo rendimiento (muchas fallas y ausencias).
    """
    payload = valid_m01_payload.copy()
    payload.update({
        "failures": 3,
        "absences": 40,
        "Dalc": 5,
        "higher": 2,
    })
    response = client.post("/predict/m01", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediccion"] in (0, 1)


def test_m01_campo_faltante(client: TestClient, valid_m01_payload: dict):
    """Envío de solicitud M01 sin el campo 'sex'."""
    payload = valid_m01_payload.copy()
    del payload["sex"]
    response = client.post("/predict/m01", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Parámetro inválido"
    assert data["campo"] == "sex"


def test_m01_edad_fuera_de_rango(client: TestClient, valid_m01_payload: dict):
    """Edad fuera de rango para M01 (permite 15 a 22 años)."""
    # 14 años (menor)
    p14 = valid_m01_payload.copy()
    p14["age"] = 14
    assert client.post("/predict/m01", json=p14).status_code == 400

    # 23 años (mayor)
    p23 = valid_m01_payload.copy()
    p23["age"] = 23
    assert client.post("/predict/m01", json=p23).status_code == 400


def test_m01_bva_ausencias(client: TestClient, valid_m01_payload: dict):
    """Límites de ausencias (0 a 93)."""
    # 0 ausencias (límite inferior)
    p0 = valid_m01_payload.copy()
    p0["absences"] = 0
    assert client.post("/predict/m01", json=p0).status_code == 200

    # 93 ausencias (límite superior)
    p93 = valid_m01_payload.copy()
    p93["absences"] = 93
    assert client.post("/predict/m01", json=p93).status_code == 200

    # -1 ausencias (inválido)
    p_neg = valid_m01_payload.copy()
    p_neg["absences"] = -1
    assert client.post("/predict/m01", json=p_neg).status_code == 400

    # 94 ausencias (inválido)
    p94 = valid_m01_payload.copy()
    p94["absences"] = 94
    assert client.post("/predict/m01", json=p94).status_code == 400
