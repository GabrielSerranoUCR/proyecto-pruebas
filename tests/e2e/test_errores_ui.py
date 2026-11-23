"""
Capa 3 (test scripts): manejo de errores en la interfaz (respuestas 400/500 de
la API y caída de la conexión). Se intercepta la red para no depender del
backend.
Curso: Pruebas de Software (CI0142)
"""

import json

import pytest
from playwright.sync_api import expect

from .data.payloads import payload_m02

pytestmark = pytest.mark.e2e


def test_muestra_los_errores_de_validacion_de_la_api(flujo):
    """Una respuesta 400 lista cada campo inválido devuelto por la API."""
    formulario = flujo.preparar("m02", payload_m02())

    cuerpo = {
        "error": "Parámetro inválido",
        "campo": "age",
        "detalle": "Debe ser mayor o igual a 1",
        "errores": [{"campo": "age", "detalle": "Debe ser mayor o igual a 1"}],
    }
    flujo.page.route(
        "**/predict/m02",
        lambda ruta: ruta.fulfill(
            status=400,
            content_type="application/json",
            body=json.dumps(cuerpo),
        ),
    )
    formulario.calcular("/predict/m02")

    expect(formulario.error).to_be_visible()
    expect(formulario.cuerpo_resultado).to_contain_text("Parámetro inválido")
    expect(formulario.cuerpo_resultado.locator("li")).to_have_text(
        "age: Debe ser mayor o igual a 1"
    )


def test_muestra_un_error_interno_del_servidor(flujo):
    """Una respuesta 500 muestra el mensaje de error devuelto por la API."""
    formulario = flujo.preparar("m02", payload_m02())
    flujo.page.route(
        "**/predict/m02",
        lambda ruta: ruta.fulfill(
            status=500,
            content_type="application/json",
            body=json.dumps({"error": "Error interno del servidor"}),
        ),
    )
    formulario.calcular("/predict/m02")

    expect(formulario.error).to_be_visible()
    expect(formulario.cuerpo_resultado).to_contain_text("Error interno del servidor")


def test_avisa_cuando_no_hay_conexion_con_la_api(flujo):
    """Si la petición falla en la red, la interfaz lo informa sin romperse."""
    formulario = flujo.preparar("m02", payload_m02())
    flujo.page.route("**/predict/m02", lambda ruta: ruta.abort())
    formulario.calcular("/predict/m02", esperar_respuesta=False)

    expect(formulario.error).to_be_visible()
    expect(formulario.cuerpo_resultado).to_contain_text("No se pudo conectar con la API")
