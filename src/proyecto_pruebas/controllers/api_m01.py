"""
Controlador (MVC) de la API JSON del modelo M01.
Curso: Pruebas de Software (CI0142)
"""

from fastapi import APIRouter

from proyecto_pruebas.models import m01
from proyecto_pruebas.models.errores import ErrorRespuesta

router = APIRouter(prefix="/predict", tags=["M01"])

RESPUESTAS_ERROR = {
    400: {"model": ErrorRespuesta, "description": "Datos inválidos, faltantes o JSON mal formado"},
    404: {"model": ErrorRespuesta, "description": "Ruta o modelo inexistente"},
    500: {"model": ErrorRespuesta, "description": "Fallo no controlado del servicio"},
}


@router.post("/m01", response_model=m01.M01Output, responses=RESPUESTAS_ERROR,
             summary="Aprobación del curso (clasificación binaria)")
def predict_m01(payload: m01.M01Input) -> m01.M01Output:
    """Estima si un estudiante aprobará el curso."""
    return m01.predict(payload)
