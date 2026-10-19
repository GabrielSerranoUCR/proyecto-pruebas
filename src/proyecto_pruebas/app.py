"""
Aplicación FastAPI (MVC): conecta los controladores de la API.
Curso: Pruebas de Software (CI0142)
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from proyecto_pruebas.controllers import api_m02

logger = logging.getLogger(__name__)

app = FastAPI(title="Proyecto Pruebas - API de modelos", version="0.1.0")
app.include_router(api_m02.router)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """Responde 400 (en lugar del 422 por defecto) con el detalle de cada campo inválido."""
    errores = [
        {"campo": ".".join(str(part) for part in err["loc"][1:]), "mensaje": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(status_code=400, content={"error": "Entrada inválida", "detalle": errores})


@app.exception_handler(Exception)
async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Evita exponer stack traces, rutas internas o credenciales en la respuesta."""
    logger.exception("Error interno no controlado", exc_info=exc)
    return JSONResponse(status_code=500, content={"error": "Error interno del servidor"})


def run() -> None:
    """Levanta el servidor de desarrollo."""
    import uvicorn  # pylint: disable=import-outside-toplevel

    uvicorn.run("proyecto_pruebas.app:app", host="127.0.0.1", port=8000, reload=True)
