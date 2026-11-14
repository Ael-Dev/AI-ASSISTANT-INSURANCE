"""Probar el agente de políticas desde la terminal.

Uso con preguntas directas: uv run python scripts/ask_agent.py "pregunta"
Uso interactivo: uv run python scripts/ask_agent.py
"""

# Librería estándar
import sys

# Módulos del proyecto
from src.agents.policy_agent import create_policy_agent
from src.config.model_factory import create_default_embeddings
from src.config.settings import get_settings
from src.tools.rag_tool import build_rag_tool


def print_agent_answer(agent, question: str) -> None:
    """Enviar la pregunta al agente e imprimir las tools usadas y la respuesta."""
    # El usuario solo envía la pregunta, nunca el contexto
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})

    # Imprimir la pregunta
    print(f"\nPREGUNTA: {question}")

    # Imprimir cada tool que el agente decidió llamar
    for message in result["messages"]:
        for tool_call in getattr(message, "tool_calls", []):
            print(f"Tool llamada: {tool_call['name']} con {tool_call['args']}")

    # Imprimir la respuesta final
    print(f"\nRESPUESTA:\n{result['messages'][-1].content}")


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
