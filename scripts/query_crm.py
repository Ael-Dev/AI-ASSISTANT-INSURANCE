"""Probar el CRM en SQLite desde la terminal.

Uso con un cliente: uv run python scripts/query_crm.py BU79786
Uso interactivo: uv run python scripts/query_crm.py
Sin cliente muestra además un resumen de la tabla.
"""

# Librería estándar
import sqlite3
import sys

# Módulos del proyecto
from src.config.settings import get_settings
from src.schemas.customer import Customer
from src.tools.crm_loader import CUSTOMERS_TABLE_NAME


def print_customer(connection: sqlite3.Connection, customer_id: str) -> None:
    """Consultar un cliente por su identificador e imprimir todos sus campos."""
    # Validar el formato del identificador antes de consultar
    if len(customer_id) != 7:
        print(f"Identificador inválido: {customer_id}")
        return

    # Consultar con parámetro para evitar inyección SQL
    cursor = connection.execute(
        f"SELECT * FROM {CUSTOMERS_TABLE_NAME} WHERE customer_id = ?", (customer_id,)
    )
    row = cursor.fetchone()

    # Avisar si el cliente no existe
    if row is None:
        print(f"Cliente no encontrado: {customer_id}")
        return

    # Imprimir cada columna con su valor
    print(f"\nCLIENTE: {customer_id}")
    for column_name, value in zip(Customer.model_fields.keys(), row):
        print(f"  {column_name}: {value}")


def print_summary(connection: sqlite3.Connection) -> None:
    """Imprimir un resumen general de la tabla."""
    # Contar los clientes guardados
    total = connection.execute(f"SELECT COUNT(*) FROM {CUSTOMERS_TABLE_NAME}").fetchone()[0]
    print(f"Clientes en la tabla: {total}")

    # Contar clientes por tipo de cobertura
    print("Clientes por cobertura:")
    for coverage, count in connection.execute(
        f"SELECT coverage, COUNT(*) FROM {CUSTOMERS_TABLE_NAME} GROUP BY coverage"
    ):
        print(f"  {coverage}: {count}")

    # Mostrar clientes con quejas abiertas como ejemplo
    print("Ejemplo de clientes con quejas abiertas:")
    for customer_id, complaints in connection.execute(
        f"SELECT customer_id, number_of_open_complaints FROM {CUSTOMERS_TABLE_NAME} "
        "WHERE number_of_open_complaints > 0 LIMIT 3"
    ):
        print(f"  {customer_id}: {complaints} quejas")


def main() -> None:
    # Abrir la base SQLite configurada
    settings = get_settings()
    connection = sqlite3.connect(settings.sqlite_database_path)

    # Si hay identificadores como argumentos, consultar solo esos
    customer_ids = sys.argv[1:]
    if customer_ids:
        for customer_id in customer_ids:
            print_customer(connection, customer_id)
        return

    # Sin argumentos, mostrar el resumen y consultar en bucle
    print_summary(connection)
    print("\nEscribe un customer_id. Enter vacío o 'salir' para terminar.")
    while True:
        customer_id = input("\n> ").strip()
        if customer_id.lower() in ("", "salir"):
            break
        print_customer(connection, customer_id)


# Correr solo si se ejecuta el archivo directamente
if __name__ == "__main__":
    main()
