"""Esquemas de la consulta entrante y de la respuesta del asistente."""

from pydantic import BaseModel, Field

from src.schemas.customer import CustomerIdentifier


class UserQuery(BaseModel):
    """Consulta de un usuario. El customer_id identifica quien pregunta en la sesión."""

    session_id: str = Field(min_length=1, max_length=64)
    customer_id: CustomerIdentifier
    question: str = Field(min_length=1, max_length=2000)


class AssistantAnswer(BaseModel):
    """Respuesta del asistente con las fuentes usadas."""

    session_id: str
    answer: str
    sources: list[str] = Field(default_factory=list)
