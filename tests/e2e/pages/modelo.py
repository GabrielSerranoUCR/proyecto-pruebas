"""
Capa 2 (pages): formulario de un modelo y su tarjeta de resultado.

El page object conoce el negocio (qué campos tiene el formulario, cómo se
rellena y cómo se muestra el resultado), pero delega las acciones de UI en la
capa core.
"""

from typing import Any

from playwright.sync_api import Locator, Page, Response, expect

from ..core import ui


class ModeloPage:
    """Formulario de predicción de un modelo y su panel de resultado."""

    def __init__(self, page: Page, base_url: str, modelo: str) -> None:
        self.page = page
        self.modelo = modelo.upper()
        self.url = f"{base_url}/{modelo.lower()}"
        self.ultima_respuesta: Response | None = None

    # ---------- Navegación y acciones ----------

    def abrir(self) -> "ModeloPage":
        # domcontentloaded evita depender de recursos externos (p. ej. Google Fonts)
        self.page.goto(self.url, wait_until="domcontentloaded")
        expect(self.titulo).to_be_visible()
        expect(self.formulario).to_be_visible()
        return self

    def rellenar(self, datos: dict[str, Any]) -> "ModeloPage":
        """Completa los campos en orden; los "Sí/No" habilitan sus dependientes."""
        for nombre, valor in datos.items():
            if ui.es_select(self.page, nombre):
                ui.elegir(self.page, nombre, str(valor))
            else:
                ui.escribir(self.page, nombre, str(valor))
        return self

    def calcular(self, endpoint: str, esperar_respuesta: bool = True) -> Response | None:
        """Envía el formulario al endpoint; con `esperar_respuesta=False` no espera."""
        self.ultima_respuesta = ui.enviar(self.page, endpoint, esperar_respuesta)
        return self.ultima_respuesta

    def activar_seccion(self, numero: int) -> "ModeloPage":
        """Activa una pestaña del formulario (solo visible en la interfaz móvil)."""
        self.page.locator(f"#pestana-{numero}").click()
        return self

    # ---------- Elementos de la página ----------

    @property
    def titulo(self) -> Locator:
        return self.page.locator("h1")

    @property
    def formulario(self) -> Locator:
        return self.page.locator("#form")

    @property
    def pestanas(self) -> Locator:
        return self.page.locator(".pestanas")

    @property
    def resultado(self) -> Locator:
        return self.page.locator("#result.ok")

    @property
    def error(self) -> Locator:
        return self.page.locator("#result.err")

    @property
    def cuerpo_resultado(self) -> Locator:
        return self.page.locator("#result-body")

    @property
    def valor_predicho(self) -> Locator:
        return self.page.locator("#result-body .valor")

    @property
    def resumen(self) -> Locator:
        return self.page.locator("#resumen")

    @property
    def resumen_datos(self) -> Locator:
        return self.page.locator("#resumen-datos")

    @property
    def principal(self) -> Locator:
        return self.page.locator("main.modelo")

    def control(self, nombre: str) -> Locator:
        return self.page.locator(f"[name='{nombre}']")

    def error_de_campo(self, nombre: str) -> Locator:
        return self.page.locator(f".campo:has([name='{nombre}']) .campo-error")
