"""
Capa 1 (core): arranque y parada del servidor real para las pruebas E2E.

Levanta Uvicorn en un puerto libre, con la persistencia en Supabase desactivada
para que las pruebas no dependan de servicios externos.
"""

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
RUTA_SRC = RAIZ / "src"
ESPERA_MAXIMA = 60.0


def puerto_libre() -> int:
    """Reserva un puerto TCP libre del sistema."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_libre:
        socket_libre.bind(("127.0.0.1", 0))
        return int(socket_libre.getsockname()[1])


def _esperar_servidor(url: str, proceso: subprocess.Popen, espera_maxima: float) -> None:
    """Espera a que el servidor responda o falla mostrando su salida."""
    limite = time.monotonic() + espera_maxima
    while time.monotonic() < limite:
        if proceso.poll() is not None:
            salida = proceso.stdout.read() if proceso.stdout else ""
            raise RuntimeError(
                f"El servidor terminó con código {proceso.returncode}:\n{salida}"
            )
        try:
            with urllib.request.urlopen(f"{url}/openapi.json", timeout=1):
                return
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(0.2)
    raise RuntimeError(f"El servidor no respondió en {espera_maxima} segundos")


@contextmanager
def servidor_local(espera_maxima: float = ESPERA_MAXIMA) -> Iterator[str]:
    """Inicia la aplicación en segundo plano y entrega su URL base."""
    puerto = puerto_libre()
    entorno = os.environ.copy()
    entorno["SUPABASE_LOGS_ENABLED"] = "false"
    entorno["PYTHONPATH"] = os.pathsep.join(
        filtro for filtro in (str(RUTA_SRC), entorno.get("PYTHONPATH")) if filtro
    )

    proceso = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn", "proyecto_pruebas.app:app",
            "--host", "127.0.0.1", "--port", str(puerto), "--log-level", "warning",
        ],
        cwd=RAIZ,
        env=entorno,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    url = f"http://127.0.0.1:{puerto}"
    try:
        _esperar_servidor(url, proceso, espera_maxima)
        yield url
    finally:
        proceso.terminate()
        try:
            proceso.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proceso.kill()
            proceso.wait(timeout=10)
