"""Construcción de la base de conocimiento: Markdown, chunks, embeddings y LanceDB."""

# Librería estándar
import logging
from pathlib import Path

# Librerías externas
import lancedb
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_lancedb import LanceDB
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# Módulos del proyecto
from src.config.settings import Settings

# Logger propio de este módulo
logger = logging.getLogger(__name__)

# Encabezados Markdown que se conservan como metadatos de cada chunk
# Niveles de encabezado y su nombre de metadato
HEADERS_TO_SPLIT_ON = [("#", "section"), ("##", "subsection"), ("###", "topic")]


# Dividir los Markdown en fragmentos
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
    # Procesar cada Markdown
    for markdown_path in markdown_paths:
        # Leer el archivo y dividirlo por encabezados
        sections = header_splitter.split_text(markdown_path.read_text(encoding="utf-8"))
        # Recorrer cada sección
        for section in sections:
            # Guardar el nombre del documento para citarlo
            section.metadata["document_name"] = markdown_path.stem
        # Subdividir por tamaño y acumular
        chunks.extend(size_splitter.split_documents(sections))

    # Informar cuántos fragmentos hay
    logger.info("Chunks generados: %d", len(chunks))
    # Devolver los fragmentos
    return chunks


# Nota: langchain-lancedb sobrescribe la clave "source" con la ruta de la base.
# Por eso el nombre del documento se guarda en "document_name".
# Abrir la tabla de vectores
def open_vector_store(embeddings: Embeddings, settings: Settings) -> LanceDB:
    """Abre la tabla de LanceDB con el modelo de embeddings indicado."""
    # Devolver la base vectorial configurada
    return LanceDB(
        embedding_function=embeddings,
        uri=settings.vector_store_directory,
        table_name=settings.vector_store_table_name,
    )


# Reconstruir la base vectorial desde cero
def rebuild_vector_store(chunks: list[Document], embeddings: Embeddings, settings: Settings) -> int:
    """Borra la tabla anterior y guarda los chunks por lotes. Es seguro repetirlo."""
    # Crear la carpeta de la base si no existe
    settings.vector_store_directory.mkdir(parents=True, exist_ok=True)

    # La librería no permite vaciar la tabla, así que se elimina y se vuelve a crear
    # Eliminar la tabla anterior si existe
    lancedb.connect(settings.vector_store_directory).drop_table(
        settings.vector_store_table_name, ignore_missing=True
    )
    # Abrir la tabla nueva
    vector_store = open_vector_store(embeddings, settings)

    # Tamaño de cada lote
    batch_size = settings.embedding_batch_size
    # Recorrer los fragmentos por lotes
    for start_index in range(0, len(chunks), batch_size):
        # Calcular embeddings y guardar el lote
        vector_store.add_documents(chunks[start_index : start_index + batch_size])

    # Devolver cuántos fragmentos se guardaron
    return len(chunks)
