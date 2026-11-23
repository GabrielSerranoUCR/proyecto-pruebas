"""
Fixtures de las pruebas E2E: servidor real, navegador móvil y page objects.

La infraestructura vive en `core/`, el negocio en `pages/` y `flows/`, y los
datos en `data/`. Los tests solo reciben fixtures y llaman a los flujos.

Curso: Pruebas de Software (CI0142)
"""

from collections.abc import Iterator

import pytest

from .core.servidor import servidor_local
from .flows.prediccion import FlujoPrediccion
from .pages.inicio import InicioPage

# Un iPhone real: el servidor marca la interfaz como móvil y Chromium, además,
# aplica la ventana angosta de 390 px.
UA_MOVIL = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Mobile/15E148 Safari/604.1"
)


@pytest.fixture(scope="session")
def app_url() -> Iterator[str]:
    """Levanta la aplicación en segundo plano y devuelve su URL base."""
    with servidor_local() as url:
        yield url


@pytest.fixture
def inicio(page, app_url) -> InicioPage:
    """Página de inicio lista para navegar a los modelos."""
    return InicioPage(page, app_url)


@pytest.fixture
def flujo(page, app_url) -> FlujoPrediccion:
    """Flujo de predicción en resolución de escritorio."""
    return FlujoPrediccion(page, app_url)


@pytest.fixture
def movil_page(browser, pytestconfig, output_path):
    """Página con ventana y user agent de teléfono (interfaz móvil).

    Como usa su propio contexto, pytest-playwright no le toma la captura final;
    con ``--screenshot=on`` se guarda aquí, igual que en las pruebas de escritorio.
    """
    contexto = browser.new_context(
        viewport={"width": 390, "height": 844},
        user_agent=UA_MOVIL,
        is_mobile=True,
        has_touch=True,
        device_scale_factor=3,
    )
    pagina = contexto.new_page()
    yield pagina
    if pytestconfig.getoption("--screenshot") == "on":
        pagina.screenshot(path=f"{output_path}/test-finished-1.png", full_page=True)
    contexto.close()


@pytest.fixture
def flujo_movil(movil_page, app_url) -> FlujoPrediccion:
    """Flujo de predicción con la interfaz móvil (pestañas y pantalla aparte)."""
    return FlujoPrediccion(movil_page, app_url)
