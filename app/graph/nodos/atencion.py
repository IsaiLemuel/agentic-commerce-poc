from langchain_core.messages import AIMessage
from langgraph.config import get_stream_writer
from app.agentes.atencion import agente_atencion
from app.graph.estado import Estado


async def nodo_atencion(state: Estado):
    writer = get_stream_writer()
    writer({"type": "node_status", "node": "atencion", "message": "NEXO está contigo"})

    resultado = await agente_atencion.ainvoke({"messages": state.get("messages", [])})

    for mensaje in reversed(resultado["messages"]):
        if isinstance(mensaje, AIMessage) and mensaje.content and not mensaje.tool_calls:
            writer({"type": "message", "content": mensaje.content})
            break

    return {"messages": resultado["messages"]}
