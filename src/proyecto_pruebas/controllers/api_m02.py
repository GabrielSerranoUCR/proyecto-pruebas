"""
Controlador (MVC) de la API JSON del modelo M02.
Curso: Pruebas de Software (CI0142)
"""

from fastapi import APIRouter

from proyecto_pruebas.models import m02

router = APIRouter(prefix="/predict", tags=["M02"])


@router.post("/m02", response_model=m02.M02Output)
def predict_m02(payload: m02.M02Input) -> m02.M02Output:
    """Estima la presión arterial sistólica (sysBP, en mmHg) de un paciente."""
    return m02.predict(payload)
