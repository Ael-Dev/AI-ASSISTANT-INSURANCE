"""Pruebas de la etapa 1: esquemas, carga del CRM, chunking y fábrica de modelos."""

import sqlite3

import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from pydantic import ValidationError

from src.config.model_factory import create_embedding_model
from src.config.settings import ModelProvider, ModelSettings, Settings
from src.rag.ingest import rebuild_vector_store, split_markdown_into_chunks
from src.schemas.query import UserQuery
from src.tools.crm_loader import read_customers_from_csv, write_customers_to_sqlite


def test_csv_loader_discards_invalid_rows_and_normalizes_dates(settings_for_tests):
    customers = read_customers_from_csv(settings_for_tests.customers_csv_path)
    by_identifier = {customer.customer_id: customer for customer in customers}

    assert "BU79786" in by_identifier
    assert by_identifier["BU79786"].effective_to_date == "2011-02-24"
    assert len(customers) > 9000


def test_customers_are_stored_in_sqlite(settings_for_tests, tmp_path):
    customers = read_customers_from_csv(settings_for_tests.customers_csv_path)
    database_path = tmp_path / "crm.db"
    write_customers_to_sqlite(customers, database_path)

    with sqlite3.connect(database_path) as connection:
        stored_count = connection.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    assert stored_count == len(customers)


def test_query_rejects_invalid_customer_identifier():
    with pytest.raises(ValidationError):
        UserQuery(session_id="s1", customer_id="'; DROP TABLE", question="hola")


def test_knowledge_base_is_built_with_fake_embeddings(settings_for_tests, tmp_path):
    markdown_path = tmp_path / "manual.md"
    markdown_path.write_text("# Reclamos\n\n" + "Texto de prueba. " * 300, encoding="utf-8")

    chunks = split_markdown_into_chunks([markdown_path], settings_for_tests)
    stored_count = rebuild_vector_store(
        chunks, DeterministicFakeEmbedding(size=16), settings_for_tests
    )

    assert stored_count == len(chunks) > 1
    assert chunks[0].metadata["document_name"] == "manual"


def test_embedding_factory_rejects_provider_without_embeddings():
    anthropic_settings = ModelSettings(provider=ModelProvider.ANTHROPIC, name="any")
    with pytest.raises(ValueError):
        create_embedding_model(anthropic_settings, Settings())


def test_hybrid_retriever_and_tool_return_cited_fragments(settings_for_tests, tmp_path):
    from src.rag.retriever import create_hybrid_retriever
    from src.tools.rag_tool import create_rag_tool

    markdown_path = tmp_path / "manual.md"
    markdown_path.write_text(
        "# Grúa\n\nEl banderazo de la grúa cuesta 75 dólares.\n\n"
        "# Pintura\n\nLa pintura se cobra por panel pintado.",
        encoding="utf-8",
    )
    embeddings = DeterministicFakeEmbedding(size=16)
    chunks = split_markdown_into_chunks([markdown_path], settings_for_tests)
    rebuild_vector_store(chunks, embeddings, settings_for_tests)

    retriever = create_hybrid_retriever(embeddings, settings_for_tests)
    tool_answer = create_rag_tool(retriever).invoke({"question": "banderazo grúa"})

    assert "[Fuente: manual]" in tool_answer
    assert "banderazo" in tool_answer
