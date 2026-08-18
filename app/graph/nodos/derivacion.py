from langchain_core.messages import AIMessage
from langgraph.config import get_stream_writer
from app.graph.estado import Estado


async def nodo_derivacion(state: Estado):
    writer = get_stream_writer()
    producto = state.get("producto_seleccionado")
    writer({"type": "node_status", "node": "derivacion", "message": "Registrando la solicitud"})

    texto = "**Solicitud registrada.**"
    if producto:
        texto += f" Tu compra de **{producto['nombre']}** quedó preparada."
    texto += " Un ejecutivo humano continuará el proceso."

    writer({"type": "derivacion", "message": texto, "destino": "ejecutivo_humano"})
    return {
        "messages": [AIMessage(content=texto)],
        "finalizada": True,
        "motivo_cierre": "compra_registrada",
    }
