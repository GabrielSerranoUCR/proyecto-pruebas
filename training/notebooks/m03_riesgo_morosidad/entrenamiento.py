"""Entrenamiento del modelo M03 (riesgo de morosidad). Decisiones en README.md."""

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RAIZ = Path(__file__).resolve().parents[2]
RUTA_DATOS = RAIZ / "data" / "raw" / "M01-M02-M03.xlsx"
HOJA_ENTRENAMIENTO = "Mor Riesgo Ent"
RUTA_MODELO = RAIZ / "models" / "m03_riesgo_morosidad.joblib"

SEMILLA = 42
PROPORCION_PRUEBA = 0.2
PLIEGUES_CV = 5

CORTE_MEDIO = 0.33
CORTE_ALTO = 0.67
NIVELES = ("bajo", "medio", "alto")

COLUMNA_ID = "Loan_ID"
COLUMNA_OBJETIVO = "Loan_Status"
VALORES_OBJETIVO = {"Y", "N"}

COLUMNAS_NUMERICAS = [
    "Dependents", "ApplicantIncome", "CoapplicantIncome",
    "LoanAmount", "Loan_Amount_Term",
]
COLUMNAS_CATEGORICAS = [
    "Gender", "Married", "Education", "Self_Employed",
    "Property_Area", "Credit_History",
]


def cargar_datos(ruta=RUTA_DATOS, hoja=HOJA_ENTRENAMIENTO):
    """Lee la hoja de entrenamiento y devuelve (entradas, rechazo).

    Dependents mezcla enteros con el texto "3+"; se lleva a 3 para que la
    columna quede numerica. Si Loan_Status trae algo distinto de Y/N se
    detiene, porque la etiqueta rechazo dejaria de tener sentido.
    """
    datos = pd.read_excel(ruta, sheet_name=hoja)

    inesperados = set(datos[COLUMNA_OBJETIVO].dropna()) - VALORES_OBJETIVO
    if inesperados or datos[COLUMNA_OBJETIVO].isna().any():
        raise ValueError(f"Loan_Status con valores no esperados: {inesperados}")

    datos["Dependents"] = pd.to_numeric(datos["Dependents"].replace("3+", 3))
    rechazo = (datos[COLUMNA_OBJETIVO] == "N").astype(int).rename("rechazo")
    entradas = datos.drop(columns=[COLUMNA_ID, COLUMNA_OBJETIVO])
    return entradas, rechazo


def verificar_columnas(entradas):
    """Falla si alguna entrada no esta asignada a un grupo o sobra en ellos."""
    asignadas = set(COLUMNAS_NUMERICAS) | set(COLUMNAS_CATEGORICAS)
    faltan = set(entradas.columns) - asignadas
    sobran = asignadas - set(entradas.columns)
    if faltan or sobran:
        raise ValueError(f"Columnas sin grupo: {faltan}  Columnas inexistentes: {sobran}")


def crear_preprocesador():
    """Imputacion, escalado y one-hot que viajan dentro del modelo exportado.

    Credit_History va con las categoricas aunque sea 0/1: se imputa con el
    valor mas frecuente, no con un promedio. handle_unknown="ignore" evita que
    una categoria no vista detenga la prediccion; esa entrada queda en ceros
    para su columna, asi que la validacion del contrato le toca a la API.
    """
    numericas = Pipeline([
        ("imputar", SimpleImputer(strategy="median")),
        ("escalar", StandardScaler()),
    ])
    categoricas = Pipeline([
        ("imputar", SimpleImputer(strategy="most_frequent")),
        ("codificar", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("num", numericas, COLUMNAS_NUMERICAS),
        ("cat", categoricas, COLUMNAS_CATEGORICAS),
    ])


def dividir(entradas, rechazo):
    """Particion entrenamiento/prueba estratificada por rechazo."""
    return train_test_split(
        entradas, rechazo,
        test_size=PROPORCION_PRUEBA, stratify=rechazo, random_state=SEMILLA,
    )


def main():
    """Ejecuta el entrenamiento completo."""
    entradas, rechazo = cargar_datos()
    verificar_columnas(entradas)
    print(f"Registros: {len(entradas)}  Entradas: {entradas.shape[1]}")
    print(f"Rechazos: {rechazo.sum()}  Aprobados: {(rechazo == 0).sum()}")
    print("Faltantes por columna:")
    print(entradas.isna().sum()[lambda s: s > 0].to_string())

    x_ent, x_pru, y_ent, y_pru = dividir(entradas, rechazo)
    print(f"Entrenamiento: {len(x_ent)}  Prueba: {len(x_pru)}")
    print(f"Tasa de rechazo  entrenamiento: {y_ent.mean():.3f}  prueba: {y_pru.mean():.3f}")


if __name__ == "__main__":
    main()