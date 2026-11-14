"""Carga del CSV de clientes hacia SQLite, validando cada fila con Pydantic."""

# Librería estándar
import csv
import logging
import sqlite3
from pathlib import Path

# Librerías externas
from pydantic import ValidationError

# Módulos del proyecto
from src.schemas.customer import Customer

# Logger propio de este módulo
logger = logging.getLogger(__name__)

# Nombre de la tabla de clientes
CUSTOMERS_TABLE_NAME = "customers"


# Leer y validar los clientes del CSV
def read_customers_from_csv(csv_path: Path) -> list[Customer]:
    """Lee el CSV y descarta las filas inválidas, como la fila de numeración."""
    # Lista de clientes válidos
    valid_customers: list[Customer] = []
    # Contador de filas descartadas
    invalid_rows_count = 0

    # Abrir el CSV y cerrarlo al terminar
    with csv_path.open(encoding="utf-8", newline="") as csv_file:
        # Recorrer cada fila como diccionario
        for row in csv.DictReader(csv_file):
            # Intentar validar la fila
            try:
                # Si es válida, agregar a la lista
                valid_customers.append(Customer.model_validate(row))
            # Si la fila no cumple el esquema
            except ValidationError:
                # Contar la fila descartada
                invalid_rows_count += 1

    # Informar cuántas filas se aceptaron y descartaron
    logger.info(
        "Clientes válidos: %d, filas descartadas: %d", len(valid_customers), invalid_rows_count
    )
    # Devolver los clientes válidos
    return valid_customers


# Armar el SQL para crear la tabla
def build_create_table_statement() -> str:
    """Genera el CREATE TABLE a partir de los campos del esquema Customer."""
    # Lista de columnas en SQL
    column_definitions = []
    # Recorrer los campos del esquema
    for field_name, field_info in Customer.model_fields.items():
        # Elegir el tipo SQL según el tipo del campo
        sql_type = {int: "INTEGER", float: "REAL"}.get(field_info.annotation, "TEXT")
        # El identificador es la clave primaria
        primary_key = " PRIMARY KEY" if field_name == "customer_id" else ""
        # Agregar la definición de la columna
        column_definitions.append(f"{field_name} {sql_type}{primary_key}")
    # Devolver el SQL completo
    return f"CREATE TABLE {CUSTOMERS_TABLE_NAME} ({', '.join(column_definitions)})"


# Guardar los clientes en SQLite
def write_customers_to_sqlite(customers: list[Customer], database_path: Path) -> int:
    """Recrea la tabla de clientes y la llena. Es seguro ejecutarlo varias veces."""
    # Crear la carpeta de la base si no existe
    database_path.parent.mkdir(parents=True, exist_ok=True)
    # Nombres de las columnas
    column_names = list(Customer.model_fields.keys())
    # Un marcador por columna para insertar de forma segura
    placeholders = ", ".join("?" for _ in column_names)
    # Armar el SQL de inserción
    insert_statement = (
        f"INSERT INTO {CUSTOMERS_TABLE_NAME} ({', '.join(column_names)}) VALUES ({placeholders})"
    )

    # Abrir la base y confirmar los cambios al terminar
    with sqlite3.connect(database_path) as connection:
        # Borrar la tabla anterior para empezar limpio
        connection.execute(f"DROP TABLE IF EXISTS {CUSTOMERS_TABLE_NAME}")
        # Crear la tabla nueva
        connection.execute(build_create_table_statement())
        # Insertar todas las filas de una vez
        connection.executemany(
            insert_statement,
            [tuple(customer.model_dump()[name] for name in column_names) for customer in customers],
        )
    # Devolver cuántos clientes se guardaron
    return len(customers)
