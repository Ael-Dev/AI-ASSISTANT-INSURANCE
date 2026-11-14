"""Fábrica de modelos. El resto del código nunca importa un proveedor concreto."""

from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

from src.config.settings import ModelProvider, ModelSettings, Settings


def create_chat_model(model_settings: ModelSettings, settings: Settings) -> BaseChatModel:
    """Crea un modelo de chat para cualquier proveedor soportado."""
    extra_arguments: dict = {}

    # Ollama necesita saber donde corre el servidor local
    if model_settings.provider == ModelProvider.OLLAMA:
        extra_arguments["base_url"] = settings.ollama_base_url

    return init_chat_model(
        model_settings.name,
        model_provider=model_settings.provider.value,
        temperature=model_settings.temperature,
        **extra_arguments,
    )


def create_embedding_model(model_settings: ModelSettings, settings: Settings) -> Embeddings:
    """Crea un modelo de embeddings. Solo algunos proveedores ofrecen embeddings."""
    provider = model_settings.provider

    if provider == ModelProvider.OLLAMA:
        return init_embeddings(
            model_settings.name,
            provider="ollama",
            base_url=settings.ollama_base_url,
        )

    if provider == ModelProvider.GOOGLE_GENAI:
        return init_embeddings(model_settings.name, provider="google_genai")

    # OpenRouter expone embeddings con la API compatible de OpenAI
    if provider == ModelProvider.OPENROUTER:
        return init_embeddings(
            model_settings.name,
            provider="openai",
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            check_embedding_ctx_length=False,
        )

    raise ValueError(
        f"El proveedor '{provider.value}' no ofrece embeddings. "
        "Usa ollama, google_genai u openrouter."
    )


def create_default_llm(settings: Settings) -> BaseChatModel:
    """Modelo principal que usarán los agentes."""
    return create_chat_model(settings.llm, settings)


def create_judge_model(settings: Settings) -> BaseChatModel:
    """Modelo juez para evaluar respuestas, independiente del principal."""
    return create_chat_model(settings.judge, settings)


def create_default_embeddings(settings: Settings) -> Embeddings:
    """Embeddings usados tanto en la ingesta como en la consulta."""
    return create_embedding_model(settings.embedding, settings)
