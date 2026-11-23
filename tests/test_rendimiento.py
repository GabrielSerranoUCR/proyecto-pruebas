"""
Prueba no funcional de rendimiento básico (RNF-01, CP-30).
Curso: Pruebas de Software (CI0142)

Mide el tiempo de respuesta de cada endpoint de predicción en un escenario
representativo (una solicitud válida repetida, tras calentar el caché del
artefacto ``.joblib``) y verifica que el percentil 95 quede bajo el umbral de
aceptación definido en el plan de pruebas. La persistencia en Supabase se
simula para medir solo API + modelo.
"""

# Pytest fixtures are injected as function arguments.
# pylint: disable=redefined-outer-name

import statistics
import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from proyecto_pruebas.app import app

REPETICIONES = 20
UMBRAL_P95_MS = 500.0


@pytest.fixture(scope="module")
def cliente_sin_bd():
    """Cliente HTTP sin llamadas reales a Supabase."""
    with patch("proyecto_pruebas.middleware_logs.registrar_log"):
        with TestClient(app) as test_client:
            yield test_client


@pytest.mark.parametrize("modelo", ["m01", "m02", "m03"])
def test_cp30_tiempo_de_respuesta(
    cliente_sin_bd, modelo, valid_m01_payload, valid_m02_payload, valid_m03_payload
):
    """El p95 del tiempo de respuesta de /predict/<modelo> es menor que 500 ms."""
    payload = {
        "m01": valid_m01_payload,
        "m02": valid_m02_payload,
        "m03": valid_m03_payload,
    }[modelo]
    ruta = f"/predict/{modelo}"

    # Calentamiento: carga del artefacto en el caché @lru_cache.
    assert cliente_sin_bd.post(ruta, json=payload).status_code == 200

    tiempos_ms = []
    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        respuesta = cliente_sin_bd.post(ruta, json=payload)
        tiempos_ms.append((time.perf_counter() - inicio) * 1000)
        assert respuesta.status_code == 200

    tiempos_ms.sort()
    p95 = tiempos_ms[int(0.95 * (len(tiempos_ms) - 1))]
    print(
        f"\n{ruta}: media={statistics.mean(tiempos_ms):.2f} ms "
        f"mediana={statistics.median(tiempos_ms):.2f} ms "
        f"min={tiempos_ms[0]:.2f} ms max={tiempos_ms[-1]:.2f} ms p95={p95:.2f} ms"
    )
    assert p95 < UMBRAL_P95_MS, f"{ruta}: p95={p95:.2f} ms supera {UMBRAL_P95_MS} ms"
