import json
from langchain.tools import tool, ToolRuntime


@tool
def mostrar_opciones_accion(
    titulo: str,
    mensaje: str,
    opciones: list[str],
    runtime: ToolRuntime,
) -> str:
    """Muestra de 2 a 4 acciones concretas para que el usuario elija cómo continuar."""
    opciones_limpias = [o.strip() for o in opciones if o and o.strip()][:4]
    runtime.stream_writer({
        "type": "opciones_accion",
        "titulo": titulo,
        "message": mensaje,
        "opciones": opciones_limpias,
    })
    return json.dumps(opciones_limpias, ensure_ascii=False)
