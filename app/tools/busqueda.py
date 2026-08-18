import json
from langchain.tools import tool, ToolRuntime
from app.dominio.catalogo import ContextoBusqueda


def _emitir(runtime: ToolRuntime, origen: str, mensaje: str):
    runtime.stream_writer({"type": "status", "origen": origen, "message": mensaje})


@tool
def buscar_productos(query: str, mensaje_progreso: str, runtime: ToolRuntime[ContextoBusqueda]) -> str:
    """Devuelve el catálogo real disponible. query expresa lo que se desea encontrar."""
    _emitir(runtime, "buscar_productos", mensaje_progreso)
    return json.dumps(runtime.context.productos, ensure_ascii=False)


@tool
def buscar_ofertas(query: str, mensaje_progreso: str, runtime: ToolRuntime[ContextoBusqueda]) -> str:
    """Devuelve las ofertas reales disponibles."""
    _emitir(runtime, "buscar_ofertas", mensaje_progreso)
    return json.dumps(runtime.context.ofertas, ensure_ascii=False)


@tool
def mostrar_opciones_productos(titulo: str, mensaje: str, ids_productos: list[int], runtime: ToolRuntime[ContextoBusqueda]) -> str:
    """Muestra cards seleccionables de productos reales por ID."""
    ids = set(ids_productos)
    opciones = [p for p in runtime.context.productos if p["id"] in ids]
    runtime.stream_writer({
        "type": "opciones_productos", "modo": "productos",
        "titulo": titulo, "message": mensaje, "opciones": opciones,
    })
    return json.dumps(opciones, ensure_ascii=False)


@tool
def mostrar_opciones_ofertas(titulo: str, mensaje: str, ids_ofertas: list[int], runtime: ToolRuntime[ContextoBusqueda]) -> str:
    """Muestra cards seleccionables de ofertas reales por ID de oferta."""
    ids = set(ids_ofertas)
    opciones = [o for o in runtime.context.ofertas if o["id"] in ids]
    runtime.stream_writer({
        "type": "opciones_productos", "modo": "ofertas",
        "titulo": titulo, "message": mensaje, "opciones": opciones,
    })
    return json.dumps(opciones, ensure_ascii=False)
