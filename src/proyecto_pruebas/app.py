"""
Aplicación FastAPI (MVC): conecta los controladores de la API y de las páginas.
Curso: Pruebas de Software (CI0142)
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from proyecto_pruebas.controllers import api_m02, pages
from proyecto_pruebas.models.errores import ErrorRespuesta, mensaje_validacion

logger = logging.getLogger(__name__)

app = FastAPI(title="Proyecto Pruebas - API de modelos", version="0.1.0")
app.include_router(api_m02.router)
app.include_router(pages.router)
app.mount("/static", StaticFiles(directory=pages.STATIC_DIR), name="static")


# Mensajes para los errores HTTP que genera el framework (ruta o método inexistente)
ERRORES_HTTP = {404: "Ruta no encontrada", 405: "Método no permitido"}


def error_json(status_code: int, **campos) -> JSONResponse:
    """Respuesta de error con el formato común de la API."""
    # exclude_unset conserva "campo": null cuando se indica explícitamente
    cuerpo = ErrorRespuesta(**campos).model_dump(exclude_unset=True)
    return JSONResponse(status_code=status_code, content=cuerpo)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """Responde 400 (en lugar del 422 por defecto) con el detalle de cada campo inválido."""
    errores = []
    for err in exc.errors():
        # loc = ("body", "<campo>"); en un JSON mal formado el segundo elemento es la posición
        campo = err["loc"][1] if len(err["loc"]) > 1 and err["type"] != "json_invalid" else None
        errores.append({"campo": campo, "detalle": mensaje_validacion(err)})

    if any(err["type"] == "json_invalid" for err in exc.errors()):
        tipo = "JSON mal formado"
    elif errores[0]["campo"] is None:
        tipo = "Cuerpo de la solicitud inválido"
    else:
        tipo = "Parámetro inválido"
    return error_json(400, error=tipo, **errores[0], errores=errores)


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Devuelve los errores HTTP del framework (404, 405, ...) con el formato común."""
    return error_json(exc.status_code, error=ERRORES_HTTP.get(exc.status_code, str(exc.detail)))


@app.exception_handler(Exception)
async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Evita exponer stack traces, rutas internas o credenciales en la respuesta."""
    logger.exception("Error interno no controlado", exc_info=exc)
    return error_json(500, error="Error interno del servidor")


def openapi_schema() -> dict:
    """Esquema OpenAPI sin la respuesta 422 de FastAPI, que esta API reemplaza por 400."""
    if not app.openapi_schema:
        schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
        for path in schema["paths"].values():
            for operation in path.values():
                operation["responses"].pop("422", None)
        for nombre in ("HTTPValidationError", "ValidationError"):
            schema.get("components", {}).get("schemas", {}).pop(nombre, None)
        app.openapi_schema = schema
    return app.openapi_schema


app.openapi = openapi_schema


def run() -> None:
    """Levanta el servidor de desarrollo."""
    import uvicorn  # pylint: disable=import-outside-toplevel

    uvicorn.run("proyecto_pruebas.app:app", host="127.0.0.1", port=8000, reload=True)
