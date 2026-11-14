"""Probar el agente de políticas desde la terminal.

Uso con preguntas directas: uv run python scripts/ask_agent.py "pregunta"
Uso interactivo: uv run python scripts/ask_agent.py
"""

# Librería estándar
import sys

# Módulos del proyecto
from src.agents.policy_agent import ask_policy_agent, create_policy_agent
from src.config.model_factory import create_default_embeddings
from src.config.settings import get_settings
from src.tools.rag_tool import build_rag_tool


def print_agent_answer(agent, question: str) -> None:
    """Enviar la pregunta al agente e imprimir la respuesta con sus fuentes reales."""
    # Invocar el agente y obtener la respuesta con las fuentes de la tool
    answer = ask_policy_agent(agent, question, session_id="terminal")

    # Imprimir la pregunta, las consultas enviadas al RAG y la respuesta
    print(f"\nPREGUNTA: {question}")
    print(f"CONSULTAS AL RAG: {answer.search_queries}")
    print(f"\nRESPUESTA:\n{answer.answer}")

    # Imprimir solo las fuentes que el modelo usó y que existen en lo recuperado
    print("\nFUENTES USADAS:")
    # Avisar si la respuesta no se apoyó en ningún fragmento
    if not answer.sources:
        print("- Ninguna")
    for source in answer.sources:
        print(f"- {source}")


def main() -> None:
    # Cargar la configuración y construir la tool y el agente
    settings = get_settings()
    rag_tool = build_rag_tool(create_default_embeddings(settings), settings)
    agent = create_policy_agent(settings, rag_tool)

    # Si hay preguntas como argumentos, responder solo esas
    questions = sys.argv[1:]
    if questions:
        for question in questions:
            print_agent_answer(agent, question)
        return

    # Si no hay argumentos, preguntar en bucle hasta que se escriba salir o nada
    print("Escribe una pregunta. Enter vacío o 'salir' para terminar.")
    while True:
        question = input("\n> ").strip()
        if question.lower() in ("", "salir"):
            break
        print_agent_answer(agent, question)


# Correr solo si se ejecuta el archivo directamente
if __name__ == "__main__":
    main()
