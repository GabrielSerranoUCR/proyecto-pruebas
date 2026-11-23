"""
Capa 2 (flows): flujo de negocio "obtener una predicción".

Orquesta la navegación, el llenado del formulario y el envío a la API. Los
tests de capa 3 solo piden el resultado esperado, sin conocer los selectores.
"""

from typing import Any

from playwright.sync_api import Page

from ..pages.modelo import ModeloPage

ENDPOINTS = {
    "m01": "/predict/m01",
    "m02": "/predict/m02",
    "m03": "/predict/m03",
}


class FlujoPrediccion:
    """Flujo de extremo a extremo para predecir con cualquiera de los modelos."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

    def abrir_formulario(self, modelo: str) -> ModeloPage:
        return ModeloPage(self.page, self.base_url, modelo).abrir()

    def preparar(self, modelo: str, datos: dict[str, Any]) -> ModeloPage:
        """Deja el formulario completo y listo para enviar."""
        return self.abrir_formulario(modelo).rellenar(datos)

    def predecir(self, modelo: str, datos: dict[str, Any]) -> ModeloPage:
        """Completa el formulario, envía la predicción y devuelve la página."""
        pagina = self.preparar(modelo, datos)
        pagina.calcular(ENDPOINTS[modelo.lower()])
        return pagina
