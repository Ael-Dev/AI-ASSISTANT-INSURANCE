"""Tool de LangChain que el agente de políticas usa para consultar los manuales."""

# Librerías externas
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import BaseTool, tool

# Módulos del proyecto
from src.config.settings import Settings
from src.rag.retriever import create_hybrid_retriever


# Dar formato a los fragmentos con su fuente
def format_documents_with_citations(documents: list) -> str:
    """Une los fragmentos indicando el documento de origen para poder citarlo."""
    # Si la búsqueda no encontró nada
    if not documents:
        # Mensaje claro para el agente
        return "No se encontró información relevante en los manuales."
    # Unir los fragmentos separados por línea en blanco
    return "\n\n".join(
        f"[Fuente: {document.metadata.get('document_name', 'desconocida')}]\n"
        f"{document.page_content}"
        for document in documents
    )


# Crear la tool con un retriever dado
def create_rag_tool(retriever: BaseRetriever) -> BaseTool:
    """Crea la tool sobre un retriever ya construido."""

    # Registrar la función como tool de LangChain
    @tool
    # Tool que el agente puede invocar
    def search_policy_documents(question: str) -> str:
        """Busca en los manuales de la aseguradora procedimientos, coberturas, costos y reclamos."""
        # Buscar y devolver fragmentos con fuente
        return format_documents_with_citations(retriever.invoke(question))

    # Devolver la tool creada
    return search_policy_documents


# Atajo que arma todo el RAG
def build_rag_tool(embeddings: Embeddings, settings: Settings) -> BaseTool:
    """Atajo que construye el retriever híbrido y la tool juntos."""
    # Crear el retriever y luego la tool
    return create_rag_tool(create_hybrid_retriever(embeddings, settings))
