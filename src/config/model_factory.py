"""Fábrica de modelos. El resto del código nunca importa un proveedor concreto."""

# Creador universal de modelos de chat
from langchain.chat_models import init_chat_model

# Creador universal de modelos de embeddings
from langchain.embeddings import init_embeddings

# Tipo base de los modelos de embeddings
from langchain_core.embeddings import Embeddings

# Tipo base de los modelos de chat
from langchain_core.language_models import BaseChatModel

# Configuración del proyecto
from src.config.settings import ModelProvider, ModelSettings, Settings


# Crea un modelo de chat de cualquier proveedor
def create_chat_model(model_settings: ModelSettings, settings: Settings) -> BaseChatModel:
    """Crea un modelo de chat para cualquier proveedor soportado."""
    # Argumentos extra según el proveedor
    extra_arguments: dict = {}

    # Ollama necesita saber donde corre el servidor local
    # Solo Ollama necesita la dirección del servidor
    if model_settings.provider == ModelProvider.OLLAMA:
        # Agrega la dirección del servidor local
        extra_arguments["base_url"] = settings.ollama_base_url

    # Devuelve el modelo ya configurado
    return init_chat_model(
        model_settings.name,
        model_provider=model_settings.provider.value,
        temperature=model_settings.temperature,
        **extra_arguments,
    )


# Crea un modelo de embeddings
def create_embedding_model(model_settings: ModelSettings, settings: Settings) -> Embeddings:
    """Crea un modelo de embeddings. Solo algunos proveedores ofrecen embeddings."""
    # Guarda el proveedor para compararlo
    provider = model_settings.provider

    # Caso embeddings locales
    if provider == ModelProvider.OLLAMA:
        # Devuelve el modelo de embeddings configurado
        return init_embeddings(
            model_settings.name,
            provider="ollama",
            base_url=settings.ollama_base_url,
        )

    # Caso embeddings de Gemini
    if provider == ModelProvider.GOOGLE_GENAI:
        # Embeddings de Gemini con la llave del entorno
        return init_embeddings(model_settings.name, provider="google_genai")

    # OpenRouter expone embeddings con la API compatible de OpenAI
    # Caso embeddings vía OpenRouter
    if provider == ModelProvider.OPENROUTER:
        # Devuelve el modelo de embeddings configurado
        return init_embeddings(
            model_settings.name,
            provider="openai",
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            check_embedding_ctx_length=False,
        )

    # Error claro si el proveedor no ofrece embeddings
    raise ValueError(
        f"El proveedor '{provider.value}' no ofrece embeddings. "
        "Usa ollama, google_genai u openrouter."
    )


# Atajo para el modelo principal
def create_default_llm(settings: Settings) -> BaseChatModel:
    """Modelo principal que usarán los agentes."""
    # Usa la configuración del rol llm
    return create_chat_model(settings.llm, settings)


# Atajo para el modelo juez
def create_judge_model(settings: Settings) -> BaseChatModel:
    """Modelo juez para evaluar respuestas, independiente del principal."""
    # Usa la configuración del rol judge
    return create_chat_model(settings.judge, settings)


# Atajo para el modelo de embeddings
def create_default_embeddings(settings: Settings) -> Embeddings:
    """Embeddings usados tanto en la ingesta como en la consulta."""
    # Usa la configuración del rol embedding
    return create_embedding_model(settings.embedding, settings)
