"""Configuración central del proyecto. Todo se lee del archivo .env o del entorno."""

from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelProvider(StrEnum):
    """Proveedores soportados. El valor coincide con el nombre que usa LangChain."""

    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    GOOGLE_GENAI = "google_genai"
    XAI = "xai"
    ANTHROPIC = "anthropic"


class ModelSettings(BaseModel):
    """Un modelo configurable por rol: proveedor, nombre y temperatura."""

    provider: ModelProvider
    name: str
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


class Settings(BaseSettings):
    """Variables de entorno, ej: LLM_PROVIDER, LLM_NAME y LLM_TEMPERATURE."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Modelos por rol. Cambiar de local a pago es solo cambiar estas variables
    llm_provider: ModelProvider = ModelProvider.OLLAMA
    llm_name: str = "qwen3:8b"
    llm_temperature: float = 0.0
    judge_provider: ModelProvider = ModelProvider.OLLAMA
    judge_name: str = "qwen3:8b"
    judge_temperature: float = 0.0
    embedding_provider: ModelProvider = ModelProvider.OLLAMA
    embedding_name: str = "bge-m3"

    # Conexiones. Las llaves de cada proveedor las lee LangChain directamente del entorno
    ollama_base_url: str = "http://localhost:11434"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_api_key: str = ""

    # Rutas de datos
    customers_csv_path: Path = Path("data/synthetic/structured/AutoInsurance.csv")
    raw_documents_directory: Path = Path("data/raw")
    markdown_documents_directory: Path = Path("data/processed/markdown")
    sqlite_database_path: Path = Path("data/processed/crm.db")
    vector_store_directory: Path = Path("data/vectorstore")
    vector_store_collection_name: str = "insurance_documents"

    # Parámetros de chunking en caracteres
    chunk_size: int = Field(default=1200, gt=0)
    chunk_overlap: int = Field(default=150, ge=0)
    embedding_batch_size: int = Field(default=64, gt=0)

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    log_level: str = "INFO"

    @property
    def llm(self) -> ModelSettings:
        return ModelSettings(
            provider=self.llm_provider, name=self.llm_name, temperature=self.llm_temperature
        )

    @property
    def judge(self) -> ModelSettings:
        return ModelSettings(
            provider=self.judge_provider, name=self.judge_name, temperature=self.judge_temperature
        )

    @property
    def embedding(self) -> ModelSettings:
        return ModelSettings(provider=self.embedding_provider, name=self.embedding_name)


@lru_cache
def get_settings() -> Settings:
    """Devuelve una única instancia de la configuración."""
    return Settings()
