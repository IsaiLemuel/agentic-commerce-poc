from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class Estado(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    consulta_busqueda: str
    producto_seleccionado: dict | None
    interacciones: int
    finalizada: bool
    motivo_cierre: str
