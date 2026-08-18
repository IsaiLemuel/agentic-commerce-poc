from langchain_core.messages import HumanMessage, AIMessage
from langgraph.config import get_stream_writer
from app.agentes.busqueda import agente_busqueda
from app.dominio.catalogo import CONTEXTO_BUSQUEDA
from app.graph.estado import Estado


async def nodo_busqueda(state: Estado):
    writer = get_stream_writer()
    writer({"type": "node_status", "node": "busqueda", "message": "Especialista de búsqueda activo"})

    historial = state.get("messages", [])
    consulta = state.get("consulta_busqueda", "")
    tarea_interna = HumanMessage(content=(
        "[TAREA INTERNA]\n"
        f"Solicitud: {consulta}\n\n"
        "Resuelve esta tarea ahora usando tus tools. "
        "Cuando corresponda, genera también la estructura visual adecuada para la interfaz."
    ))
    entrada = historial + [tarea_interna]

    resultado = await agente_busqueda.ainvoke(
        {"messages": entrada},
        context=CONTEXTO_BUSQUEDA,
    )
    mensajes_nuevos = resultado["messages"][len(entrada):]

    for mensaje in reversed(mensajes_nuevos):
        if isinstance(mensaje, AIMessage) and mensaje.content and not mensaje.tool_calls:
            writer({"type": "message", "content": mensaje.content})
            break

    return {"messages": mensajes_nuevos, "consulta_busqueda": ""}
