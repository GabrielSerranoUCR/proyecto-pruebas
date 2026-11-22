"""
Pruebas de la capa de interfaz de usuario (HTML/Jinja2):
- CP-01: Despliegue de formulario M01 y panel de pesos de variables
- CP-02: Despliegue de formulario M02 y panel de pesos de variables
- Despliegue de formulario M03 (sin Credit_History) y panel de pesos
- Carga de página principal con los tres modelos
Curso: Pruebas de Software (CI0142)
"""

from fastapi.testclient import TestClient


def test_cp01_despliegue_formulario_m01(client: TestClient):
    """
    CP-01: Carga de la página del formulario para M01 (Aprobación del curso).
    Verifica respuesta 200, presencia de campos específicos de M01 y visualización de pesos.
    """
    response = client.get("/m01")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    html = response.text
    assert "Aprobación del curso" in html
    assert 'name="absences"' in html
    assert 'name="failures"' in html
    assert "Pesos de las variables (%)" in html


def test_cp02_despliegue_formulario_m02(client: TestClient):
    """
    CP-02: Carga de la página del formulario para M02 (Presión arterial).
    Verifica respuesta 200, presencia de campos clínicos de M02 y visualización de pesos.
    """
    response = client.get("/m02")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    html = response.text
    assert "Presión arterial" in html
    assert 'name="totChol"' in html
    assert 'name="cigsPerDay"' in html
    assert 'name="heartRate"' in html
    assert "Pesos de las variables (%)" in html


def test_despliegue_formulario_m03(client: TestClient):
    """
    Carga de la página del formulario para M03 (Riesgo de morosidad).
    Verifica que Credit_History ya no esté en el formulario y que se muestren los pesos.
    """
    response = client.get("/m03")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    html = response.text
    assert "Riesgo de morosidad" in html
    assert 'name="ApplicantIncome"' in html
    assert 'name="Property_Area"' in html
    assert 'name="Credit_History"' not in html
    assert "Pesos de las variables (%)" in html


def test_pagina_inicio_renderiza_modelos(client: TestClient):
    """
    Verifica que la página principal (/) cargue correctamente y liste los modelos disponibles.
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert "Aprobación del curso" in html
    assert "Presión arterial" in html
    assert "Riesgo de morosidad" in html
