"""Recuperación híbrida: búsqueda semántica en LanceDB más BM25 por palabras clave."""

import json

import lancedb
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict
from rank_bm25 import BM25Okapi

from src.config.settings import Settings
from src.rag.ingest import open_vector_store


def tokenize_text(text: str) -> list[str]:
    """Tokenización simple en minúsculas para BM25."""
    return text.lower().split()


class BM25DocumentRetriever(BaseRetriever):
    """Retriever por palabras clave sobre una lista fija de documentos."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    documents: list[Document]
    bm25_index: BM25Okapi
    top_k: int

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        scores = self.bm25_index.get_scores(tokenize_text(query))
        ranked_positions = sorted(range(len(scores)), key=scores.__getitem__, reverse=True)
        return [self.documents[position] for position in ranked_positions[: self.top_k]]


def load_stored_documents(settings: Settings) -> list[Document]:
    """Lee todos los chunks guardados en LanceDB para construir el índice BM25."""
    table = lancedb.connect(settings.vector_store_directory).open_table(
        settings.vector_store_table_name
    )
    stored_rows = table.to_arrow().to_pylist()
    return [
        Document(page_content=row["text"], metadata=json.loads(row["metadata"]))
        for row in stored_rows
    ]


def create_hybrid_retriever(embeddings: Embeddings, settings: Settings) -> EnsembleRetriever:
    """Combina el retriever semántico y BM25 con los pesos definidos en la configuración."""
    dense_retriever = open_vector_store(embeddings, settings).as_retriever(
        search_kwargs={"k": settings.retrieval_top_k}
    )

    documents = load_stored_documents(settings)
    bm25_retriever = BM25DocumentRetriever(
        documents=documents,
        bm25_index=BM25Okapi([tokenize_text(document.page_content) for document in documents]),
        top_k=settings.retrieval_top_k,
    )

    return EnsembleRetriever(
        retrievers=[dense_retriever, bm25_retriever],
        weights=[settings.dense_weight, settings.bm25_weight],
    )
