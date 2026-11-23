"""
Capa 3 (test scripts): navegación entre la página de inicio y los formularios.
Curso: Pruebas de Software (CI0142)
"""

import re

import pytest
from playwright.sync_api import expect

from .pages.inicio import InicioPage
from .pages.modelo import ModeloPage

pytestmark = pytest.mark.e2e


def test_inicio_lista_los_tres_modelos(inicio: InicioPage):
    """La página principal muestra los tres modelos con su enlace de cálculo."""
    inicio.abrir()

    for modelo, nombre, ruta in (
        ("M01", "Aprobación del curso", "/m01"),
        ("M02", "Presión arterial", "/m02"),
        ("M03", "Riesgo de morosidad", "/m03"),
    ):
        panel = inicio.panel(modelo)
        expect(panel.get_by_role("heading", name=nombre)).to_be_visible()
        expect(inicio.enlace(modelo)).to_have_attribute("href", ruta)


def test_desde_inicio_se_abre_el_formulario_m01(inicio: InicioPage):
    """El botón "Calcular" del panel M01 navega a su formulario completo."""
    formulario = inicio.abrir().abrir_modelo("M01")

    expect(inicio.page).to_have_url(re.compile(r"/m01$"))
    expect(formulario.titulo).to_have_text("Aprobación del curso")
    expect(formulario.control("absences")).to_be_visible()
    expect(inicio.page.locator(".pesos-panel")).to_be_visible()


def test_volver_al_inicio_desde_un_formulario(flujo):
    """El enlace de regreso del formulario devuelve a la página principal."""
    formulario: ModeloPage = flujo.abrir_formulario("m03")

    formulario.page.get_by_role("link", name="Volver al inicio").click()
    expect(formulario.page).to_have_url(re.compile(r"/$"))
    expect(formulario.page.get_by_role("heading", name="Riesgo de morosidad")).to_be_visible()
