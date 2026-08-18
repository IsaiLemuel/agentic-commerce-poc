from fastapi import WebSocket, WebSocketDisconnect
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from app.config import MAX_INTERACCIONES
from app.graph.builder import graph


def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def _estado(thread_id: str):
    return graph.get_state(_config(thread_id))


async def _enviar_eventos(websocket: WebSocket, entrada: dict | Command, thread_id: str) -> bool:
    config = _config(thread_id)

    async for evento in graph.astream(entrada, config=config, stream_mode="custom"):
        if isinstance(evento, dict):
            await websocket.send_json(evento)

    estado = graph.get_state(config)
    if estado.interrupts:
        await websocket.send_json(estado.interrupts[0].value)

    finalizada = bool(estado.values.get("finalizada"))
    if finalizada:
        await websocket.send_json({
            "type": "session_end",
            "reason": estado.values.get("motivo_cierre", "finalizada"),
            "message": "Esta interacción terminó. Puedes iniciar una conversación nueva cuando quieras.",
        })
    return finalizada


async def _registrar_interaccion(websocket: WebSocket, thread_id: str) -> int | None:
    estado = _estado(thread_id)
    actual = int(estado.values.get("interacciones", 0))

    if estado.values.get("finalizada"):
        await websocket.send_json({"type": "session_end", "reason": "finalizada", "message": "Esta sesión ya terminó."})
        return None

    siguiente = actual + 1
    if siguiente > MAX_INTERACCIONES:
        await websocket.send_json({
            "type": "session_end",
            "reason": "limite_interacciones",
            "message": f"Llegamos al límite de {MAX_INTERACCIONES} interacciones de esta POC. Inicia una nueva conversación para continuar.",
        })
        return None

    await websocket.send_json({"type": "session_meta", "interacciones": siguiente, "max_interacciones": MAX_INTERACCIONES})
    return siguiente


async def websocket_nexo(websocket: WebSocket, thread_id: str):
    await websocket.accept()
    estado_inicial = _estado(thread_id)
    await websocket.send_json({
        "type": "connected",
        "thread_id": thread_id,
        "interacciones": int(estado_inicial.values.get("interacciones", 0)),
        "max_interacciones": MAX_INTERACCIONES,
    })

    try:
        while True:
            payload = await websocket.receive_json()
            tipo = payload.get("type")

            if tipo in {"message", "seleccion"}:
                numero = await _registrar_interaccion(websocket, thread_id)
                if numero is None:
                    await websocket.close(code=1000)
                    return

                if tipo == "message":
                    contenido = (payload.get("content") or "").strip()
                    if not contenido:
                        continue
                    entrada = {"messages": [HumanMessage(content=contenido)], "interacciones": numero}
                else:
                    producto_id = payload.get("producto_id")
                    nombre = payload.get("nombre", "producto")
                    modo = payload.get("modo", "productos")
                    origen = "una oferta mostrada" if modo == "ofertas" else "el catálogo mostrado"
                    entrada = {
                        "messages": [HumanMessage(content=f"Quiero seleccionar {nombre} (ID {producto_id}) desde {origen} y continuar con la compra.")],
                        "interacciones": numero,
                    }

                if await _enviar_eventos(websocket, entrada, thread_id):
                    await websocket.close(code=1000)
                    return

            elif tipo == "resume":
                if await _enviar_eventos(websocket, Command(resume=payload.get("data", {})), thread_id):
                    await websocket.close(code=1000)
                    return

    except WebSocketDisconnect:
        return
