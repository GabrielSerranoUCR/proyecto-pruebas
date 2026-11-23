"""
Capa 3 (test scripts): validación en el navegador y predicción real contra la
API con los modelos de Machine Learning entrenados.
Curso: Pruebas de Software (CI0142)
"""

import re

import pytest
from playwright.sync_api import expect

from .data.payloads import payload_m01, payload_m02, payload_m03_sin_codeudor

pytestmark = pytest.mark.e2e


def test_flujo_completo_m01(flujo):
    """CP-01: completar el formulario de M01 y obtener la predicción de aprobación."""
    pagina = flujo.predecir("m01", payload_m01())

    assert pagina.ultima_respuesta.status == 200
    expect(pagina.resultado).to_be_visible()
    expect(pagina.valor_predicho).to_have_text(re.compile(r"^(Aprueba|No aprueba)$"))
    expect(pagina.cuerpo_resultado).to_contain_text("Probabilidad de aprobar:")
    expect(pagina.cuerpo_resultado).to_contain_text("Modelo M01")


def test_flujo_completo_m02(flujo):
    """CP-02: completar el formulario de M02 y obtener la presión sistólica estimada."""
    pagina = flujo.predecir("m02", payload_m02())

    assert pagina.ultima_respuesta.status == 200
    expect(pagina.resultado).to_be_visible()
    expect(pagina.valor_predicho).to_have_text(re.compile(r"^-?\d+\.\d{2}mmHg$"))
    expect(pagina.cuerpo_resultado).to_contain_text("Modelo M02")


def test_flujo_completo_m03(flujo):
    """CP-03: completar el formulario de M03 (sin codeudor) y obtener el nivel de riesgo."""
    pagina = flujo.predecir("m03", payload_m03_sin_codeudor())

    assert pagina.ultima_respuesta.status == 200
    expect(pagina.resultado).to_be_visible()
    expect(pagina.valor_predicho).to_have_text(
        re.compile(r"^Riesgo (bajo|medio|alto)$")
    )
    expect(pagina.cuerpo_resultado).to_contain_text("Probabilidad de rechazo:")


def test_campos_obligatorios_marcan_error_y_bloquean_el_envio(flujo):
    """Sin datos, la validación del navegador marca los campos y no llama a la API."""
    pagina = flujo.abrir_formulario("m01")

    peticiones = []
    pagina.page.on("request", lambda peticion: peticiones.append(peticion.url))
    pagina.page.get_by_role("button", name="Calcular predicción").click()

    error_edad = pagina.error_de_campo("age")
    expect(error_edad).to_have_text("Campo requerido")
    expect(error_edad).to_be_visible()
    expect(pagina.control("age")).to_be_focused()
    assert not [url for url in peticiones if "/predict/" in url]


def test_valor_fuera_de_rango_muestra_el_limite(flujo):
    """Un valor fuera del contrato muestra el máximo permitido al enviar."""
    pagina = flujo.abrir_formulario("m01")
    pagina.control("age").fill("99")
    pagina.page.get_by_role("button", name="Calcular predicción").click()

    expect(pagina.error_de_campo("age")).to_have_text("Debe ser como máximo 22")


def test_error_desaparece_al_corregir_el_campo(flujo):
    """La validación por campo limpia el mensaje cuando el valor vuelve a ser válido."""
    pagina = flujo.abrir_formulario("m02")
    edad = pagina.control("age")
    edad.fill("999")
    expect(pagina.error_de_campo("age")).to_be_visible()

    edad.fill("50")
    expect(pagina.error_de_campo("age")).to_be_hidden()
