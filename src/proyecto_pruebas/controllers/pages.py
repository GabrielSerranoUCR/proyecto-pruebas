"""
Controlador (MVC) de las páginas HTML de la interfaz de usuario.
Curso: Pruebas de Software (CI0142)
"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from proyecto_pruebas.models.m02 import M02Input

VIEWS_DIR = Path(__file__).resolve().parents[1] / "views"
STATIC_DIR = VIEWS_DIR / "static"

templates = Jinja2Templates(directory=VIEWS_DIR / "templates")
router = APIRouter(include_in_schema=False)

# Modelos de la página de inicio; los que no tienen ruta aparecen como "Próximamente"
MODELOS = {
    "M01": {
        "id": "M01", "nombre": "Aprobación del curso", "ruta": "/m01",
        "algoritmo": "Clasificación binaria",
        "descripcion": (
            "Estima si un estudiante aprobará el curso a partir de su desempeño académico."
        ),
        "imagen": "img/testpass.jpg", "fondo": "img/classroombg.jpg",
    },
    "M02": {
        "id": "M02", "nombre": "Presión arterial", "ruta": "/m02",
        "algoritmo": "Regresión",
        "descripcion": (
            "Estima la presión arterial sistólica (mmHg) a partir de los datos del paciente."
        ),
        "imagen": "img/pressure.jpg", "fondo": "img/hospitalbg.jpg",
    },
    "M03": {
        "id": "M03", "nombre": "Riesgo de morosidad", "ruta": "/m03",
        "algoritmo": "Clasificación multiclase",
        "descripcion": (
            "Clasifica el riesgo de morosidad de un cliente a partir de su perfil financiero."
        ),
        "imagen": "img/debt.jpg", "fondo": "img/bankbg.jpg",
    },
}

SI_NO = [(0, "No"), (1, "Sí")]

# (nombre, etiqueta, opciones); opciones=None indica un campo numérico
M02_GRUPOS = [
    ("Datos generales", [
        ("male", "Sexo", [(1, "Masculino"), (0, "Femenino")]),
        ("age", "Edad (años)", None),
        ("education", "Nivel educativo", [
            (1, "1 - Primaria"), (2, "2 - Secundaria"),
            (3, "3 - Técnico"), (4, "4 - Universitario"),
        ]),
    ]),
    ("Hábitos y antecedentes", [
        ("currentSmoker", "¿Fumador actual?", SI_NO),
        ("cigsPerDay", "Cigarrillos por día", None),
        ("BPMeds", "¿Toma medicamentos para la presión?", SI_NO),
        ("prevalentStroke", "¿Derrame cerebral previo?", SI_NO),
        ("prevalentHyp", "¿Hipertensión previa?", SI_NO),
        ("diabetes", "¿Diabetes?", SI_NO),
    ]),
    ("Mediciones clínicas", [
        ("totChol", "Colesterol total (mg/dL)", None),
        ("BMI", "Índice de masa corporal", None),
        ("heartRate", "Frecuencia cardíaca (lpm)", None),
        ("glucose", "Glucosa (mg/dL)", None),
    ]),
]


def build_grupos(schema_model: type[BaseModel], grupos: list) -> list[dict]:
    """Combina las etiquetas de la vista con los límites del contrato del modelo."""
    props = schema_model.model_json_schema()["properties"]
    return [
        {
            "titulo": titulo,
            "campos": [
                {
                    "name": name,
                    "label": label,
                    "options": options,
                    "integer": props[name]["type"] == "integer",
                    "min": props[name].get("minimum", props[name].get("exclusiveMinimum")),
                    "min_exclusive": "exclusiveMinimum" in props[name],
                    "max": props[name]["maximum"],
                }
                for name, label, options in campos
            ],
        }
        for titulo, campos in grupos
    ]


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    """Página de inicio con los tres modelos."""
    return templates.TemplateResponse(request, "inicio.html", {"modelos": MODELOS.values()})


def render_modelo(request: Request, modelo_id: str, grupos: list | None = None,
                  endpoint: str | None = None) -> HTMLResponse:
    """Página de un modelo; sin grupos ni endpoint se muestra como vista previa."""
    modelo = MODELOS[modelo_id]
    return templates.TemplateResponse(request, "modelo.html", {
        "titulo": modelo["nombre"],
        "descripcion": modelo["descripcion"],
        "fondo": modelo["fondo"],
        "algoritmo": modelo["algoritmo"],
        "grupos": grupos or [],
        "endpoint": endpoint,
    })


@router.get("/m01", response_class=HTMLResponse)
def page_m01(request: Request) -> HTMLResponse:
    """Vista previa del modelo M01 (aún sin campos ni API)."""
    return render_modelo(request, "M01")


@router.get("/m02", response_class=HTMLResponse)
def page_m02(request: Request) -> HTMLResponse:
    """Formulario del modelo M02."""
    return render_modelo(request, "M02", build_grupos(M02Input, M02_GRUPOS), "/predict/m02")


@router.get("/m03", response_class=HTMLResponse)
def page_m03(request: Request) -> HTMLResponse:
    """Vista previa del modelo M03 (aún sin campos ni API)."""
    return render_modelo(request, "M03")
