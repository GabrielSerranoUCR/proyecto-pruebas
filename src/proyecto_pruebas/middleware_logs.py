"""
Middleware que registra las consultas a /predict/<modelo> en Supabase.

Captura la entrada, la salida, el estado HTTP y la duración de cada solicitud,
incluidos los errores de validación (400), las rutas inexistentes (404) y los
fallos internos (500).
"""

import json
import logging
import re
import time
from typing import Any

from starlette.background import BackgroundTask
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from proyecto_pruebas.logs_supabase import RegistroLog, registrar_log

logger = logging.getLogger(__name__)

_RUTA_MODELO = re.compile(r"^/predict/(m\d{2})(?:/|$)", re.IGNORECASE)
_MAX_TEXTO = 4000


def modelo_de_ruta(ruta: str) -> str | None:
    """Extrae 'M02' de '/predict/m02'; devuelve None para otras rutas."""
    coincidencia = _RUTA_MODELO.match(ruta)
    return coincidencia.group(1).upper() if coincidencia else None


def parsear_cuerpo(cuerpo: bytes) -> Any:
    """Devuelve el JSON del cuerpo o el texto (truncado) si no es JSON."""
    if not cuerpo:
        return None
    texto = cuerpo.decode("utf-8", errors="replace")
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return texto[:_MAX_TEXTO]


def _error_de_salida(salida: Any) -> str | None:
    """Extrae el mensaje de error del cuerpo JSON de una respuesta 4xx/5xx."""
    if not isinstance(salida, dict):
        return None
    partes = [salida.get("error"), salida.get("detalle")]
    mensaje = " - ".join(str(parte) for parte in partes if parte)
    return mensaje or None


def _id_de_salida(salida: Any) -> str | None:
    """Extrae el id_ejecucion de una respuesta exitosa."""
    if isinstance(salida, dict):
        valor = salida.get("id_ejecucion")
        return str(valor) if valor else None
    return None


def _texto_error(exc: Exception) -> str:
    """Resume una excepción no controlada para guardarla en el log."""
    return f"{type(exc).__name__}: {exc}"[:_MAX_TEXTO]


def _milisegundos(inicio: float) -> int:
    """Duración transcurrida desde `inicio`, en milisegundos."""
    return int((time.perf_counter() - inicio) * 1000)


class LogMiddleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
    """Registra todas las solicitudes a los endpoints de predicción."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        modelo = modelo_de_ruta(request.url.path)
        if modelo is None:
            return await call_next(request)

        entrada = parsear_cuerpo(await request.body())
        inicio = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            registrar_log(RegistroLog(
                modelo=modelo,
                endpoint=request.url.path,
                metodo=request.method,
                estado=500,
                duracion_ms=_milisegundos(inicio),
                entrada=entrada,
                error=_texto_error(exc),
            ))
            raise

        # Se consume el cuerpo para poder guardar la salida y luego se reconstruye.
        cuerpo = b""
        async for fragmento in response.body_iterator:
            cuerpo += fragmento

        salida = parsear_cuerpo(cuerpo)
        tarea = BackgroundTask(
            registrar_log,
            RegistroLog(
                modelo=modelo,
                endpoint=request.url.path,
                metodo=request.method,
                estado=response.status_code,
                duracion_ms=_milisegundos(inicio),
                entrada=entrada,
                salida=salida,
                error=_error_de_salida(salida) if response.status_code >= 400 else None,
                id_ejecucion=_id_de_salida(salida),
            ),
        )
        return Response(
            content=cuerpo,
            status_code=response.status_code,
            headers=dict(response.headers),
            background=tarea,
        )
