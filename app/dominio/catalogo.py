import json
from dataclasses import dataclass
from pathlib import Path
from app.config import DATA_DIR


def _cargar_json(nombre: str) -> list[dict]:
    ruta: Path = DATA_DIR / nombre
    with ruta.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


PRODUCTOS = _cargar_json("productos.json")
OFERTAS = _cargar_json("ofertas.json")


@dataclass(frozen=True)
class ContextoBusqueda:
    productos: list[dict]
    ofertas: list[dict]


CONTEXTO_BUSQUEDA = ContextoBusqueda(productos=PRODUCTOS, ofertas=OFERTAS)


def buscar_producto_por_id(producto_id: int) -> dict | None:
    return next((p for p in PRODUCTOS if p["id"] == producto_id), None)
