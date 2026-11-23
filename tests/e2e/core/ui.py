"""
Capa 1 (core): acciones primitivas de UI sobre los formularios.

No conocen el negocio de los modelos: solo saben localizar campos, activar la
pestaña que los contiene (interfaz móvil), elegir opciones en la lista
desplegable personalizada (dropdown.js) y enviar el formulario.
"""

from playwright.sync_api import Locator, Page, Response, expect

BOTON_CALCULAR = "Calcular predicción"


def campo(page: Page, nombre: str) -> Locator:
    """Contenedor (label) del campo cuyo control tiene el nombre indicado."""
    return page.locator(f".campo:has([name='{nombre}'])")


def _numero_de_seccion(caja: Locator) -> str:
    seccion = caja.locator("xpath=ancestor::fieldset").get_attribute("id")
    if not seccion:
        raise AssertionError("El campo no pertenece a ninguna sección del formulario")
    return seccion.removeprefix("grupo-")


def campo_visible(page: Page, nombre: str) -> Locator:
    """Devuelve el campo, activando su pestaña si está oculto (interfaz móvil)."""
    caja = campo(page, nombre)
    if not caja.is_visible():
        page.locator(f"#pestana-{_numero_de_seccion(caja)}").click()
        expect(caja).to_be_visible()
    return caja


def es_select(page: Page, nombre: str) -> bool:
    """Indica si el control del campo es un <select> (lista de opciones)."""
    return campo_visible(page, nombre).locator(f"[name='{nombre}']").evaluate(
        "elemento => elemento.tagName"
    ) == "SELECT"


def escribir(page: Page, nombre: str, valor: str) -> None:
    """Escribe un valor en un campo numérico o de texto."""
    campo_visible(page, nombre).locator(f"[name='{nombre}']").fill(valor)


def elegir(page: Page, nombre: str, valor: str) -> None:
    """Elige una opción usando la lista desplegable visible de la página."""
    caja = campo_visible(page, nombre)
    boton = caja.locator(".dropdown-boton")
    expect(boton).to_be_visible()
    boton.click()

    opcion = caja.locator(f".dropdown-lista li[data-value='{valor}']")
    expect(opcion).to_be_visible()
    opcion.click()

    # El <select> oculto es la fuente del valor que se envía a la API
    expect(caja.locator("select")).to_have_value(valor)


def enviar(page: Page, endpoint: str, esperar_respuesta: bool = True) -> Response | None:
    """Envía el formulario y, si se pide, devuelve la respuesta de la API."""
    if not esperar_respuesta:
        page.get_by_role("button", name=BOTON_CALCULAR).click()
        return None
    with page.expect_response(
        lambda respuesta: endpoint in respuesta.url
        and respuesta.request.method == "POST"
    ) as respuesta:
        page.get_by_role("button", name=BOTON_CALCULAR).click()
    return respuesta.value
