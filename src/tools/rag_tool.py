"""Tool de LangChain que el agente de políticas usa para consultar los manuales.

El resultado vuelve al modelo como mensaje de tool y no como texto del usuario.
"""

# Librería estándar
from xml.sax.saxutils import escape, quoteattr

# Librerías externas
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import BaseTool, tool

# Módulos del proyecto
from src.config.settings import Settings
from src.rag.retriever import create_hybrid_retriever


# Dar formato XML a los fragmentos para que el modelo los trate como datos
def format_documents_as_sources(documents: list) -> str:
    """Envuelve cada fragmento en una etiqueta source con atributos que fija el sistema."""
    # Si la búsqueda no encontró nada
    if not documents:
        # Mensaje claro para el agente
        return "<sources></sources>"

    # Construir una etiqueta source por fragmento
    source_blocks = []
    for position, document in enumerate(documents, start=1):
        # Unir los títulos disponibles como sección del fragmento
        section_titles = [
            document.metadata[key]
            for key in ("section", "subsection", "topic")
            if key in document.metadata
        ]
        # Escapar los atributos para que no puedan romper la etiqueta
        attributes = (
            f"id={quoteattr(str(position))} "
            f"document={quoteattr(document.metadata.get('document_name', 'desconocido'))} "
            f"section={quoteattr(' > '.join(section_titles))}"
        )
        # Escapar el contenido para que no pueda cerrar la etiqueta ni abrir otras
        source_blocks.append(f"<source {attributes}>\n{escape(document.page_content)}\n</source>")

    # Devolver todos los fragmentos dentro de un único bloque
    return "<sources>\n" + "\n".join(source_blocks) + "\n</sources>"


# Crear la tool con un retriever dado
def create_rag_tool(retriever: BaseRetriever, max_documents: int = 3) -> BaseTool:
    """Crea la tool sobre un retriever ya construido. Devuelve como máximo max_documents."""

    # Registrar la función como tool y separar el texto para el modelo del artefacto para el sistema
    @tool(response_format="content_and_artifact")
    # Tool que el agente puede invocar
    def search_policy_documents(queries: list[str]) -> tuple[str, list[dict]]:
        """Busca en los manuales una o varias consultas sobre siniestros, coberturas y costos."""
        # Buscar cada consulta. Cada lista ya viene ordenada por el reranker
        results_per_query = [retriever.invoke(query) for query in queries]

        # Repartir los lugares por turnos entre las consultas, sin repetir fragmentos
        documents: list = []
        seen_contents: set[str] = set()
        for position in range(max(len(results) for results in results_per_query)):
            for results in results_per_query:
                if position < len(results) and results[position].page_content not in seen_contents:
                    seen_contents.add(results[position].page_content)
                    documents.append(results[position])
        # Conservar solo los primeros fragmentos del reparto
        documents = documents[:max_documents]

        # Devolver el XML para el modelo y los metadatos reales con el mismo id
        return format_documents_as_sources(documents), [
            {
                "id": position,
                "document_name": document.metadata.get("document_name", "desconocido"),
                "topic": document.metadata.get("topic")
                or document.metadata.get("subsection")
                or document.metadata.get("section", ""),
            }
            for position, document in enumerate(documents, start=1)
        ]

    # Devolver la tool creada
    return search_policy_documents


# Atajo que arma todo el RAG
def build_rag_tool(embeddings: Embeddings, settings: Settings) -> BaseTool:
    """Atajo que construye el retriever híbrido y la tool juntos."""
    # Crear el retriever y luego la tool
    return create_rag_tool(create_hybrid_retriever(embeddings, settings), settings.rerank_top_k)
