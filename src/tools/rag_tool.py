"""Tool de LangChain que el agente de políticas usa para consultar los manuales."""

from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import BaseTool, tool

from src.config.settings import Settings
from src.rag.retriever import create_hybrid_retriever


def format_documents_with_citations(documents: list) -> str:
    """Une los fragmentos indicando el documento de origen para poder citarlo."""
    if not documents:
        return "No se encontró información relevante en los manuales."
    return "\n\n".join(
        f"[Fuente: {document.metadata.get('document_name', 'desconocida')}]\n"
        f"{document.page_content}"
        for document in documents
    )


def create_rag_tool(retriever: BaseRetriever) -> BaseTool:
    """Crea la tool sobre un retriever ya construido."""

    @tool
    def search_policy_documents(question: str) -> str:
        """Busca en los manuales de la aseguradora procedimientos, coberturas, costos y reclamos."""
        return format_documents_with_citations(retriever.invoke(question))

    return search_policy_documents


def build_rag_tool(embeddings: Embeddings, settings: Settings) -> BaseTool:
    """Atajo que construye el retriever híbrido y la tool juntos."""
    return create_rag_tool(create_hybrid_retriever(embeddings, settings))
