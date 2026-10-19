"""
Persistencia de los registros de ejecución de los modelos en Supabase.

Cada modelo tiene su propia tabla (logs_m01, logs_m02 y logs_m03). El registro es
"fail-soft": si Supabase no está configurado o falla, la predicción continúa y
el registro se escribe únicamente en la terminal del proceso.
"""

import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv
from supabase import Client, ClientOptions, create_client

logger = logging.getLogger(__name__)

# Carga el .env al importar el módulo (no lanza si el archivo no existe).
load_dotenv()

# Solo se permite insertar en tablas conocidas; evita inyección en el nombre.
TABLAS_POR_MODELO = {
    "m01": "logs_m01",
    "m02": "logs_m02",
    "m03": "logs_m03",
}

TIMEOUT_SEGUNDOS = 5


@dataclass(frozen=True)
class RegistroLog:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Una fila de la tabla de logs de un modelo."""

    modelo: str
    endpoint: str
    metodo: str
    estado: int
    duracion_ms: int
    entrada: Any = None
    salida: Any = None
    error: str | None = None
    id_ejecucion: str | None = None

    def fila(self) -> dict[str, Any]:
        """Convierte el registro en la fila que se inserta en Supabase."""
        datos = asdict(self)
        datos["modelo"] = self.modelo.upper()
        datos["id_ejecucion"] = self.id_ejecucion or str(uuid.uuid4())
        return datos


def logs_habilitados() -> bool:
    """Permite desactivar la persistencia (por ejemplo, en pruebas)."""
    valor = os.getenv("SUPABASE_LOGS_ENABLED", "true")
    return valor.strip().lower() not in {"0", "false", "no", "off"}


@lru_cache(maxsize=1)
def get_client() -> Client | None:
    """Crea el cliente una sola vez; devuelve None si faltan las credenciales."""
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    if not url or not key:
        logger.error(
            "Supabase no configurado (faltan SUPABASE_URL o SUPABASE_KEY): "
            "los registros se escribirán solo en la terminal."
        )
        return None
    # Timeout corto para que una caída de Supabase no retrase las respuestas.
    return create_client(url, key, options=ClientOptions(postgrest_client_timeout=TIMEOUT_SEGUNDOS))


def _texto(valor: Any) -> str:
    """Serializa un campo del registro para mostrarlo en una sola línea."""
    if valor is None:
        return "-"
    return json.dumps(valor, ensure_ascii=False, default=str)


def _registrar_en_terminal(fila: dict[str, Any]) -> None:
    """Imprime el registro en la terminal cuando no se guarda en Supabase."""
    logger.warning(
        "LOG %s %s -> %s (%s ms) id=%s entrada=%s salida=%s error=%s",
        fila["modelo"],
        fila["endpoint"],
        fila["estado"],
        fila["duracion_ms"],
        fila["id_ejecucion"],
        _texto(fila["entrada"]),
        _texto(fila["salida"]),
        fila["error"] or "-",
    )


def registrar_log(registro: RegistroLog) -> None:
    """Guarda el registro en Supabase; si no puede, lo escribe en la terminal."""
    tabla = TABLAS_POR_MODELO.get(registro.modelo.lower())
    if tabla is None:
        logger.warning("Modelo sin tabla de logs: %s", registro.modelo)
        return

    fila = registro.fila()

    # Sin Supabase (deshabilitado o sin credenciales) el registro no se pierde:
    # se escribe en la terminal del proceso.
    if not logs_habilitados():
        _registrar_en_terminal(fila)
        return

    cliente = get_client()
    if cliente is None:
        _registrar_en_terminal(fila)
        return

    try:
        # returning="minimal" evita que PostgREST pida de vuelta la fila insertada:
        # con RLS de solo INSERT, "return=representation" exige además una política SELECT.
        cliente.table(tabla).insert(fila, returning="minimal").execute()
    except Exception:  # pylint: disable=broad-exception-caught
        # CP-27: una falla de Supabase no debe tumbar la predicción.
        logger.exception("No se pudo guardar el log del modelo %s", registro.modelo)
        _registrar_en_terminal(fila)
