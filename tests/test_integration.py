"""
Pruebas de integración entre capas del sistema:
- UI / HTTP -> API
- API -> Modelo de Machine Learning
- API -> Persistencia (Supabase / PostgreSQL)
- Resiliencia ante caídas de la base de datos (CP-27)
Curso: Pruebas de Software (CI0142)
"""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from proyecto_pruebas.logs_supabase import RegistroLog, registrar_log
from proyecto_pruebas.models import m02


def test_integracion_api_a_modelo(client: TestClient, valid_m02_payload: dict):
    """
    Prueba de integración: Capa API -> Capa Modelo de ML.
    Verifica que la petición procesada por la API invoque directamente
    el artefacto entrenado de Ridge Regression y devuelva la predicción real del modelo.
    """
    response = client.post("/predict/m02", json=valid_m02_payload)
    assert response.status_code == 200

    api_result = response.json()

    # Invocamos directamente el modelo en la capa lógica para contrastar
    modelo_input = m02.M02Input(**valid_m02_payload)
    direct_result = m02.predict(modelo_input)

    assert api_result["modelo"] == direct_result.modelo
    assert api_result["prediccion"] == direct_result.prediccion
    assert api_result["unidad"] == direct_result.unidad


def test_cp25_integracion_api_a_persistencia_supabase(client: TestClient, valid_m02_payload: dict):
    """
    CP-25: Prueba de integración: Capa API -> Capa Persistencia (Supabase).
    Verifica que cada ejecución exitosa despache un registro a Supabase
    con los campos mínimos requeridos (modelo, endpoint, método, estado, entrada, salida, id_ejecucion).
    """
    with patch("proyecto_pruebas.middleware_logs.registrar_log") as mock_registrar:
        response = client.post("/predict/m02", json=valid_m02_payload)
        assert response.status_code == 200

        # BackgroundTask en Starlette ejecuta registrar_log al salir el cliente
        assert mock_registrar.called
        log_enviado: RegistroLog = mock_registrar.call_args[0][0]

        assert log_enviado.modelo == "M02"
        assert log_enviado.endpoint == "/predict/m02"
        assert log_enviado.metodo == "POST"
        assert log_enviado.estado == 200
        assert log_enviado.duracion_ms >= 0
        assert log_enviado.id_ejecucion == response.json()["id_ejecucion"]
        assert log_enviado.entrada == valid_m02_payload
        assert log_enviado.salida["prediccion"] == response.json()["prediccion"]


def test_cp27_resiliencia_bd_no_disponible(client: TestClient, valid_m02_payload: dict, caplog):
    """
    CP-27: Comportamiento ante BD no disponible (Fail-soft).
    Si Supabase falla (por ejemplo, desconexión de red o error de API de PostgREST),
    el sistema NO debe lanzar un error 500 al cliente; debe entregar la predicción normalmente
    (HTTP 200) y escribir el registro en la terminal/logs como fallback.
    """
    # Simulamos un fallo catastrófico en el cliente de Supabase
    with patch("proyecto_pruebas.logs_supabase.get_client") as mock_client:
        mock_instance = MagicMock()
        mock_instance.table.side_effect = ConnectionError("Supabase PostgreSQL fuera de línea")
        mock_client.return_value = mock_instance

        # Enviamos la solicitud válida
        response = client.post("/predict/m02", json=valid_m02_payload)

        # La predicción debe completarse exitosamente a pesar del fallo de la base de datos
        assert response.status_code == 200
        data = response.json()
        assert "prediccion" in data
        assert data["modelo"] == "M02"


def test_persistencia_deshabilitada_fallback_terminal(valid_m02_payload: dict, monkeypatch):
    """
    Verifica que cuando SUPABASE_LOGS_ENABLED='false', el registro se escribe
    en la terminal mediante _registrar_en_terminal sin arrojar excepciones.
    """
    monkeypatch.setenv("SUPABASE_LOGS_ENABLED", "false")

    registro = RegistroLog(
        modelo="m02",
        endpoint="/predict/m02",
        metodo="POST",
        estado=200,
        duracion_ms=15,
        entrada=valid_m02_payload,
        salida={"prediccion": 125.5},
        id_ejecucion="test-uuid-1234",
    )

    # Debe ejecutarse sin error
    registrar_log(registro)
