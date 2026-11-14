"""Esquemas de la consulta entrante y de la respuesta del asistente."""

# Librerías externas
from pydantic import BaseModel, Field

# Módulos del proyecto
from src.schemas.customer import CustomerIdentifier


# Consulta que llega del usuario
class UserQuery(BaseModel):
    """Consulta de un usuario. El customer_id identifica quien pregunta en la sesión."""

    # Identificador de la sesión con largo limitado
    session_id: str = Field(min_length=1, max_length=64)
    # Cliente que pregunta, con formato validado
    customer_id: CustomerIdentifier
    # Pregunta con largo limitado para evitar abusos
    question: str = Field(min_length=1, max_length=2000)


# Consultas de búsqueda que genera el modelo a partir de la pregunta
class SearchPlan(BaseModel):
    """Plan de búsqueda. Una consulta por cada tema si la pregunta es compuesta."""

    # Consultas autocontenidas, entre una y tres
    queries: list[str] = Field(min_length=1, max_length=3)


# Respuesta estructurada del modelo antes de agregar las fuentes
class PolicyAnswer(BaseModel):
    """Respuesta del modelo con los ids de las fuentes que usó."""

    # Texto de la respuesta
    answer: str
    # Ids de las etiquetas source que sustentan la respuesta, vacío si no hay información
    used_source_ids: list[int] = Field(default_factory=list)


# Respuesta que devuelve el asistente
class AssistantAnswer(BaseModel):
    """Respuesta del asistente con las fuentes usadas."""

    # Sesión a la que pertenece la respuesta
    session_id: str
    # Texto de la respuesta
    answer: str
    # Consultas que se enviaron al RAG
    search_queries: list[str] = Field(default_factory=list)
    # Fuentes que el modelo usó, validadas contra lo recuperado
    sources: list[str] = Field(default_factory=list)
