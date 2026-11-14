"""Reranker local: reordena los candidatos con un cross-encoder y se queda con los mejores."""

# Librería estándar
from collections.abc import Sequence

# Librerías externas
from fastembed.rerank.cross_encoder import TextCrossEncoder
from langchain_core.callbacks import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document
from pydantic import ConfigDict

# Módulos del proyecto
from src.config.settings import Settings


# Compresor de LangChain que reordena documentos por relevancia
class CrossEncoderReranker(BaseDocumentCompressor):
    """Puntúa cada candidato contra la pregunta y devuelve los mejores."""

    # Permitir el tipo TextCrossEncoder como campo
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Modelo cross-encoder ya cargado
    cross_encoder: TextCrossEncoder
    # Cantidad de fragmentos a devolver
    top_k: int

    def compress_documents(
        self, documents: Sequence[Document], query: str, callbacks: Callbacks = None
    ) -> Sequence[Document]:
        # Evitar puntuar si no hay candidatos
        if not documents:
            return []

        # Puntuar cada candidato contra la pregunta
        scores = list(
            self.cross_encoder.rerank(query, [document.page_content for document in documents])
        )
        # Ordenar los candidatos de mayor a menor puntaje
        ranked = sorted(zip(scores, documents), key=lambda pair: pair[0], reverse=True)

        # Guardar el puntaje en los metadatos y devolver solo los mejores
        best_documents = []
        for score, document in ranked[: self.top_k]:
            best_documents.append(
                Document(
                    page_content=document.page_content,
                    metadata={**document.metadata, "rerank_score": round(float(score), 4)},
                )
            )
        return best_documents


# Crear el reranker con el modelo configurado
def create_reranker(settings: Settings) -> CrossEncoderReranker:
    """Descarga el modelo la primera vez y lo reutiliza desde la carpeta de caché."""
    # Cargar el modelo cross-encoder en la carpeta de caché configurada
    cross_encoder = TextCrossEncoder(
        model_name=settings.rerank_model_name,
        cache_dir=str(settings.rerank_cache_directory),
        threads=settings.rerank_threads,
    )
    # Devolver el reranker con la cantidad final de fragmentos
    return CrossEncoderReranker(cross_encoder=cross_encoder, top_k=settings.rerank_top_k)
