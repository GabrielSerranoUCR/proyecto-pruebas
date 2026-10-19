"""
Controlador (MVC) de las páginas HTML de la interfaz de usuario.
Curso: Pruebas de Software (CI0142)
"""

import re
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from proyecto_pruebas.models.m01 import M01Input
from proyecto_pruebas.models.m02 import M02Input
from proyecto_pruebas.models.m03 import M03Input

VIEWS_DIR = Path(__file__).resolve().parents[1] / "views"
STATIC_DIR = VIEWS_DIR / "static"

templates = Jinja2Templates(directory=VIEWS_DIR / "templates")

# "Mobi" es la marca que usan los navegadores de teléfonos en su user agent (Android, iOS,
# Firefox, Opera); iPhone e iPod se incluyen por navegadores que la omiten
UA_MOVIL = re.compile(r"Mobi|iPhone|iPod")


def es_movil(request: Request) -> bool:
    """Indica si la solicitud viene de un teléfono, aunque esté en horizontal."""
    return bool(UA_MOVIL.search(request.headers.get("user-agent", "")))


templates.env.globals["es_movil"] = es_movil
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
        # 17 campos: con 5 columnas el formulario cabe sin desplazamiento en 1440 x 900
        "columnas": 5,
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
# M01 usa la codificación del cuaderno de entrenamiento: sí = 1, no = 2
SI_NO_M01 = [(1, "Sí"), (2, "No")]
ESCOLARIDAD = [
    (0, "Ninguna"), (1, "4.º grado"), (2, "Primaria"), (3, "Secundaria"), (4, "Superior"),
]


def escala(*etiquetas: str) -> list[tuple[int, str]]:
    """Opciones de una escala 1 a 5; solo se muestra la etiqueta cualitativa."""
    return list(enumerate(etiquetas, start=1))


# (nombre, etiqueta, opciones[, habilita]); opciones=None indica un campo numérico.
# habilita: campo que solo se activa con "Sí" (con "No" queda bloqueado en 0).
M02_GRUPOS = [
    ("Datos generales", [
        ("male", "Sexo", [(1, "Masculino"), (0, "Femenino")]),
        ("age", "Edad (años)", None),
        ("education", "Nivel educativo", [
            (1, "Primaria"), (2, "Secundaria"), (3, "Técnico"), (4, "Universitario"),
        ]),
    ]),
    ("Hábitos y antecedentes", [
        ("currentSmoker", "¿Fumador actual?", SI_NO, "cigsPerDay"),
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


M01_GRUPOS = [
    ("Datos personales", [
        ("sex", "Sexo", [(1, "Masculino"), (2, "Femenino")]),
        ("age", "Edad (años)", None),
        ("famsize", "Tamaño familiar", [(1, "Más de 3"), (2, "3 o menos")]),
        ("Medu", "Escolaridad madre", ESCOLARIDAD),
        ("Fedu", "Escolaridad padre", ESCOLARIDAD),
    ]),
    ("Trayectoria académica", [
        ("failures", "Cursos perdidos", [
            (0, "0"), (1, "1"), (2, "2"), (3, "3 o más"),
        ]),
        ("absences", "Ausencias", None),
        ("reason", "Motivo de elección", [
            (1, "Cursos"), (2, "Cercanía"), (3, "Reputación"), (4, "Otro"),
        ]),
        ("schoolsup", "¿Apoyo escolar?", SI_NO_M01),
        ("famsup", "¿Apoyo familiar?", SI_NO_M01),
        ("nursery", "¿Preescolar?", SI_NO_M01),
        ("higher", "¿Educ. superior?", SI_NO_M01),
    ]),
    ("Hábitos y entorno", [
        ("internet", "¿Internet en casa?", SI_NO_M01),
        ("activities", "¿Actividades extra?", SI_NO_M01),
        ("freetime", "Tiempo libre", escala("Muy poco", "Poco", "Moderado", "Bastante", "Mucho")),
        ("Dalc", "Alcohol (semana)", escala("Muy bajo", "Bajo", "Moderado", "Alto", "Muy alto")),
        ("health", "Estado de salud", escala("Muy mal", "Mal", "Regular", "Bien", "Muy bien")),
    ]),
]

# Los valores son los del conjunto de datos; las etiquetas se muestran en español
SI_NO_M03 = [("No", "No"), ("Yes", "Sí")]
M03_GRUPOS = [
    ("Solicitante", [
        ("Gender", "Sexo", [("Male", "Masculino"), ("Female", "Femenino")]),
        ("Married", "¿Casado?", SI_NO_M03),
        ("Dependents", "Dependientes", [(0, "0"), (1, "1"), (2, "2"), (3, "3 o más")]),
        ("Education", "Educación", [("Graduate", "Graduado"), ("Not Graduate", "No graduado")]),
    ]),
    ("Empleo e ingresos", [
        ("Self_Employed", "¿Trabaja por cuenta propia?", SI_NO_M03),
        ("ApplicantIncome", "Ingreso mensual del solicitante (USD)", None),
        # Solo de la interfaz: el contrato no lo incluye, pero aclara cuándo llenar el ingreso
        ("tieneCodeudor", "¿Tiene codeudor?", SI_NO, "CoapplicantIncome"),
        ("CoapplicantIncome", "Ingreso mensual del codeudor (USD)", None),
    ]),
    ("Préstamo", [
        ("LoanAmount", "Monto del préstamo (miles de USD)", None),
        ("Loan_Amount_Term", "Plazo (meses)", None),
        ("Credit_History", "¿Historial crediticio al día?", [(1, "Sí"), (0, "No")]),
        ("Property_Area", "Zona de la propiedad", [
            ("Urban", "Urbana"), ("Semiurban", "Semiurbana"), ("Rural", "Rural"),
        ]),
    ]),
]


def build_campo(props: dict, name: str, label: str, options: list | None,
                habilita: str | None = None) -> dict:
    """Un campo de la vista con los límites que fija el contrato del modelo."""
    prop = props.get(name, {})
    return {
        "name": name,
        "label": label,
        "options": options,
        # Las listas con valores de texto se envían sin convertir a número
        "tipo": "str" if options and isinstance(options[0][0], str) else "int",
        "integer": prop.get("type") == "integer",
        "min": prop.get("minimum", prop.get("exclusiveMinimum")),
        "min_exclusive": "exclusiveMinimum" in prop,
        "max": prop.get("maximum"),
        "habilita": habilita,
        # Un campo que no está en el contrato solo se usa en la interfaz y no se envía
        "local": name not in props,
    }


def build_grupos(schema_model: type[BaseModel], grupos: list) -> list[dict]:
    """Combina las etiquetas de la vista con los límites del contrato del modelo."""
    props = schema_model.model_json_schema()["properties"]
    return [
        {"titulo": titulo, "campos": [build_campo(props, *campo) for campo in campos]}
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
        "columnas": modelo.get("columnas", 4),
        "grupos": grupos or [],
        "endpoint": endpoint,
    })


@router.get("/m01", response_class=HTMLResponse)
def page_m01(request: Request) -> HTMLResponse:
    """Formulario del modelo M01."""
    return render_modelo(request, "M01", build_grupos(M01Input, M01_GRUPOS), "/predict/m01")


@router.get("/m02", response_class=HTMLResponse)
def page_m02(request: Request) -> HTMLResponse:
    """Formulario del modelo M02."""
    return render_modelo(request, "M02", build_grupos(M02Input, M02_GRUPOS), "/predict/m02")


@router.get("/m03", response_class=HTMLResponse)
def page_m03(request: Request) -> HTMLResponse:
    """Formulario del modelo M03."""
    return render_modelo(request, "M03", build_grupos(M03Input, M03_GRUPOS), "/predict/m03")
