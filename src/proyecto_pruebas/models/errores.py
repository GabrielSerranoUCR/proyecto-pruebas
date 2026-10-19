"""
Modelo (MVC) de las respuestas de error comunes de la API.
Sigue el formato de referencia del enunciado: {"error", "campo", "detalle"}.
"""

from pydantic import BaseModel, Field


class ErrorCampo(BaseModel):
    """Error de validación de un campo de la solicitud."""

    campo: str | None = Field(
        description="Campo con error; null si el error es del cuerpo completo."
    )
    detalle: str = Field(description="Explicación del error.")


class ErrorRespuesta(BaseModel):
    """Cuerpo de toda respuesta de error (400, 404, 405 y 500)."""

    error: str = Field(description="Tipo de error.")
    campo: str | None = Field(
        default=None, description="Primer campo con error (solo en 400 por validación)."
    )
    detalle: str | None = Field(default=None, description="Explicación del primer error.")
    errores: list[ErrorCampo] | None = Field(
        default=None, description="Todos los errores de validación (solo en 400)."
    )


def mensaje_validacion(err: dict) -> str:
    """Traduce al español los errores de validación de Pydantic más comunes."""
    # Límites como 0.0 se muestran como 0
    ctx = {k: f"{v:g}" if isinstance(v, (int, float)) else v for k, v in err.get("ctx", {}).items()}
    if err["type"] == "missing" and len(err["loc"]) == 1:
        return "Se requiere un cuerpo JSON"
    mensajes = {
        "missing": "Campo requerido",
        "int_type": "Debe ser un número entero",
        "int_from_float": "Debe ser un número entero",
        "float_type": "Debe ser un número",
        "greater_than": f"El valor debe ser mayor que {ctx.get('gt')}",
        "greater_than_equal": f"El valor debe ser mayor o igual que {ctx.get('ge')}",
        "less_than": f"El valor debe ser menor que {ctx.get('lt')}",
        "less_than_equal": f"El valor debe ser menor o igual que {ctx.get('le')}",
        "string_type": "Debe ser una cadena de texto",
        "literal_error": "Valor no permitido; valores válidos: "
                         f"{str(ctx.get('expected', '')).replace(' or ', ' o ')}",
        "extra_forbidden": "Campo no permitido",
        "json_invalid": "El cuerpo de la solicitud no es un JSON válido",
        "model_attributes_type": "El cuerpo debe ser un objeto JSON",
        "dict_type": "El cuerpo debe ser un objeto JSON",
    }
    return mensajes.get(err["type"], err["msg"])
