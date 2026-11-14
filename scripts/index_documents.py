"""Ingesta completa: CSV a SQLite y PDFs a Markdown, chunks, embeddings y LanceDB.

Uso: uv run python scripts/index_documents.py [--skip-vectors]
"""

# Librería estándar
import argparse
import logging

# Módulos del proyecto
from src.config.model_factory import create_default_embeddings
from src.config.settings import get_settings
from src.rag.document_converter import convert_pdfs_to_markdown
from src.rag.ingest import rebuild_vector_store, split_markdown_into_chunks
from src.tools.crm_loader import read_customers_from_csv, write_customers_to_sqlite

# Logger de este script
logger = logging.getLogger("index_documents")


# Función principal de la ingesta
def main() -> None:
    # Definir los argumentos del script
    parser = argparse.ArgumentParser(description="Construye el CRM y la base de conocimiento")
    # Opción para omitir el cálculo de embeddings
    parser.add_argument(
        "--skip-vectors",
        action="store_true",
        help="Solo carga SQLite y genera Markdown, sin llamar al modelo de embeddings",
    )
    # Leer los argumentos recibidos
    arguments = parser.parse_args()

    # Cargar la configuración
    settings = get_settings()
    # Configurar el formato de los logs
    logging.basicConfig(level=settings.log_level, format="%(levelname)s %(message)s")
    # pdfminer emite avisos de fuentes que no afectan el resultado
    # Silenciar avisos de fuentes del lector de PDF
    logging.getLogger("pdfminer").setLevel(logging.ERROR)

    # Paso 1: datos estructurados hacia SQLite
    # Leer y validar los clientes
    customers = read_customers_from_csv(settings.customers_csv_path)
    # Guardar los clientes en SQLite
    stored_customers_count = write_customers_to_sqlite(customers, settings.sqlite_database_path)
    # Informar cuántos clientes se guardaron
    logger.info("Clientes guardados en SQLite: %d", stored_customers_count)

    # Paso 2: PDFs hacia Markdown
    # Convertir los PDFs a Markdown
    markdown_paths = convert_pdfs_to_markdown(
        settings.raw_documents_directory, settings.markdown_documents_directory
    )

    # Si se pidió omitir los embeddings
    if arguments.skip_vectors:
        # Terminar sin calcular embeddings
        return

    # Paso 3: chunks, embeddings y LanceDB
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
    # Iniciar la ingesta
    main()
