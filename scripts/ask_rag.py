"""Probar el RAG desde la terminal.

Uso con preguntas directas: uv run python scripts/ask_rag.py "pregunta uno" "pregunta dos"
Uso interactivo: uv run python scripts/ask_rag.py
"""

# Librería estándar
import sys

# Módulos del proyecto
from src.config.model_factory import create_default_embeddings
from src.config.settings import get_settings
from src.rag.retriever import create_hybrid_retriever


def print_answer(retriever, question: str) -> None:
    """Buscar los fragmentos de una pregunta e imprimirlos con su fuente."""
    # Buscar los fragmentos más relevantes
    documents = retriever.invoke(question)

    # Imprimir la pregunta y cuántos fragmentos se encontraron
    print(f"\nPREGUNTA: {question}")
    print(f"Fragmentos encontrados: {len(documents)}")

    # Imprimir cada fragmento completo con su documento de origen
    for position, document in enumerate(documents, start=1):
        score = document.metadata.get("rerank_score")
        document_name = document.metadata.get("document_name")
        print(f"\n--- Fragmento {position} | {document_name} | puntaje {score}")
        print(document.page_content)


def main() -> None:
    # Cargar la configuración y construir el retriever híbrido
    settings = get_settings()
    retriever = create_hybrid_retriever(create_default_embeddings(settings), settings)

    # Si hay preguntas como argumentos, responder solo esas
    questions = sys.argv[1:]
    if questions:
        for question in questions:
            print_answer(retriever, question)
        return

    # Si no hay argumentos, preguntar en bucle hasta que se escriba salir o nada
    print("Escribe una pregunta. Enter vacío o 'salir' para terminar.")
    while True:
        question = input("\n> ").strip()
        if question.lower() in ("", "salir"):
            break
        print_answer(retriever, question)


# Correr solo si se ejecuta el archivo directamente
if __name__ == "__main__":
    main()
