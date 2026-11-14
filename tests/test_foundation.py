"""Pruebas de la etapa 1: esquemas, carga del CRM, chunking y fábrica de modelos."""

# Librería estándar
import sqlite3

# Librerías externas
import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from pydantic import ValidationError

# Módulos del proyecto
from src.config.model_factory import create_embedding_model
from src.config.settings import ModelProvider, ModelSettings, Settings
from src.rag.ingest import rebuild_vector_store, split_markdown_into_chunks
from src.schemas.query import UserQuery
from src.tools.crm_loader import read_customers_from_csv, write_customers_to_sqlite


# Probar la lectura del CSV
def test_csv_loader_discards_invalid_rows_and_normalizes_dates(settings_for_tests):
    # Leer los clientes del CSV
    customers = read_customers_from_csv(settings_for_tests.customers_csv_path)
    # Indexar los clientes por identificador
    by_identifier = {customer.customer_id: customer for customer in customers}

    # El cliente de ejemplo debe existir
    assert "BU79786" in by_identifier
    # La fecha debe quedar en formato ISO
    assert by_identifier["BU79786"].effective_to_date == "2011-02-24"
    # Casi todas las filas deben ser válidas
    assert len(customers) > 9000


# Probar el guardado en SQLite
def test_customers_are_stored_in_sqlite(settings_for_tests, tmp_path):
    # Leer los clientes del CSV
    customers = read_customers_from_csv(settings_for_tests.customers_csv_path)
    # Base temporal para la prueba
    database_path = tmp_path / "crm.db"
    # Guardar los clientes
    write_customers_to_sqlite(customers, database_path)

    # Abrir la base creada
    with sqlite3.connect(database_path) as connection:
        # Contar las filas guardadas
        stored_count = connection.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    # Verificar que se guardó todo
    assert stored_count == len(customers)


# Probar que se rechace un identificador malicioso
def test_query_rejects_invalid_customer_identifier():
    # Esperar un error de validación
    with pytest.raises(ValidationError):
        # Intento de inyección SQL como identificador
        UserQuery(session_id="s1", customer_id="'; DROP TABLE", question="hola")


# Probar la construcción de la base de conocimiento
def test_knowledge_base_is_built_with_fake_embeddings(settings_for_tests, tmp_path):
    # Markdown temporal
    markdown_path = tmp_path / "manual.md"
    # Escribir un texto largo para forzar varios fragmentos
    markdown_path.write_text("# Reclamos\n\n" + "Texto de prueba. " * 300, encoding="utf-8")

    # Dividir el Markdown en fragmentos
    chunks = split_markdown_into_chunks([markdown_path], settings_for_tests)
    # Guardar los fragmentos con embeddings falsos
    stored_count = rebuild_vector_store(
        chunks, DeterministicFakeEmbedding(size=16), settings_for_tests
    )

    # Verificar que se guardaron todos y hay más de uno
    assert stored_count == len(chunks) > 1
    # El nombre del documento quedó en los metadatos
    assert chunks[0].metadata["document_name"] == "manual"


# Probar el error de un proveedor sin embeddings
def test_embedding_factory_rejects_provider_without_embeddings():
    # Anthropic no ofrece embeddings
    anthropic_settings = ModelSettings(provider=ModelProvider.ANTHROPIC, name="any")
    # Esperar un error de valor
    with pytest.raises(ValueError):
        # Fallar con mensaje claro
        create_embedding_model(anthropic_settings, Settings())


# Probar el retriever híbrido y la tool
def test_hybrid_retriever_and_tool_return_cited_fragments(settings_for_tests, tmp_path):
    # Módulos del proyecto
    from src.rag.retriever import create_hybrid_retriever
    from src.tools.rag_tool import create_rag_tool

    # Markdown temporal
    markdown_path = tmp_path / "manual.md"
    # Escribir dos secciones de prueba
    markdown_path.write_text(
        "# Grúa\n\nEl banderazo de la grúa cuesta 75 dólares.\n\n"
        "# Pintura\n\nLa pintura se cobra por panel pintado.",
        encoding="utf-8",
    )
    # Embeddings falsos de 16 dimensiones
    embeddings = DeterministicFakeEmbedding(size=16)
    # Dividir el Markdown en fragmentos
    chunks = split_markdown_into_chunks([markdown_path], settings_for_tests)
    # Guardar los fragmentos
    rebuild_vector_store(chunks, embeddings, settings_for_tests)

    # Crear el retriever híbrido
    retriever = create_hybrid_retriever(embeddings, settings_for_tests)
    # Invocar la tool con una pregunta
    tool_answer = create_rag_tool(retriever).invoke({"question": "banderazo grúa"})

    # La respuesta incluye la fuente
    assert "[Fuente: manual]" in tool_answer
    # La respuesta contiene el fragmento esperado
    assert "banderazo" in tool_answer
