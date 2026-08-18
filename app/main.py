from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import STATIC_DIR
from app.comunicacion.websocket import websocket_nexo

app = FastAPI(title="NEXO Shop POC v2")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def inicio():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "nexo-shop-v2"}


@app.websocket("/ws/{thread_id}")
async def ws(websocket: WebSocket, thread_id: str):
    await websocket_nexo(websocket, thread_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
