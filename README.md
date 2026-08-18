# NEXO Shop POC v3

POC de tienda conversacional con LangChain `create_agent`, LangGraph, WebSocket y frontend HTML/CSS/JS.

## Qué cambió

- La compra **cierra realmente la interacción** y obliga a iniciar un `thread_id` nuevo.
- Existe un **máximo de interacciones por sesión** (`MAX_INTERACCIONES` en `app/config.py`).
- Las antiguas `guias.json` dejaron de fingir ser artículos del catálogo: ahora son **skills internas** en `app/skills/`.
- Catálogo y ofertas siguen separados como **datos comerciales de runtime**.
- El agente puede responder en **Markdown**, incluidas tablas.
- Puede mostrar **opciones de acción** cuando conviene que el usuario decida cómo seguir.
- El frontend se simplificó: conversación y resultados primero; eventos técnicos quedan secundarios.

## Ejecutar

1. Inicia LM Studio en `http://127.0.0.1:1234/v1` con el modelo configurado en `app/config.py`.
2. `pip install -r requirements.txt`
3. Desde la raíz: `python -m app.main`
4. Abre `http://127.0.0.1:8000`

## Separación conceptual

- `data/productos.json`: fuente real de productos.
- `data/ofertas.json`: fuente real de promociones.
- `app/skills/*.md`: criterio e instrucciones que puede usar la IA; **no se renderizan como productos ni artículos**.
- LangGraph: controla flujo, interrupt, cierre e invariantes.
- Agentes: comprenden, buscan, recomiendan y deciden cómo presentar el resultado.
