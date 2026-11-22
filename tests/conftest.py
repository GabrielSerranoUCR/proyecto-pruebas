"""
Configuración común y accesorios (fixtures) para la batería de pruebas de pytest.
Curso: Pruebas de Software (CI0142)
"""

import os
import pytest
from fastapi.testclient import TestClient

from proyecto_pruebas.app import app


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configura variables de entorno para la ejecución de pruebas."""
    # Desactiva llamadas de red reales a Supabase durante pruebas automáticas por defecto
    os.environ["SUPABASE_LOGS_ENABLED"] = "true"
    yield


@pytest.fixture
def client():
    """Cliente de pruebas para la API FastAPI."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_m02_payload():
    """Carga útil válida para el modelo M02 (Presión arterial)."""
    return {
        "male": 1,
        "age": 50,
        "education": 2,
        "currentSmoker": 1,
        "cigsPerDay": 20.0,
        "BPMeds": 0,
        "prevalentStroke": 0,
        "prevalentHyp": 0,
        "diabetes": 0,
        "totChol": 240.0,
        "BMI": 26.5,
        "heartRate": 75.0,
        "glucose": 80.0,
    }


@pytest.fixture
def valid_m01_payload():
    """Carga útil válida para el modelo M01 (Aprobación de curso)."""
    return {
        "sex": 2,
        "age": 17,
        "famsize": 1,
        "Medu": 2,
        "Fedu": 1,
        "failures": 0,
        "absences": 4,
        "reason": 3,
        "schoolsup": 2,
        "famsup": 1,
        "nursery": 1,
        "higher": 1,
        "internet": 1,
        "activities": 2,
        "freetime": 3,
        "Dalc": 1,
        "health": 3,
    }


@pytest.fixture
def valid_m03_payload():
    """Carga útil válida para el modelo M03 (Riesgo de morosidad, sin Credit_History)."""
    return {
        "Gender": "Male",
        "Married": "Yes",
        "Dependents": 0,
        "Education": "Graduate",
        "Self_Employed": "No",
        "ApplicantIncome": 5720.0,
        "CoapplicantIncome": 0.0,
        "LoanAmount": 110.0,
        "Loan_Amount_Term": 360.0,
        "Property_Area": "Urban",
    }
