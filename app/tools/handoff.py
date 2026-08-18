from typing import Literal
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import Command


@tool
def transferir_a_busqueda(
    motivo: str,
    mensaje_usuario: str,
    runtime: ToolRuntime,
) -> Command[Literal["busqueda"]]:
    """Transfiere a Búsqueda. mensaje_usuario describe de forma breve y natural qué se hará ahora."""
    runtime.stream_writer({
        "type": "status",
        "origen": "atencion",
        "message": mensaje_usuario,
    })

    ultimo_ai = next(
        mensaje for mensaje in reversed(runtime.state["messages"])
        if isinstance(mensaje, AIMessage)
    )
    tool_message = ToolMessage(
        content=f"Solicitud transferida: {motivo}",
        tool_call_id=runtime.tool_call_id,
    )
    return Command(
        goto="busqueda",
        update={
            "messages": [ultimo_ai, tool_message],
            "consulta_busqueda": motivo,
        },
        graph=Command.PARENT,
    )
