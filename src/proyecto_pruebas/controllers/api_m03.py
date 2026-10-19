"""
Controlador (MVC) de la API JSON del modelo M03.
Curso: Pruebas de Software (CI0142)
"""

from fastapi import APIRouter

from proyecto_pruebas.models import m03
from proyecto_pruebas.models.errores import ErrorRespuesta

router = APIRouter(prefix="/predict", tags=["M03"])

RESPUESTAS_ERROR = {
    400: {"model": ErrorRespuesta, "description": "Datos inválidos, faltantes o JSON mal formado"},
    404: {"model": ErrorRespuesta, "description": "Ruta o modelo inexistente"},
    500: {"model": ErrorRespuesta, "description": "Fallo no controlado del servicio"},
}


@router.post("/m03", response_model=m03.M03Output, responses=RESPUESTAS_ERROR,
             summary="Riesgo de morosidad (clasificación multiclase)")
def predict_m03(payload: m03.M03Input) -> m03.M03Output:
    """Clasifica el nivel de riesgo de morosidad (bajo, medio, alto) de una solicitud."""
    return m03.predict(payload)
