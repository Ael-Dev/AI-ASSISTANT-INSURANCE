"""Construcción de la base de conocimiento: Markdown, chunks, embeddings y LanceDB."""

# Registro de mensajes
import logging

# Manejo de rutas de archivos
from pathlib import Path

# Cliente directo de LanceDB
import lancedb

# Tipo de fragmento con texto y metadatos
from langchain_core.documents import Document

# Tipo base de los modelos de embeddings
from langchain_core.embeddings import Embeddings

# Base vectorial LanceDB para LangChain
from langchain_lancedb import LanceDB

# Divisores de texto
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# Configuración del proyecto
from src.config.settings import Settings

# Logger propio de este módulo
logger = logging.getLogger(__name__)

# Encabezados Markdown que se conservan como metadatos de cada chunk
# Niveles de encabezado y su nombre de metadato
HEADERS_TO_SPLIT_ON = [("#", "section"), ("##", "subsection"), ("###", "topic")]


# Divide los Markdown en fragmentos
def split_markdown_into_chunks(markdown_paths: list[Path], settings: Settings) -> list[Document]:
    """Divide primero por encabezados y luego por tamaño para mantener el contexto."""
    # Divisor por encabezados que conserva los títulos
    header_splitter = MarkdownHeaderTextSplitter(HEADERS_TO_SPLIT_ON, strip_headers=False)
    # Divisor por tamaño con los parámetros configurados
    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    # Lista final de fragmentos
    chunks: list[Document] = []
    # Procesa cada Markdown
    for markdown_path in markdown_paths:
        # Lee el archivo y lo divide por encabezados
        sections = header_splitter.split_text(markdown_path.read_text(encoding="utf-8"))
        # Recorre cada sección
        for section in sections:
            # Guarda el nombre del documento para citarlo
            section.metadata["document_name"] = markdown_path.stem
        # Subdivide por tamaño y acumula
        chunks.extend(size_splitter.split_documents(sections))

    # Informa cuántos fragmentos hay
    logger.info("Chunks generados: %d", len(chunks))
    # Devuelve los fragmentos
    return chunks


# Nota: langchain-lancedb sobrescribe la clave "source" con la ruta de la base.
# Por eso el nombre del documento se guarda en "document_name".
# Abre la tabla de vectores
def open_vector_store(embeddings: Embeddings, settings: Settings) -> LanceDB:
    """Abre la tabla de LanceDB con el modelo de embeddings indicado."""
    # Devuelve la base vectorial configurada
    return LanceDB(
        embedding_function=embeddings,
        uri=settings.vector_store_directory,
        table_name=settings.vector_store_table_name,
    )


# Reconstruye la base vectorial desde cero
def rebuild_vector_store(chunks: list[Document], embeddings: Embeddings, settings: Settings) -> int:
    """Borra la tabla anterior y guarda los chunks por lotes. Es seguro repetirlo."""
    # Crea la carpeta de la base si no existe
    settings.vector_store_directory.mkdir(parents=True, exist_ok=True)

    # La librería no permite vaciar la tabla, así que se elimina y se vuelve a crear
    # Elimina la tabla anterior si existe
    lancedb.connect(settings.vector_store_directory).drop_table(
        settings.vector_store_table_name, ignore_missing=True
    )
    # Abre la tabla nueva
    vector_store = open_vector_store(embeddings, settings)

    # Tamaño de cada lote
    batch_size = settings.embedding_batch_size
    # Recorre los fragmentos por lotes
    for start_index in range(0, len(chunks), batch_size):
        # Calcula embeddings y guarda el lote
        vector_store.add_documents(chunks[start_index : start_index + batch_size])

    # Devuelve cuántos fragmentos se guardaron
    return len(chunks)
