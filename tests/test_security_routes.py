"""
Pruebas de seguridad de rutas, manejo de códigos de estado HTTP y no divulgación de información sensible.
Curso: Pruebas de Software (CI0142)
"""

from unittest.mock import patch
from fastapi.testclient import TestClient

from proyecto_pruebas.app import app


def test_cp14_ruta_o_modelo_inexistente_retorna_404(client: TestClient):
    """
    CP-14: Solicitud a una ruta no definida o modelo inexistente.
    Debe retornar HTTP 404 con formato JSON estandarizado sin stack traces.
    """
    response = client.get("/ruta/totalmente/inexistente")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Ruta no encontrada"


def test_cp15_metodo_no_permitido_retorna_405(client: TestClient):
    """
    CP-15: Solicitud con método HTTP no soportado (GET en lugar de POST en /predict/m02).
    Debe responder HTTP 405.
    """
    response = client.get("/predict/m02")
    assert response.status_code == 405
    data = response.json()
    assert data["error"] == "Método no permitido"


def test_cp17_no_divulgacion_de_informacion_en_error_500(valid_m02_payload: dict):
    """
    CP-17: Seguridad de manejo de errores.
    Ante un fallo interno no controlado (error 500), la API NO debe revelar stack traces,
    rutas absolutas de archivos del servidor, ni variables de entorno o credenciales.
    """
    # Usamos raise_server_exceptions=False para capturar la respuesta HTTP 500 real del servidor
    with TestClient(app, raise_server_exceptions=False) as no_raise_client:
        with patch("proyecto_pruebas.models.m02.predict", side_effect=RuntimeError("Fallo interno simulado")):
            response = no_raise_client.post("/predict/m02", json=valid_m02_payload)
            assert response.status_code == 500

            data = response.json()
            assert data["error"] == "Error interno del servidor"
            # Verifica que la respuesta no filtre detalles de archivos ni el mensaje de excepción crudo
            assert "Traceback" not in response.text
            assert "Fallo interno simulado" not in response.text
            assert "/home/" not in response.text
