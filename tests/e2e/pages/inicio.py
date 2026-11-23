"""
Capa 2 (pages): página de inicio con los paneles de los tres modelos.
"""

from playwright.sync_api import Page, expect

from .modelo import ModeloPage


class InicioPage:
    """Página principal: lista los modelos y permite abrir cada formulario."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.url = f"{self.base_url}/"

    def abrir(self) -> "InicioPage":
        # domcontentloaded evita depender de recursos externos (p. ej. Google Fonts)
        self.page.goto(self.url, wait_until="domcontentloaded")
        expect(self.panel("M01")).to_be_visible()
        return self

    def panel(self, modelo: str):
        """Panel de un modelo; `modelo` es su identificador ("M01", "M02", "M03")."""
        return self.page.locator(f'section[aria-labelledby="panel-{modelo}"]')

    def enlace(self, modelo: str):
        """Enlace "Calcular" del panel del modelo."""
        return self.panel(modelo).locator("a.panel-boton")

    def abrir_modelo(self, modelo: str) -> ModeloPage:
        """Hace clic en "Calcular" y devuelve el formulario del modelo."""
        self.enlace(modelo).click()
        pagina = ModeloPage(self.page, self.base_url, modelo)
        expect(pagina.titulo).to_be_visible()
        return pagina
