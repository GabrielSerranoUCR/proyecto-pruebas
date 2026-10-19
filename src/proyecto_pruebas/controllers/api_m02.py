"""
Controlador (MVC) de la API JSON del modelo M02.
Curso: Pruebas de Software (CI0142)
"""

from fastapi import APIRouter

from proyecto_pruebas.models import m02
from proyecto_pruebas.models.errores import ErrorRespuesta

router = APIRouter(prefix="/predict", tags=["M02"])

RESPUESTAS_ERROR = {
    400: {"model": ErrorRespuesta, "description": "Datos inválidos, faltantes o JSON mal formado"},
    404: {"model": ErrorRespuesta, "description": "Ruta o modelo inexistente"},
    500: {"model": ErrorRespuesta, "description": "Fallo no controlado del servicio"},
}


@router.post("/m02", response_model=m02.M02Output, responses=RESPUESTAS_ERROR,
             summary="Presión arterial estimada (regresión)")
def predict_m02(payload: m02.M02Input) -> m02.M02Output:
    """Estima la presión arterial sistólica (sysBP, en mmHg) de un paciente."""
    return m02.predict(payload)
