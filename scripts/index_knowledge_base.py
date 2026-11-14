"""Construir la base de conocimiento: PDFs a Markdown, chunks, embeddings y LanceDB.

Uso: uv run python scripts/index_knowledge_base.py
"""

# Librería estándar
import logging

# Módulos del proyecto
from src.config.model_factory import create_default_embeddings
from src.config.settings import get_settings
from src.rag.document_converter import convert_pdfs_to_markdown
from src.rag.ingest import rebuild_vector_store, split_markdown_into_chunks

# Logger de este script
logger = logging.getLogger("index_knowledge_base")


def main() -> None:
    # Cargar la configuración y el formato de los logs
    settings = get_settings()
    logging.basicConfig(level=settings.log_level, format="%(levelname)s %(message)s")
    # Silenciar avisos de fuentes del lector de PDF
    logging.getLogger("pdfminer").setLevel(logging.ERROR)

    # Convertir los PDFs a Markdown
    markdown_paths = convert_pdfs_to_markdown(
        settings.raw_documents_directory, settings.markdown_documents_directory
    )
    # Dividir los Markdown en fragmentos
    chunks = split_markdown_into_chunks(markdown_paths, settings)
    # Crear el modelo de embeddings
    embeddings = create_default_embeddings(settings)
    # Guardar los fragmentos en LanceDB
    stored_chunks_count = rebuild_vector_store(chunks, embeddings, settings)
    # Informar cuántos fragmentos se guardaron
    logger.info("Chunks guardados en LanceDB: %d", stored_chunks_count)


# Correr solo si se ejecuta el archivo directamente
if __name__ == "__main__":
    main()
