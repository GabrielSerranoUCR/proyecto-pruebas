"""
Datos de prueba para las pruebas E2E (factorías simples).

Cada función devuelve una copia nueva del diccionario para que un test no
modifique los datos de otro. No se usa base de datos: la persistencia en
Supabase está desactivada durante las pruebas.
"""

from typing import Any

_M01 = {
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

_M02 = {
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

_M03 = {
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


def payload_m01() -> dict[str, Any]:
    """Estudiante de ejemplo para el modelo de aprobación del curso."""
    return dict(_M01)


def payload_m02() -> dict[str, Any]:
    """Paciente de ejemplo para el modelo de presión arterial."""
    return dict(_M02)


def payload_m03() -> dict[str, Any]:
    """Solicitante de ejemplo (con codeudor en 0) para el modelo de morosidad."""
    return dict(_M03)


def payload_m03_sin_codeudor() -> dict[str, Any]:
    """Solicitante sin codeudor: la interfaz deshabilita CoapplicantIncome."""
    return {nombre: valor for nombre, valor in _M03.items() if nombre != "CoapplicantIncome"}
