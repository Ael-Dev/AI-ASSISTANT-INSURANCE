"""Esquemas de la consulta entrante y de la respuesta del asistente."""

# Base de modelos y validación de campos
from pydantic import BaseModel, Field

# Reutiliza el formato de identificador
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


# Respuesta que devuelve el asistente
class AssistantAnswer(BaseModel):
    """Respuesta del asistente con las fuentes usadas."""

    # Sesión a la que pertenece la respuesta
    session_id: str
    # Texto de la respuesta
    answer: str
    # Documentos usados, vacío por defecto
    sources: list[str] = Field(default_factory=list)
