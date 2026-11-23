"""Utilidades compartidas para preparar y exportar datos de entrenamiento."""

from pathlib import Path
from typing import Literal

import pandas as pd

ModelId = Literal["m01", "m02", "m03"]


def exportar_datos_prueba(
    X_test: pd.DataFrame,
    y_test: pd.Series,
    modelo: ModelId,
) -> Path:
    """Guarda predictores y objetivo de prueba en un CSV combinado."""
    if not X_test.index.equals(y_test.index):
        raise ValueError("X_test e y_test deben tener los mismos índices y orden.")

    nombre_objetivo = y_test.name or "target"
    if nombre_objetivo in X_test.columns:
        raise ValueError(f"La columna objetivo ya existe en X_test: {nombre_objetivo}")

    datos_prueba = X_test.join(y_test.rename(nombre_objetivo))
    ruta_salida = (
        Path(__file__).resolve().parent
        / "data"
        / "clean"
        / modelo
        / "1_curso"
        / "test_data.csv"
    )
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    datos_prueba.to_csv(ruta_salida, index=False)
    return ruta_salida
