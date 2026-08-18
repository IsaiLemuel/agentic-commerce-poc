from langchain.agents import create_agent
from app.modelo import modelo
from app.dominio.catalogo import ContextoBusqueda
from app.skills.loader import cargar_skills
from app.tools.busqueda import (
    buscar_productos,
    buscar_ofertas,
    mostrar_opciones_productos,
    mostrar_opciones_ofertas,
)
from app.tools.ui import mostrar_opciones_accion

SKILLS = cargar_skills("asesoria_comercial.md", "conversacion.md")

agente_busqueda = create_agent(
    model=modelo,
    tools=[
        buscar_productos,
        buscar_ofertas,
        mostrar_opciones_productos,
        mostrar_opciones_ofertas,
        mostrar_opciones_accion,
    ],
    context_schema=ContextoBusqueda,
    name="busqueda",
    system_prompt=f"""
Eres el especialista de búsqueda y recomendación de NEXO Shop.

Usa exclusivamente datos obtenidos mediante tus tools para cualquier dato comercial.
No tienes que limitarte a devolver tarjetas: también puedes comparar, recomendar, explicar y responder en Markdown.

REGLAS:
1. Para catálogo/precios/stock usa buscar_productos.
2. Para promociones usa buscar_ofertas.
3. Muestra cards solo cuando realmente ayudan a elegir.
4. Si consultaste ofertas y quieres mostrar cards, usa mostrar_opciones_ofertas.
5. Si el usuario necesita una comparación, puedes entregar una tabla Markdown con datos recuperados.
6. Si falta claridad, puedes mostrar opciones de acción concretas en vez de inventar una respuesta.
7. Los textos mensaje_progreso/titulo/mensaje son visibles: hazlos naturales, útiles y no repetitivos.
8. No inventes especificaciones ausentes en los JSON.
9. Después de usar tools, responde como un buen asesor, no como un log de sistema.

SKILLS INTERNAS:
{SKILLS}
""",
)
