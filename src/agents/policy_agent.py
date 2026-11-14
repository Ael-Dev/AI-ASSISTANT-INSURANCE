"""Agente de políticas: reformula, consulta el RAG de forma obligatoria y responde.

Es un grafo de LangGraph con tres pasos fijos. El modelo no decide si consulta el RAG.
"""

# Librería estándar
from typing import TypedDict

# Librerías externas
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph

# Módulos del proyecto
from src.config.model_factory import create_default_llm
from src.config.settings import Settings
from src.prompts.system_prompts import POLICY_AGENT_SYSTEM_PROMPT, QUERY_REWRITE_SYSTEM_PROMPT
from src.schemas.query import AssistantAnswer, PolicyAnswer, SearchPlan


# Datos que viajan entre los pasos del grafo
class PolicyState(TypedDict, total=False):
    # Pregunta original del usuario
    question: str
    # Consultas reformuladas para el RAG
    search_queries: list[str]
    # Resultado de la tool con los fragmentos y su artefacto
    retrieval_message: ToolMessage
    # Respuesta estructurada del modelo
    policy_answer: PolicyAnswer


# Elegir las fuentes que el modelo declaró usar, descartando ids inválidos
def select_used_sources(artifact: list[dict], used_source_ids: list[int]) -> list[str]:
    """Solo pasan los ids que existen en lo recuperado. El modelo no puede inventar fuentes."""
    # Armar el texto de cada fuente usada en el orden recuperado
    sources: list[str] = []
    for item in artifact:
        if item["id"] in used_source_ids:
            source = f"{item['document_name']} | {item['topic']}".rstrip(" |")
            # Evitar fuentes repetidas
            if source not in sources:
                sources.append(source)
    # Devolver las fuentes válidas y únicas
    return sources


# Crear el grafo: reformular, recuperar y responder
def create_policy_agent(settings: Settings, rag_tool: BaseTool):
    """El modelo se cambia por variables de entorno sin tocar este código."""
    # Crear el modelo configurado
    model = create_default_llm(settings)
    # Modelo que devuelve el plan de búsqueda validado con Pydantic
    query_planner = model.with_structured_output(SearchPlan)
    # Modelo que devuelve la respuesta validada con Pydantic
    answer_model = model.with_structured_output(PolicyAnswer)

    # Paso 1: reformular la pregunta o separarla si es compuesta
    def rewrite_question(state: PolicyState) -> dict:
        # Pedir el plan de búsqueda al modelo
        plan = query_planner.invoke(
            [SystemMessage(QUERY_REWRITE_SYSTEM_PROMPT), HumanMessage(state["question"])]
        )
        # Usar la pregunta original si el modelo no devolvió un plan válido
        queries = plan.queries if plan else [state["question"]]
        return {"search_queries": queries}

    # Paso 2: consultar el RAG siempre, sin dejarlo a decisión del modelo
    def retrieve_documents(state: PolicyState) -> dict:
        # Armar la llamada a la tool como si la hubiera pedido el modelo
        tool_call = {
            "name": rag_tool.name,
            "args": {"queries": state["search_queries"]},
            "id": "forced_retrieval",
            "type": "tool_call",
        }
        # Ejecutar la tool y guardar su ToolMessage con el artefacto
        return {"retrieval_message": rag_tool.invoke(tool_call)}

    # Paso 3: responder con los fragmentos recibidos como resultado de tool
    def generate_answer(state: PolicyState) -> dict:
        # Reconstruir el turno: pregunta, llamada a la tool y resultado de la tool
        messages = [
            SystemMessage(POLICY_AGENT_SYSTEM_PROMPT),
            HumanMessage(state["question"]),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": rag_tool.name,
                        "args": {"queries": state["search_queries"]},
                        "id": "forced_retrieval",
                    }
                ],
            ),
            state["retrieval_message"],
        ]
        # Obtener la respuesta validada por Pydantic
        return {"policy_answer": answer_model.invoke(messages)}

    # Unir los pasos en orden fijo
    graph = StateGraph(PolicyState)
    graph.add_node("rewrite_question", rewrite_question)
    graph.add_node("retrieve_documents", retrieve_documents)
    graph.add_node("generate_answer", generate_answer)
    graph.add_edge(START, "rewrite_question")
    graph.add_edge("rewrite_question", "retrieve_documents")
    graph.add_edge("retrieve_documents", "generate_answer")
    graph.add_edge("generate_answer", END)

    # Devolver el grafo compilado
    return graph.compile()


# Invocar el grafo y devolver la respuesta con las fuentes realmente usadas
def ask_policy_agent(agent, question: str, session_id: str) -> AssistantAnswer:
    """El usuario solo envía la pregunta. Las fuentes se validan contra lo recuperado."""
    # Ejecutar los tres pasos
    state = agent.invoke({"question": question})
    # Tomar la respuesta del modelo y el artefacto de la tool
    policy_answer = state["policy_answer"]
    artifact = state["retrieval_message"].artifact
    # Devolver la respuesta con las fuentes que el modelo declaró y existen
    return AssistantAnswer(
        session_id=session_id,
        answer=policy_answer.answer,
        search_queries=state["search_queries"],
        sources=select_used_sources(artifact, policy_answer.used_source_ids),
    )
