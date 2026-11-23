"""
Capa 3 (test scripts): interfaz móvil con pestañas, pantalla de resultado
aparte y regreso al formulario con "Calcular de nuevo".
Curso: Pruebas de Software (CI0142)
"""

import re

import pytest
from playwright.sync_api import expect

from .data.payloads import payload_m02

pytestmark = pytest.mark.e2e


def _comprobar_modo_movil(flujo_movil):
    formulario = flujo_movil.abrir_formulario("m02")
    expect(flujo_movil.page.locator("html")).to_have_class(re.compile(r"\bmovil\b"))
    expect(formulario.pestanas).to_be_visible()
    return formulario


def test_pestanas_agrupan_las_secciones(flujo_movil):
    """En móvil solo se ve la sección activa y las pestañas cambian de sección."""
    formulario = _comprobar_modo_movil(flujo_movil)

    expect(formulario.page.locator("#grupo-1")).to_be_visible()
    expect(formulario.page.locator("#grupo-2")).to_be_hidden()

    formulario.activar_seccion(2)
    expect(formulario.page.locator("#pestana-2")).to_have_attribute(
        "aria-selected", "true"
    )
    expect(formulario.page.locator("#grupo-2")).to_be_visible()
    expect(formulario.page.locator("#grupo-1")).to_be_hidden()


def test_resultado_en_pantalla_aparte_y_recalculo(flujo_movil):
    """En móvil el resultado reemplaza al formulario y se puede volver a calcular."""
    formulario = flujo_movil.predecir("m02", payload_m02())
    assert formulario.ultima_respuesta.status == 200

    expect(formulario.principal).to_have_class(re.compile(r"\bviendo-resultado\b"))
    expect(formulario.valor_predicho).to_be_visible()
    expect(formulario.formulario).to_be_hidden()

    # El resumen con los datos ingresados se despliega en la pantalla del resultado
    expect(formulario.resumen).to_be_visible()
    formulario.resumen.locator("summary").click()
    expect(formulario.resumen_datos).to_contain_text("Edad (años)")

    flujo_movil.page.locator("#recalcular").click()
    expect(formulario.principal).not_to_have_class(re.compile(r"\bviendo-resultado\b"))
    expect(formulario.formulario).to_be_visible()


def test_el_resumen_refleja_los_datos_ingresados(flujo_movil):
    """El resumen móvil muestra las mismas etiquetas y valores del formulario."""
    formulario = flujo_movil.predecir("m02", payload_m02())

    expect(formulario.resumen_datos).to_contain_text("Sexo")
    expect(formulario.resumen_datos).to_contain_text("Masculino")
    expect(formulario.resumen_datos).to_contain_text("Cigarrillos por día")
    expect(formulario.resumen_datos).to_contain_text("20")
