"""Entrenamiento del modelo M03 (riesgo de morosidad). Decisiones en README.md."""

from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score, make_scorer,
    precision_score, recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from data_utils import exportar_datos_prueba

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
# Credit_History acapara más del 53 % de la importancia total y monopoliza la decisión
# (si vale 0 predice siempre riesgo alto sin importar ingresos ni monto; si vale 1,
# casi siempre bajo). Se excluye para que el modelo evalúe el perfil financiero real.
COLUMNA_DOMINANTE = "Credit_History"
VALORES_OBJETIVO = {"Y", "N"}

COLUMNAS_NUMERICAS = [
    "Dependents", "ApplicantIncome", "CoapplicantIncome",
    "LoanAmount", "Loan_Amount_Term",
]
COLUMNAS_CATEGORICAS = [
    "Gender", "Married", "Education", "Self_Employed",
    "Property_Area",
]


def analizar_variables_dominantes(datos: pd.DataFrame, rechazo: pd.Series) -> pd.DataFrame:
    """Evalúa la información mutua de todas las variables originales (incluida Credit_History)."""
    candidatas = datos.drop(columns=[COLUMNA_ID, COLUMNA_OBJETIVO]).copy()
    for col in candidatas.columns:
        if not pd.api.types.is_numeric_dtype(candidatas[col]):
            candidatas[col] = (
                candidatas[col].fillna(candidatas[col].mode()[0]).astype("category").cat.codes
            )
        else:
            candidatas[col] = candidatas[col].fillna(candidatas[col].median())

    info = pd.Series(
        mutual_info_classif(candidatas, rechazo, random_state=SEMILLA),
        index=candidatas.columns,
    ).sort_values(ascending=False)

    proporcion = info / info.sum() if info.sum() > 0 else info
    return pd.DataFrame({
        "Informacion_mutua": info.round(4),
        "Proporcion_info": proporcion.round(4),
        "Estado": [
            "Descartada (variable dominante)" if c == COLUMNA_DOMINANTE else "Seleccionada"
            for c in info.index
        ],
    })


def cargar_datos(ruta=RUTA_DATOS, hoja=HOJA_ENTRENAMIENTO):
    """Lee la hoja de entrenamiento y devuelve (entradas, rechazo, analisis_dominancia).

    Dependents mezcla enteros con el texto "3+"; se lleva a 3 para que la
    columna quede numerica. Se descarta Loan_ID (identificador), Loan_Status
    (objetivo) y Credit_History (variable dominante que absorbe la prediccion).
    """
    datos = pd.read_excel(ruta, sheet_name=hoja)

    inesperados = set(datos[COLUMNA_OBJETIVO].dropna()) - VALORES_OBJETIVO
    if inesperados or datos[COLUMNA_OBJETIVO].isna().any():
        raise ValueError(f"Loan_Status con valores no esperados: {inesperados}")

    datos["Dependents"] = pd.to_numeric(datos["Dependents"].replace("3+", 3))
    rechazo = (datos[COLUMNA_OBJETIVO] == "N").astype(int).rename("rechazo")
    analisis = analizar_variables_dominantes(datos, rechazo)
    entradas = datos.drop(columns=[COLUMNA_ID, COLUMNA_OBJETIVO, COLUMNA_DOMINANTE])
    return entradas, rechazo, analisis


def verificar_columnas(entradas):
    """Falla si alguna entrada no esta asignada a un grupo o sobra en ellos."""
    asignadas = set(COLUMNAS_NUMERICAS) | set(COLUMNAS_CATEGORICAS)
    faltan = set(entradas.columns) - asignadas
    sobran = asignadas - set(entradas.columns)
    if faltan or sobran:
        raise ValueError(f"Columnas sin grupo: {faltan}  Columnas inexistentes: {sobran}")


def crear_preprocesador():
    """Imputacion, escalado y one-hot que viajan dentro del modelo exportado."""
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


def candidatos():
    """Linea base y modelos a comparar con balanceo de clases."""
    return {
        "Dummy": DummyClassifier(strategy="most_frequent"),
        "Regresion logistica": LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=SEMILLA,
        ),
        "Arbol de decision": DecisionTreeClassifier(
            max_depth=4, class_weight="balanced", random_state=SEMILLA,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=6, class_weight="balanced", random_state=SEMILLA,
        ),
    }


def armar_pipeline(modelo):
    """Preprocesador y modelo en un solo objeto, que es lo que se exporta."""
    return Pipeline([("preprocesar", crear_preprocesador()), ("modelo", modelo)])


def comparar(modelos, x_ent, y_ent):
    """F1 promedio de validacion cruzada por modelo, usando solo entrenamiento."""
    pliegues = StratifiedKFold(n_splits=PLIEGUES_CV, shuffle=True, random_state=SEMILLA)
    f1 = make_scorer(f1_score, zero_division=0)
    return {
        nombre: cross_val_score(
            armar_pipeline(modelo), x_ent, y_ent, cv=pliegues, scoring=f1,
        ).mean()
        for nombre, modelo in modelos.items()
    }


def calcular_pesos(pipeline: Pipeline, columnas: list[str]) -> dict[str, float]:
    """Calcula el peso relativo normalizado (suma = 1.0) de cada variable de entrada."""
    preprocesador = pipeline.named_steps["preprocesar"]
    modelo = pipeline.named_steps["modelo"]
    nombres_codificados = list(preprocesador.get_feature_names_out())

    if hasattr(modelo, "feature_importances_"):
        valores = pd.Series(np.abs(modelo.feature_importances_), index=nombres_codificados)
        agregador = "sum"
    elif hasattr(modelo, "coef_"):
        valores = pd.Series(np.abs(modelo.coef_[0]), index=nombres_codificados)
        agregador = "mean"
    else:
        return {col: round(1.0 / len(columnas), 4) for col in columnas}

    brutos = {}
    for col in columnas:
        coincidencias = [
            f for f in nombres_codificados
            if f == f"num__{col}" or f.startswith(f"cat__{col}_")
        ]
        serie_col = valores[coincidencias]
        brutos[col] = float(serie_col.sum() if agregador == "sum" else serie_col.mean())

    total = sum(brutos.values()) or 1.0
    ordenados = sorted(brutos.items(), key=lambda par: par[1], reverse=True)
    return {col: round(val / total, 4) for col, val in ordenados}


def asignar_nivel(probabilidad):
    """Convierte la probabilidad de rechazo en bajo, medio o alto."""
    if not 0 <= probabilidad <= 1:
        raise ValueError(f"Probabilidad fuera de [0, 1]: {probabilidad}")
    if probabilidad < CORTE_MEDIO:
        return NIVELES[0]
    if probabilidad < CORTE_ALTO:
        return NIVELES[1]
    return NIVELES[2]


def evaluar(pipeline, x_pru, y_pru):
    """Metricas binarias, matriz de confusion y rechazo real por nivel."""
    prediccion = pipeline.predict(x_pru)
    probabilidad = pipeline.predict_proba(x_pru)[:, 1]
    metricas = {
        "accuracy": accuracy_score(y_pru, prediccion),
        "precision": precision_score(y_pru, prediccion, zero_division=0),
        "recall": recall_score(y_pru, prediccion, zero_division=0),
        "f1": f1_score(y_pru, prediccion, zero_division=0),
    }
    niveles = pd.Series([asignar_nivel(p) for p in probabilidad], index=y_pru.index)
    tabla = (
        pd.DataFrame({"nivel": niveles, "rechazo": y_pru})
        .groupby("nivel")["rechazo"].agg(registros="count", rechazo_real="mean")
        .reindex(NIVELES)
    )
    return metricas, confusion_matrix(y_pru, prediccion), tabla


def exportar(pipeline, nombre, metricas, columnas, pesos):
    """Guarda pipeline, columnas, pesos, cortes y metricas en un solo artefacto."""
    RUTA_MODELO.parent.mkdir(parents=True, exist_ok=True)
    artefacto = {
        "model_id": "M03",
        "description": "Nivel de riesgo de morosidad (sin variable dominante Credit_History)",
        "model_name": nombre,
        "pipeline": pipeline,
        "feature_names": list(columnas),
        "weights": pesos,
        "cortes": {"medio": CORTE_MEDIO, "alto": CORTE_ALTO},
        "niveles": list(NIVELES),
        "metrics": {k: float(v) for k, v in metricas.items()},
    }
    joblib.dump(artefacto, RUTA_MODELO)


def verificar(pipeline, x_pru):
    """Comprobaciones con resultado esperado conocido; se detiene si alguna falla."""
    artefacto = joblib.load(RUTA_MODELO)
    recargado = artefacto["pipeline"]
    misma_salida = np.allclose(
        recargado.predict_proba(x_pru), pipeline.predict_proba(x_pru),
    )
    casos = {
        0.0: "bajo",
        CORTE_MEDIO - 0.01: "bajo",
        CORTE_MEDIO: "medio",
        CORTE_ALTO - 0.01: "medio",
        CORTE_ALTO: "alto",
        1.0: "alto",
    }
    fallos = {p: e for p, e in casos.items() if asignar_nivel(p) != e}
    if not misma_salida or fallos or "weights" not in artefacto:
        raise AssertionError(f"Recarga igual: {misma_salida}  Cortes fallidos: {fallos}")
    print(f"Verificacion: recarga igual, pesos exportados y {len(casos)} cortes en su nivel")


def main():
    """Ejecuta el entrenamiento completo."""
    entradas, rechazo, analisis = cargar_datos()
    verificar_columnas(entradas)
    print(f"Registros: {len(entradas)}  Entradas seleccionadas: {entradas.shape[1]}")
    print(f"Rechazos: {rechazo.sum()}  Aprobados: {(rechazo == 0).sum()}")
    print("\nAnalisis de dominancia de variables (Informacion Mutua):")
    print(analisis.to_string())

    x_ent, x_pru, y_ent, y_pru = dividir(entradas, rechazo)
    ruta_datos_prueba = exportar_datos_prueba(x_pru, y_pru, "m03")
    print(f"Datos de prueba exportados en: {ruta_datos_prueba}")
    print(f"\nEntrenamiento: {len(x_ent)}  Prueba: {len(x_pru)}")
    print(f"Tasa de rechazo  entrenamiento: {y_ent.mean():.3f}  prueba: {y_pru.mean():.3f}")

    modelos = candidatos()
    f1_cv = comparar(modelos, x_ent, y_ent)
    print("\nF1 de validacion cruzada (entrenamiento):")
    for nombre, valor in sorted(f1_cv.items(), key=lambda par: par[1], reverse=True):
        print(f"  {nombre:<20} {valor:.3f}")

    elegido = max(f1_cv, key=f1_cv.get)
    pipeline = armar_pipeline(modelos[elegido]).fit(x_ent, y_ent)
    pesos = calcular_pesos(pipeline, list(entradas.columns))
    metricas, matriz, tabla = evaluar(pipeline, x_pru, y_pru)

    print(f"\nModelo elegido: {elegido}")
    print("Metricas en prueba:", {k: round(v, 3) for k, v in metricas.items()})
    print("Matriz de confusion (filas: real 0/1, columnas: predicho 0/1):")
    print(matriz)
    print("\nPesos relativos de las variables en el modelo:")
    for col, peso in pesos.items():
        print(f"  {col:<20} {peso * 100:6.2f} % ({peso:.4f})")
    print("\nRechazo real por nivel en prueba:")
    print(tabla.round(2).to_string())

    exportar(pipeline, elegido, metricas, entradas.columns, pesos)
    print(f"\nModelo guardado en: {RUTA_MODELO}")
    verificar(pipeline, x_pru)


if __name__ == "__main__":
    main()
