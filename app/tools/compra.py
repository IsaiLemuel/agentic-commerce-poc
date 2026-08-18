import json
from typing import Literal
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import Command, interrupt
from app.dominio.catalogo import buscar_producto_por_id, OFERTAS


@tool
def iniciar_compra(
    producto_id: int,
    usar_oferta: bool,
    mensaje_usuario: str,
    runtime: ToolRuntime,
) -> Command[Literal["derivacion"]]:
    """Inicia la compra de un producto real mediante formulario e interrupt."""
    producto = buscar_producto_por_id(producto_id)
    if not producto:
        return Command(update={"messages": [ToolMessage(content="Producto no encontrado.", tool_call_id=runtime.tool_call_id)]})

    producto_compra = dict(producto)
    if usar_oferta:
        oferta = next((o for o in OFERTAS if o.get("producto_id") == producto_id), None)
        if oferta:
            producto_compra.update({
                "precio_normal": oferta["precio_normal"],
                "precio": oferta["precio_oferta"],
                "descuento": oferta["descuento"],
                "es_oferta": True,
            })

    runtime.stream_writer({"type": "status", "origen": "compra", "message": mensaje_usuario})

    datos = interrupt({
        "type": "formulario",
        "id": "formulario_compra",
        "titulo": "Completa la solicitud",
        "descripcion": "Deja tus datos para que un ejecutivo continúe la compra.",
        "producto": producto_compra,
        "campos": [
            {"name": "nombre", "label": "Nombre", "type": "text", "placeholder": "Tu nombre", "required": True},
            {"name": "apellido", "label": "Apellido", "type": "text", "placeholder": "Tu apellido", "required": True},
            {"name": "email", "label": "Correo", "type": "email", "placeholder": "nombre@correo.cl", "required": True},
            {"name": "telefono", "label": "Teléfono", "type": "tel", "placeholder": "+56 9 ...", "required": False},
        ],
    })

    if isinstance(datos, dict) and datos.get("accion") == "cancelar":
        return Command(update={"messages": [ToolMessage(content="El usuario canceló la solicitud.", tool_call_id=runtime.tool_call_id)]})

    ultimo_ai = next(m for m in reversed(runtime.state["messages"]) if isinstance(m, AIMessage))
    tool_message = ToolMessage(
        content=json.dumps({"estado": "solicitud_completada", "producto": producto_compra, "datos": datos}, ensure_ascii=False),
        tool_call_id=runtime.tool_call_id,
    )
    return Command(
        goto="derivacion",
        update={"messages": [ultimo_ai, tool_message], "producto_seleccionado": producto_compra},
        graph=Command.PARENT,
    )
