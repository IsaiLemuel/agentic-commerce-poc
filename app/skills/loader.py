from pathlib import Path
from app.config import SKILLS_DIR


def cargar_skills(*nombres: str) -> str:
    bloques: list[str] = []
    for nombre in nombres:
        ruta: Path = SKILLS_DIR / nombre
        bloques.append(ruta.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(bloques)
