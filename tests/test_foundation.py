"""Pruebas de la etapa 1: esquemas, carga del CRM, chunking y fábrica de modelos."""

# Base de datos SQLite incluida en Python
import sqlite3

# Framework de pruebas
import pytest

# Embeddings falsos y rápidos para probar
from langchain_core.embeddings import DeterministicFakeEmbedding

# Error que lanza Pydantic al validar
from pydantic import ValidationError

# Fábrica de embeddings
from src.config.model_factory import create_embedding_model

# Configuración del proyecto
from src.config.settings import ModelProvider, ModelSettings, Settings

# Fragmentación y carga en LanceDB
from src.rag.ingest import rebuild_vector_store, split_markdown_into_chunks

# Esquema de consulta
from src.schemas.query import UserQuery

# Carga del CRM
from src.tools.crm_loader import read_customers_from_csv, write_customers_to_sqlite


# Prueba la lectura del CSV
def test_csv_loader_discards_invalid_rows_and_normalizes_dates(settings_for_tests):
    # Lee los clientes del CSV
    customers = read_customers_from_csv(settings_for_tests.customers_csv_path)
    # Indexa los clientes por identificador
    by_identifier = {customer.customer_id: customer for customer in customers}

    # El cliente de ejemplo debe existir
    assert "BU79786" in by_identifier
    # La fecha debe quedar en formato ISO
    assert by_identifier["BU79786"].effective_to_date == "2011-02-24"
    # Casi todas las filas deben ser válidas
    assert len(customers) > 9000


# Prueba el guardado en SQLite
def test_customers_are_stored_in_sqlite(settings_for_tests, tmp_path):
    # Lee los clientes del CSV
    customers = read_customers_from_csv(settings_for_tests.customers_csv_path)
    # Base temporal para la prueba
    database_path = tmp_path / "crm.db"
    # Guarda los clientes
    write_customers_to_sqlite(customers, database_path)

    # Abre la base creada
    with sqlite3.connect(database_path) as connection:
        # Cuenta las filas guardadas
        stored_count = connection.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    # Debe haberse guardado todo
    assert stored_count == len(customers)


# Prueba que se rechace un identificador malicioso
def test_query_rejects_invalid_customer_identifier():
    # Se espera un error de validación
    with pytest.raises(ValidationError):
        # Intento de inyección SQL como identificador
        UserQuery(session_id="s1", customer_id="'; DROP TABLE", question="hola")


# Prueba la construcción de la base de conocimiento
def test_knowledge_base_is_built_with_fake_embeddings(settings_for_tests, tmp_path):
    # Markdown temporal
    markdown_path = tmp_path / "manual.md"
    # Escribe un texto largo para forzar varios fragmentos
    markdown_path.write_text("# Reclamos\n\n" + "Texto de prueba. " * 300, encoding="utf-8")

    # Divide el Markdown en fragmentos
    chunks = split_markdown_into_chunks([markdown_path], settings_for_tests)
    # Guarda los fragmentos con embeddings falsos
    stored_count = rebuild_vector_store(
        chunks, DeterministicFakeEmbedding(size=16), settings_for_tests
    )

    # Se guardaron todos y hay más de uno
    assert stored_count == len(chunks) > 1
    # El nombre del documento quedó en los metadatos
    assert chunks[0].metadata["document_name"] == "manual"


# Prueba el error de un proveedor sin embeddings
def test_embedding_factory_rejects_provider_without_embeddings():
    # Anthropic no ofrece embeddings
    anthropic_settings = ModelSettings(provider=ModelProvider.ANTHROPIC, name="any")
    # Se espera un error de valor
    with pytest.raises(ValueError):
        # Debe fallar con mensaje claro
        create_embedding_model(anthropic_settings, Settings())


# Prueba el retriever híbrido y la tool
def test_hybrid_retriever_and_tool_return_cited_fragments(settings_for_tests, tmp_path):
    # Constructor del retriever híbrido
    from src.rag.retriever import create_hybrid_retriever

    # Constructor de la tool
    from src.tools.rag_tool import create_rag_tool

    # Markdown temporal
    markdown_path = tmp_path / "manual.md"
    # Escribe dos secciones de prueba
    markdown_path.write_text(
        "# Grúa\n\nEl banderazo de la grúa cuesta 75 dólares.\n\n"
        "# Pintura\n\nLa pintura se cobra por panel pintado.",
        encoding="utf-8",
    )
    # Embeddings falsos de 16 dimensiones
    embeddings = DeterministicFakeEmbedding(size=16)
    # Divide el Markdown en fragmentos
    chunks = split_markdown_into_chunks([markdown_path], settings_for_tests)
    # Guarda los fragmentos
    rebuild_vector_store(chunks, embeddings, settings_for_tests)

    # Crea el retriever híbrido
    retriever = create_hybrid_retriever(embeddings, settings_for_tests)
    # Invoca la tool con una pregunta
    tool_answer = create_rag_tool(retriever).invoke({"question": "banderazo grúa"})

    # La respuesta incluye la fuente
    assert "[Fuente: manual]" in tool_answer
    # La respuesta contiene el fragmento esperado
    assert "banderazo" in tool_answer
