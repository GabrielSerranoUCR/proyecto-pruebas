"""
Script de entrenamiento y evaluación para el modelo M02: Presión Arterial Estimada (Regresión).
Curso: Pruebas de Software (CI0142)
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def load_data() -> pd.DataFrame:
    """Carga el conjunto de datos desde el archivo Excel M01-M02-M03.xlsx o CSV de respaldo."""
    excel_path = "training/data/raw/M01-M02-M03.xlsx"
    csv_path = "training/data/raw/m02_presion_arterial.csv"

    if os.path.exists(excel_path):
        return pd.read_excel(excel_path, sheet_name="Presión Arterial")
    elif os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    else:
        raise FileNotFoundError("No se encontró el archivo de datos para Presión Arterial.")

def preprocess_and_split(df: pd.DataFrame):
    """Limpia y prepara las variables predictoras y la variable objetivo."""
    df = df.copy()
    # Si la persona no fuma (currentSmoker == 0) y cigsPerDay es nulo, se imputa 0
    df.loc[(df["currentSmoker"] == 0) & (df["cigsPerDay"].isna()), "cigsPerDay"] = 0

    feature_cols = [
        "male",
        "age",
        "education",
        "currentSmoker",
        "cigsPerDay",
        "BPMeds",
        "prevalentStroke",
        "prevalentHyp",
        "diabetes",
        "totChol",
        "BMI",
        "heartRate",
        "glucose",
    ]
    target_col = "sysBP"

    X = df[feature_cols]
    y = df[target_col]

    return train_test_split(X, y, test_size=0.2, random_state=42), feature_cols

def build_pipeline(regressor, numerical_cols: list[str], binary_cols: list[str]) -> Pipeline:
    """Crea un pipeline reproducible con imputación, escalado y regresor."""
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    bin_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
    ])

    preprocessor = ColumnTransformer([
        ("num", num_pipeline, numerical_cols),
        ("bin", bin_pipeline, binary_cols),
    ])

    return Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", regressor),
    ])

def evaluate_models(X_train, X_test, y_train, y_test, numerical_cols, binary_cols):
    """Entrena y evalúa los diferentes modelos candidatos."""
    candidate_regressors = {
        "Dummy (Mean)": DummyRegressor(strategy="mean"),
        "Linear Regression": LinearRegression(),
        "Ridge": Ridge(alpha=1.0),
        "Decision Tree": RandomForestRegressor(n_estimators=1, max_depth=5, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42),
    }

    results = []
    trained_pipelines = {}
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    for name, reg in candidate_regressors.items():
        pipe = build_pipeline(reg, numerical_cols, binary_cols)
        cv_r2 = cross_val_score(pipe, X_train, y_train, cv=kf, scoring="r2").mean()

        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)

        mae = mean_absolute_error(y_test, preds)
        mse = mean_squared_error(y_test, preds)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, preds)

        results.append({
            "Modelo": name,
            "CV R2 (5-fold)": cv_r2,
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2,
        })
        trained_pipelines[name] = pipe

    res_df = pd.DataFrame(results).sort_values("RMSE")
    return res_df, trained_pipelines

def main():
    print("[1/4] Cargando datos de Presión Arterial...")
    df = load_data()
    print(f"      Dimensiones del dataset: {df.shape[0]} filas x {df.shape[1]} columnas")

    print("[2/4] Preparando y dividiendo datos (80% train / 20% test)...")
    (X_train, X_test, y_train, y_test), feature_cols = preprocess_and_split(df)

    numerical_cols = ["age", "education", "cigsPerDay", "totChol", "BMI", "heartRate", "glucose"]
    binary_cols = ["male", "currentSmoker", "BPMeds", "prevalentStroke", "prevalentHyp", "diabetes"]

    print("[3/4] Entrenando y evaluando modelos candidatos...")
    res_df, trained_pipelines = evaluate_models(
        X_train, X_test, y_train, y_test, numerical_cols, binary_cols
    )
    print("\nResultados de Comparación:")
    print(res_df.to_string(index=False))

    best_model_name = res_df.iloc[0]["Modelo"]
    best_pipe = trained_pipelines[best_model_name]

    print(f"\n[4/4] Mejor modelo seleccionado: {best_model_name}")
    model_output_dir = "training/models"
    os.makedirs(model_output_dir, exist_ok=True)
    model_path = os.path.join(model_output_dir, "blood_pressure_ridge_model.joblib")

    # Exportamos directamente el pipeline listo para inferencia en el backend
    joblib.dump(best_pipe, model_path)
    print(f"      Modelo exportado exitosamente en: {model_path}")

    # Prueba de inferencia
    sample_patient = pd.DataFrame([{
        "male": 1,
        "age": 45,
        "education": 3,
        "currentSmoker": 1,
        "cigsPerDay": 20,
        "BPMeds": 0,
        "prevalentStroke": 0,
        "prevalentHyp": 0,
        "diabetes": 0,
        "totChol": 220,
        "BMI": 26.5,
        "heartRate": 75,
        "glucose": 85,
    }])
    pred_bp = best_pipe.predict(sample_patient)[0]
    print(f"\nVerificación de inferencia:")
    print(f"Paciente de muestra -> Presión Arterial Sistólica Estimada: {pred_bp:.2f} mmHg")

if __name__ == "__main__":
    main()
