from langchain_openai import AzureChatOpenAI, ChatOpenAI

from app.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT,
    MODEL_API_KEY,
    MODEL_BASE_URL,
    MODEL_NAME,
    MODEL_TEMPERATURE,
)


def _azure_configurado() -> bool:
    valores = (
        AZURE_OPENAI_API_KEY,
        AZURE_OPENAI_ENDPOINT,
        AZURE_OPENAI_API_VERSION,
        AZURE_OPENAI_DEPLOYMENT,
    )
    return all(valor and valor.strip() for valor in valores)


def crear_modelo():
    """Crea Azure OpenAI si está configurado; si no, usa OpenAI-compatible."""

    if _azure_configurado():
        print(
            "[MODELO] Azure OpenAI | "
            f"deployment={AZURE_OPENAI_DEPLOYMENT} | "
            f"endpoint={AZURE_OPENAI_ENDPOINT}"
        )
        return AzureChatOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_DEPLOYMENT,
            temperature=MODEL_TEMPERATURE,
        )

    print(
        "[MODELO] OpenAI-compatible | "
        f"model={MODEL_NAME} | base_url={MODEL_BASE_URL}"
    )
    return ChatOpenAI(
        base_url=MODEL_BASE_URL,
        api_key=MODEL_API_KEY,
        model=MODEL_NAME,
        temperature=MODEL_TEMPERATURE,
    )


modelo = crear_modelo()
