"""Construcción de la base de conocimiento: Markdown, chunks, embeddings y ChromaDB."""

import logging
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from src.config.settings import Settings

logger = logging.getLogger(__name__)

# Encabezados Markdown que se conservan como metadatos de cada chunk
HEADERS_TO_SPLIT_ON = [("#", "section"), ("##", "subsection"), ("###", "topic")]


def split_markdown_into_chunks(markdown_paths: list[Path], settings: Settings) -> list[Document]:
    """Divide primero por encabezados y luego por tamaño para mantener el contexto."""
    header_splitter = MarkdownHeaderTextSplitter(HEADERS_TO_SPLIT_ON, strip_headers=False)
    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    chunks: list[Document] = []
    for markdown_path in markdown_paths:
        sections = header_splitter.split_text(markdown_path.read_text(encoding="utf-8"))
        for section in sections:
            section.metadata["source"] = markdown_path.stem
        chunks.extend(size_splitter.split_documents(sections))

    logger.info("Chunks generados: %d", len(chunks))
    return chunks


def create_vector_store(embeddings: Embeddings, settings: Settings) -> Chroma:
    """Abre la colección de ChromaDB con el modelo de embeddings indicado."""
    return Chroma(
        collection_name=settings.vector_store_collection_name,
        embedding_function=embeddings,
        persist_directory=str(settings.vector_store_directory),
    )


def rebuild_vector_store(chunks: list[Document], embeddings: Embeddings, settings: Settings) -> int:
    """Borra la colección anterior y guarda los chunks por lotes."""
    vector_store = create_vector_store(embeddings, settings)
    vector_store.reset_collection()

    batch_size = settings.embedding_batch_size
    for start_index in range(0, len(chunks), batch_size):
        vector_store.add_documents(chunks[start_index : start_index + batch_size])

    return len(chunks)
