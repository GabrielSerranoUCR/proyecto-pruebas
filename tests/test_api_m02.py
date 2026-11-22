"""
Batería de pruebas automatizadas para la API del Modelo M02 (Presión arterial estimada - Regresión).
Cubre casos funcionales positivos, negativos, análisis de valores límite y robustez.
Curso: Pruebas de Software (CI0142)
"""

import uuid
from fastapi.testclient import TestClient


def test_cp08_predict_m02_exitoso_contrato_completo(client: TestClient, valid_m02_payload: dict):
    """
    CP-08 / CP-20 / CP-21: Solicitud válida a /predict/m02.
    Verifica que responda HTTP 200 y que cumpla estrictamente el contrato:
    - id_ejecucion (UUID válido)
    - fecha (YYYY-MM-DD)
    - hora (HH:MM:SS)
    - modelo == 'M02'
    - prediccion numérica con 2 decimales y en rango fisiológico razonable (80 - 250 mmHg)
    - unidad == 'mmHg'
    - metrica (MAE, RMSE, R2 presentes y numéricos)
    """
    response = client.post("/predict/m02", json=valid_m02_payload)
    assert response.status_code == 200, f"Error inesperado: {response.text}"

    data = response.json()
    assert "id_ejecucion" in data
    uuid.UUID(data["id_ejecucion"])  # Valida que sea un UUID válido

    assert "fecha" in data
    assert "hora" in data
    assert data["modelo"] == "M02"
    assert data["unidad"] == "mmHg"

    # CP-20: Redondeo a exactamente 2 decimales
    pred = data["prediccion"]
    assert isinstance(pred, float)
    assert round(pred, 2) == pred

    # CP-21: Presión en rango fisiológico
    assert 80.0 <= pred <= 250.0

    # Métricas
    metrica = data["metrica"]
    assert "MAE" in metrica and metrica["MAE"] > 0
    assert "RMSE" in metrica and metrica["RMSE"] > 0
    assert "R2" in metrica and 0 < metrica["R2"] <= 1.0

    # Pesos relativos de las variables
    assert "pesos" in data
    assert isinstance(data["pesos"], dict)
    assert len(data["pesos"]) == 13
    assert abs(sum(data["pesos"].values()) - 1.0) < 0.01


def test_cp09_predict_m02_campo_faltante(client: TestClient, valid_m02_payload: dict):
    """
    CP-09: Envío de solicitud con campo obligatorio faltante (totChol).
    Debe responder HTTP 400 con formato estándar de error.
    """
    payload = valid_m02_payload.copy()
    del payload["totChol"]

    response = client.post("/predict/m02", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Parámetro inválido"
    assert data["campo"] == "totChol"
    assert "errores" in data


def test_cp10_predict_m02_tipo_incorrecto_cadena(client: TestClient, valid_m02_payload: dict):
    """
    CP-10: Envío de tipo incorrecto (cadena en campo numérico 'age').
    Debe responder HTTP 400 debido a strict=True en Pydantic.
    """
    payload = valid_m02_payload.copy()
    payload["age"] = "cincuenta"

    response = client.post("/predict/m02", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Parámetro inválido"
    assert data["campo"] == "age"


def test_cp11_predict_m02_tipo_incorrecto_booleano_en_entero(client: TestClient, valid_m02_payload: dict):
    """
    CP-11: Envío de booleano True en lugar de entero 1 en 'male'.
    Con strict=True en Pydantic no se permite coerción de boolean a int.
    """
    payload = valid_m02_payload.copy()
    payload["male"] = True

    response = client.post("/predict/m02", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Parámetro inválido"
    assert data["campo"] == "male"


def test_cp12_predict_m02_campo_adicional_no_permitido(client: TestClient, valid_m02_payload: dict):
    """
    Validación de contrato estricto: campos desconocidos o adicionales no permitidos (extra='forbid').
    """
    payload = valid_m02_payload.copy()
    payload["campo_extra_no_valido"] = 12345

    response = client.post("/predict/m02", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Parámetro inválido"
    assert data["campo"] == "campo_extra_no_valido"


def test_cp13_predict_m02_json_mal_formado(client: TestClient):
    """
    CP-13: Envío de cuerpo de solicitud con sintaxis JSON inválida.
    Debe retornar HTTP 400 con error 'JSON mal formado'.
    """
    cuerpo_invalido = '{"male": 1, "age": 50, "totChol": }'
    response = client.post(
        "/predict/m02",
        content=cuerpo_invalido,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "JSON mal formado"


# --- Pruebas de Análisis de Valores Límite (BVA) ---

def test_bva_m02_edad_limites_exactos(client: TestClient, valid_m02_payload: dict):
    """
    Análisis de valores límite para 'age' (rango válido: 1 a 120 años).
    Límite inferior exacto: 1 -> Válido (200)
    Límite superior exacto: 120 -> Válido (200)
    """
    # Límite inferior
    payload_inf = valid_m02_payload.copy()
    payload_inf["age"] = 1
    res_inf = client.post("/predict/m02", json=payload_inf)
    assert res_inf.status_code == 200

    # Límite superior
    payload_sup = valid_m02_payload.copy()
    payload_sup["age"] = 120
    res_sup = client.post("/predict/m02", json=payload_sup)
    assert res_sup.status_code == 200


def test_cp06_cp07_bva_m02_edad_fuera_de_limites(client: TestClient, valid_m02_payload: dict):
    """
    CP-06 y CP-07: Valores inmediatamente fuera de los límites de 'age'.
    Justo debajo del límite inferior: age = 0 -> 400
    Justo encima del límite superior: age = 121 -> 400
    Valor negativo: age = -5 -> 400
    """
    # Justo debajo
    p0 = valid_m02_payload.copy()
    p0["age"] = 0
    assert client.post("/predict/m02", json=p0).status_code == 400

    # Negativo
    p_neg = valid_m02_payload.copy()
    p_neg["age"] = -5
    assert client.post("/predict/m02", json=p_neg).status_code == 400

    # Justo encima
    p121 = valid_m02_payload.copy()
    p121["age"] = 121
    assert client.post("/predict/m02", json=p121).status_code == 400


def test_bva_m02_cigs_per_day_limites(client: TestClient, valid_m02_payload: dict):
    """
    Análisis de valores límite para cigsPerDay (rango válido: 0 a 100).
    """
    # 0 (no fumador)
    p0 = valid_m02_payload.copy()
    p0["currentSmoker"] = 0
    p0["cigsPerDay"] = 0.0
    assert client.post("/predict/m02", json=p0).status_code == 200

    # 100 (límite superior)
    p100 = valid_m02_payload.copy()
    p100["cigsPerDay"] = 100.0
    assert client.post("/predict/m02", json=p100).status_code == 200

    # -1 (inválido)
    p_inv = valid_m02_payload.copy()
    p_inv["cigsPerDay"] = -1.0
    assert client.post("/predict/m02", json=p_inv).status_code == 400

    # 101 (inválido)
    p_sup = valid_m02_payload.copy()
    p_sup["cigsPerDay"] = 101.0
    assert client.post("/predict/m02", json=p_sup).status_code == 400


def test_cp24_predict_m02_valores_clinicos_extremos(client: TestClient, valid_m02_payload: dict):
    """
    CP-24: Robustez ante combinaciones de parámetros clínicos mínimos o extremos válidos.
    Verifica que no se produzca excepción 500.
    """
    payload_min = valid_m02_payload.copy()
    payload_min.update({
        "male": 0,
        "age": 18,
        "education": 1,
        "currentSmoker": 0,
        "cigsPerDay": 0.0,
        "BPMeds": 0,
        "prevalentStroke": 0,
        "prevalentHyp": 0,
        "diabetes": 0,
        "totChol": 100.0,
        "BMI": 15.0,
        "heartRate": 45.0,
        "glucose": 50.0,
    })
    res_min = client.post("/predict/m02", json=payload_min)
    assert res_min.status_code == 200
    assert 80.0 <= res_min.json()["prediccion"] <= 250.0
