"""Recuperación híbrida: búsqueda semántica en LanceDB más BM25 por palabras clave."""

# Librería estándar
import json

# Librerías externas
import lancedb
from langchain_classic.retrievers import ContextualCompressionRetriever, EnsembleRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict
from rank_bm25 import BM25Okapi

# Módulos del proyecto
from src.config.settings import Settings
from src.rag.ingest import open_vector_store
from src.rag.reranker import create_reranker


# Convertir un texto en palabras
def tokenize_text(text: str) -> list[str]:
    """Tokenización simple en minúsculas para BM25."""
    # Minúsculas y separación por espacios
    return text.lower().split()


# Retriever por palabras clave
class BM25DocumentRetriever(BaseRetriever):
    """Retriever por palabras clave sobre una lista fija de documentos."""

    # Permitir usar el tipo BM25Okapi como campo
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Fragmentos donde se busca
    documents: list[Document]
    # Índice BM25 ya calculado
    bm25_index: BM25Okapi
    # Cantidad de resultados a devolver
    top_k: int

    # Método que LangChain llama al buscar
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        # Puntuar cada fragmento contra la pregunta
        scores = self.bm25_index.get_scores(tokenize_text(query))
        # Ordenar las posiciones de mayor a menor puntaje
        ranked_positions = sorted(range(len(scores)), key=scores.__getitem__, reverse=True)
        # Devolver los mejores fragmentos
        return [self.documents[position] for position in ranked_positions[: self.top_k]]


# Cargar los fragmentos guardados en LanceDB
def load_stored_documents(settings: Settings) -> list[Document]:
    """Lee todos los chunks guardados en LanceDB para construir el índice BM25."""
    # Abrir la tabla de vectores
    table = lancedb.connect(settings.vector_store_directory).open_table(
        settings.vector_store_table_name
    )
    # Leer todas las filas como diccionarios
    stored_rows = table.to_arrow().to_pylist()
    # Convertir cada fila en un Document
    return [
        Document(page_content=row["text"], metadata=json.loads(row["metadata"]))
        for row in stored_rows
    ]


# Crear el retriever híbrido
def create_hybrid_retriever(embeddings: Embeddings, settings: Settings) -> BaseRetriever:
    """Combina semántico y BM25 con pesos, y aplica reranking si está activo."""
    # Retriever semántico sobre LanceDB
    dense_retriever = open_vector_store(embeddings, settings).as_retriever(
        search_kwargs={"k": settings.retrieval_candidates_k}
    )

    # Fragmentos para el índice BM25
    documents = load_stored_documents(settings)
    # Retriever por palabras clave
    bm25_retriever = BM25DocumentRetriever(
        documents=documents,
        bm25_index=BM25Okapi([tokenize_text(document.page_content) for document in documents]),
        top_k=settings.retrieval_candidates_k,
    )

    # Unir ambos retrievers según sus pesos
    ensemble_retriever = EnsembleRetriever(
        retrievers=[dense_retriever, bm25_retriever],
        weights=[settings.dense_weight, settings.bm25_weight],
    )

    # Devolver los candidatos sin reranking si está desactivado
    if not settings.rerank_enabled:
        return ensemble_retriever

    # Reordenar los candidatos y quedarse con los mejores
    return ContextualCompressionRetriever(
        base_compressor=create_reranker(settings),
        base_retriever=ensemble_retriever,
    )
