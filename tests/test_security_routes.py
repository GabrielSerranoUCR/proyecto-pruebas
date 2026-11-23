"""
Pruebas de seguridad de rutas, manejo de códigos de estado HTTP
y no divulgación de información sensible.
Curso: Pruebas de Software (CI0142)
"""

from unittest.mock import MagicMock, patch

import pytest
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


@pytest.mark.parametrize(
    ("ruta", "campo", "valor"),
    [
        ("/predict/m02", "age", "35; DROP TABLE usuarios;"),
        ("/predict/m03", "ApplicantIncome", "1 OR 1=1; DELETE FROM logs_m03;--"),
        ("/predict/m03", "Property_Area", "Urban'; DROP TABLE logs_m03;--"),
    ],
)
def test_cp16_entrada_maliciosa_rechazada_sin_efectos_en_bd(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    client: TestClient,
    valid_m02_payload: dict,
    valid_m03_payload: dict,
    ruta: str,
    campo: str,
    valor: str,
):
    """
    CP-16: Entrada maliciosa (inyección SQL) en campos numéricos y categóricos.
    La API debe rechazarla con HTTP 400 indicando el campo, sin invocar el modelo,
    y la única operación sobre la BD debe ser la inserción parametrizada del log
    (el texto malicioso viaja como dato, nunca como sentencia SQL).
    """
    payload = dict(valid_m02_payload if ruta.endswith("m02") else valid_m03_payload)
    payload[campo] = valor
    modulo = "m02" if ruta.endswith("m02") else "m03"

    cliente_bd = MagicMock()
    with patch("proyecto_pruebas.logs_supabase.logs_habilitados", return_value=True), \
         patch("proyecto_pruebas.logs_supabase.get_client", return_value=cliente_bd), \
         patch(f"proyecto_pruebas.models.{modulo}.predict") as predict:
        response = client.post(ruta, json=payload)

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Parámetro inválido"
    assert data["campo"] == campo
    assert "prediccion" not in data
    predict.assert_not_called()

    # Solo se usa la tabla de logs del modelo y solo mediante insert(...)
    cliente_bd.table.assert_called_once_with(f"logs_{modulo}")
    tabla = cliente_bd.table.return_value
    tabla.insert.assert_called_once()
    fila = tabla.insert.call_args.args[0]
    assert fila["estado"] == 400
    assert fila["entrada"][campo] == valor
    for operacion in ("delete", "update", "upsert", "rpc"):
        assert not getattr(tabla, operacion).called


def test_cp17_no_divulgacion_de_informacion_en_error_500(valid_m02_payload: dict):
    """
    CP-17: Seguridad de manejo de errores.
    Ante un fallo interno no controlado (error 500), la API NO debe revelar stack traces,
    rutas absolutas de archivos del servidor, ni variables de entorno o credenciales.
    """
    # Usamos raise_server_exceptions=False para capturar la respuesta HTTP 500 real del servidor
    with TestClient(app, raise_server_exceptions=False) as no_raise_client:
        fallo = RuntimeError("Fallo interno simulado")
        with patch("proyecto_pruebas.models.m02.predict", side_effect=fallo):
            response = no_raise_client.post("/predict/m02", json=valid_m02_payload)
            assert response.status_code == 500

            data = response.json()
            assert data["error"] == "Error interno del servidor"
            # Verifica que la respuesta no filtre detalles de archivos
            # ni el mensaje de excepción crudo
            assert "Traceback" not in response.text
            assert "Fallo interno simulado" not in response.text
            assert "/home/" not in response.text
