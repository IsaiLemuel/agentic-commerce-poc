import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

# Carga explícita del .env del proyecto, sin depender del directorio
# desde el que se ejecute uvicorn/python.
load_dotenv(ENV_FILE)

DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
SKILLS_DIR = BASE_DIR / "app" / "skills"

# ------------------------------------------------------------
# Modelo
# ------------------------------------------------------------
# Valores Azure. Si los cuatro están presentes, app/modelo.py
# seleccionará AzureChatOpenAI automáticamente.
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Fallback OpenAI-compatible / LM Studio.
MODEL_BASE_URL = os.getenv("MODEL_BASE_URL", "http://127.0.0.1:1234/v1")
MODEL_API_KEY = os.getenv("MODEL_API_KEY", "not-needed")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen/qwen3-vl-4b")
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.2"))

MAX_INTERACCIONES = int(os.getenv("MAX_INTERACCIONES", "12"))
