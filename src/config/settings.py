"""Configuración central del proyecto. Todo se lee del archivo .env o del entorno."""

# Clase base para enumeraciones de texto
from enum import StrEnum

# Permite guardar en caché el resultado de una función
from functools import lru_cache

# Manejo de rutas de archivos
from pathlib import Path

# Base de modelos y validación de campos
from pydantic import BaseModel, Field

# Lectura de configuración desde el entorno
from pydantic_settings import BaseSettings, SettingsConfigDict


# Lista cerrada de proveedores de modelos permitidos
class ModelProvider(StrEnum):
    """Proveedores soportados. El valor coincide con el nombre que usa LangChain."""

    # Modelos locales con Ollama
    OLLAMA = "ollama"
    # Modelos accesibles vía OpenRouter
    OPENROUTER = "openrouter"
    # Modelos Gemini de Google
    GOOGLE_GENAI = "google_genai"
    # Modelos Grok de xAI
    XAI = "xai"
    # Modelos Claude de Anthropic
    ANTHROPIC = "anthropic"


# Datos de un modelo concreto
class ModelSettings(BaseModel):
    """Un modelo configurable por rol: proveedor, nombre y temperatura."""

    # Proveedor que sirve el modelo
    provider: ModelProvider
    # Nombre del modelo en el proveedor
    name: str
    # Creatividad de la respuesta limitada entre 0 y 2
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


# Configuración global del proyecto
class Settings(BaseSettings):
    """Variables de entorno, ej: LLM_PROVIDER, LLM_NAME y LLM_TEMPERATURE."""

    # Lee el archivo .env e ignora variables desconocidas
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Modelos por rol. Cambiar de local a pago es solo cambiar estas variables
    # Proveedor del modelo principal
    llm_provider: ModelProvider = ModelProvider.OLLAMA
    # Nombre del modelo principal
    llm_name: str = "qwen3:8b"
    # Temperatura del modelo principal
    llm_temperature: float = 0.0
    # Proveedor del modelo juez
    judge_provider: ModelProvider = ModelProvider.OLLAMA
    # Nombre del modelo juez
    judge_name: str = "qwen3:8b"
    # Temperatura del modelo juez
    judge_temperature: float = 0.0
    # Proveedor del modelo de embeddings
    embedding_provider: ModelProvider = ModelProvider.OLLAMA
    # Nombre del modelo de embeddings
    embedding_name: str = "bge-m3"

    # Conexiones. Las llaves de cada proveedor las lee LangChain directamente del entorno
    # Dirección del servidor Ollama local
    ollama_base_url: str = "http://localhost:11434"
    # Dirección de la API de OpenRouter
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    # Llave de OpenRouter, vacía por defecto
    openrouter_api_key: str = ""

    # Rutas de datos
    # Ruta del CSV de clientes
    customers_csv_path: Path = Path("data/synthetic/structured/AutoInsurance.csv")
    # Carpeta con los PDFs originales
    raw_documents_directory: Path = Path("data/raw")
    # Carpeta donde se guardan los Markdown convertidos
    markdown_documents_directory: Path = Path("data/processed/markdown")
    # Archivo de la base SQLite del CRM
    sqlite_database_path: Path = Path("data/processed/crm.db")
    # Carpeta de la base vectorial LanceDB
    vector_store_directory: Path = Path("data/vectorstore")
    # Nombre de la tabla de vectores
    vector_store_table_name: str = "insurance_documents"

    # Parámetros de chunking en caracteres
    # Tamaño máximo de cada fragmento en caracteres
    chunk_size: int = Field(default=1200, gt=0)
    # Caracteres compartidos entre fragmentos vecinos
    chunk_overlap: int = Field(default=150, ge=0)
    # Fragmentos enviados por lote al modelo de embeddings
    embedding_batch_size: int = Field(default=64, gt=0)

    # Recuperación híbrida: cuántos fragmentos devolver y el peso de cada método
    # Cantidad de fragmentos devueltos por búsqueda
    retrieval_top_k: int = Field(default=4, gt=0)
    # Peso de la búsqueda semántica
    dense_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    # Peso de la búsqueda por palabras clave
    bm25_weight: float = Field(default=0.5, ge=0.0, le=1.0)

    # API
    # Host donde escuchará la API
    api_host: str = "0.0.0.0"
    # Puerto de la API
    api_port: int = 8000

    # Nivel de detalle de los logs
    log_level: str = "INFO"

    # Se usa como atributo en lugar de método
    @property
    # Agrupa los datos del modelo principal
    def llm(self) -> ModelSettings:
        # Construye el objeto con los valores configurados
        return ModelSettings(
            provider=self.llm_provider, name=self.llm_name, temperature=self.llm_temperature
        )

    # Se usa como atributo en lugar de método
    @property
    # Agrupa los datos del modelo juez
    def judge(self) -> ModelSettings:
        # Construye el objeto con los valores configurados
        return ModelSettings(
            provider=self.judge_provider, name=self.judge_name, temperature=self.judge_temperature
        )

    # Se usa como atributo en lugar de método
    @property
    # Agrupa los datos del modelo de embeddings
    def embedding(self) -> ModelSettings:
        # Construye el objeto de embeddings con proveedor y nombre
        return ModelSettings(provider=self.embedding_provider, name=self.embedding_name)


# Evita leer el entorno más de una vez
@lru_cache
# Punto único para obtener la configuración
def get_settings() -> Settings:
    """Devuelve una única instancia de la configuración."""
    # Crea la configuración leyendo el entorno
    return Settings()
