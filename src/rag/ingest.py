"""Construcción de la base de conocimiento: Markdown, chunks, embeddings y LanceDB."""

import logging
from pathlib import Path

import lancedb
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_lancedb import LanceDB
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
            section.metadata["document_name"] = markdown_path.stem
        chunks.extend(size_splitter.split_documents(sections))

    logger.info("Chunks generados: %d", len(chunks))
    return chunks


# Nota: langchain-lancedb sobrescribe la clave "source" con la ruta de la base.
# Por eso el nombre del documento se guarda en "document_name".
def open_vector_store(embeddings: Embeddings, settings: Settings) -> LanceDB:
    """Abre la tabla de LanceDB con el modelo de embeddings indicado."""
    return LanceDB(
        embedding_function=embeddings,
        uri=settings.vector_store_directory,
        table_name=settings.vector_store_table_name,
    )


def rebuild_vector_store(chunks: list[Document], embeddings: Embeddings, settings: Settings) -> int:
    """Borra la tabla anterior y guarda los chunks por lotes. Es seguro repetirlo."""
    settings.vector_store_directory.mkdir(parents=True, exist_ok=True)

    # La librería no permite vaciar la tabla, así que se elimina y se vuelve a crear
    lancedb.connect(settings.vector_store_directory).drop_table(
        settings.vector_store_table_name, ignore_missing=True
    )
    vector_store = open_vector_store(embeddings, settings)

    batch_size = settings.embedding_batch_size
    for start_index in range(0, len(chunks), batch_size):
        vector_store.add_documents(chunks[start_index : start_index + batch_size])

    return len(chunks)
