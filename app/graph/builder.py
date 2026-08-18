from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.graph.estado import Estado
from app.graph.nodos.atencion import nodo_atencion
from app.graph.nodos.busqueda import nodo_busqueda
from app.graph.nodos.derivacion import nodo_derivacion

builder = StateGraph(Estado)
builder.add_node("atencion", nodo_atencion)
builder.add_node("busqueda", nodo_busqueda)
builder.add_node("derivacion", nodo_derivacion)
builder.add_edge(START, "atencion")
builder.add_edge("busqueda", END)
builder.add_edge("derivacion", END)

graph = builder.compile(checkpointer=MemorySaver())
