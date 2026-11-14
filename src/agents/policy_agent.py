"""Agente de políticas: responde sobre los manuales usando la tool de búsqueda."""

# Librerías externas
from langchain.agents import create_agent
from langchain_core.tools import BaseTool

# Módulos del proyecto
from src.config.model_factory import create_default_llm
from src.config.settings import Settings
from src.prompts.system_prompts import POLICY_AGENT_SYSTEM_PROMPT


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
