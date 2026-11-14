"""Ingesta completa: CSV a SQLite y PDFs a Markdown, chunks, embeddings y LanceDB.

Uso: uv run python scripts/index_documents.py [--skip-vectors]
"""

import argparse
import logging

from src.config.model_factory import create_default_embeddings
from src.config.settings import get_settings
from src.rag.document_converter import convert_pdfs_to_markdown
from src.rag.ingest import rebuild_vector_store, split_markdown_into_chunks
from src.tools.crm_loader import read_customers_from_csv, write_customers_to_sqlite

logger = logging.getLogger("index_documents")


def main() -> None:
    parser = argparse.ArgumentParser(description="Construye el CRM y la base de conocimiento")
    parser.add_argument(
        "--skip-vectors",
        action="store_true",
        help="Solo carga SQLite y genera Markdown, sin llamar al modelo de embeddings",
    )
    arguments = parser.parse_args()

    settings = get_settings()
    logging.basicConfig(level=settings.log_level, format="%(levelname)s %(message)s")
    # pdfminer emite avisos de fuentes que no afectan el resultado
    logging.getLogger("pdfminer").setLevel(logging.ERROR)

    # Paso 1: datos estructurados hacia SQLite
    customers = read_customers_from_csv(settings.customers_csv_path)
    stored_customers_count = write_customers_to_sqlite(customers, settings.sqlite_database_path)
    logger.info("Clientes guardados en SQLite: %d", stored_customers_count)

    # Paso 2: PDFs hacia Markdown
    markdown_paths = convert_pdfs_to_markdown(
        settings.raw_documents_directory, settings.markdown_documents_directory
    )

    if arguments.skip_vectors:
        return

    # Paso 3: chunks, embeddings y LanceDB
    chunks = split_markdown_into_chunks(markdown_paths, settings)
    embeddings = create_default_embeddings(settings)
    stored_chunks_count = rebuild_vector_store(chunks, embeddings, settings)
    logger.info("Chunks guardados en LanceDB: %d", stored_chunks_count)


if __name__ == "__main__":
    main()
