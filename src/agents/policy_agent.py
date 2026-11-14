"""Agente de políticas: responde sobre los manuales usando la tool de búsqueda."""

# Librerías externas
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool

# Módulos del proyecto
from src.config.model_factory import create_default_llm
from src.config.settings import Settings
from src.prompts.system_prompts import POLICY_AGENT_SYSTEM_PROMPT
from src.schemas.query import AssistantAnswer


# Crear el agente con el modelo configurado, la tool de búsqueda y su prompt
def create_policy_agent(settings: Settings, rag_tool: BaseTool):
    """El modelo se cambia por variables de entorno sin tocar este código."""
    # Devolver el agente de LangChain listo para invocar
    return create_agent(
        model=create_default_llm(settings),
        tools=[rag_tool],
        system_prompt=POLICY_AGENT_SYSTEM_PROMPT,
        name="policy_agent",
    )


# Obtener las fuentes reales de los resultados de tool, sin depender del modelo
def extract_sources(messages: list) -> list[str]:
    """Lee los artefactos de las tools y devuelve las fuentes sin repetir y en orden."""
    # Lista de fuentes en el orden en que se recuperaron
    sources: list[str] = []
    # Recorrer solo los mensajes que son resultados de tool
    for message in messages:
        if not isinstance(message, ToolMessage) or not message.artifact:
            continue
        # Armar el texto de cada fuente con su documento y su tema
        for item in message.artifact:
            source = f"{item['document_name']} | {item['topic']}".rstrip(" |")
            # Evitar fuentes repetidas
            if source not in sources:
                sources.append(source)
    # Devolver las fuentes únicas
    return sources


# Invocar el agente y devolver la respuesta con fuentes deterministas
def ask_policy_agent(agent, question: str, session_id: str) -> AssistantAnswer:
    """El usuario solo envía la pregunta. Las fuentes salen de lo que la tool recuperó."""
    # Enviar la pregunta al agente
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    # Devolver la respuesta del modelo con las fuentes reales de la tool
    return AssistantAnswer(
        session_id=session_id,
        answer=result["messages"][-1].content,
        sources=extract_sources(result["messages"]),
    )
