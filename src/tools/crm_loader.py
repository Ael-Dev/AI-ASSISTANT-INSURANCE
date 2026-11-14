"""Carga del CSV de clientes hacia SQLite, validando cada fila con Pydantic."""

# Lectura de archivos CSV
import csv

# Registro de mensajes
import logging

# Base de datos SQLite incluida en Python
import sqlite3

# Manejo de rutas de archivos
from pathlib import Path

# Error que lanza Pydantic al validar
from pydantic import ValidationError

# Esquema de un cliente
from src.schemas.customer import Customer

# Logger propio de este módulo
logger = logging.getLogger(__name__)

# Nombre de la tabla de clientes
CUSTOMERS_TABLE_NAME = "customers"


# Lee y valida los clientes del CSV
def read_customers_from_csv(csv_path: Path) -> list[Customer]:
    """Lee el CSV y descarta las filas inválidas, como la fila de numeración."""
    # Lista de clientes válidos
    valid_customers: list[Customer] = []
    # Contador de filas descartadas
    invalid_rows_count = 0

    # Abre el CSV y lo cierra al terminar
    with csv_path.open(encoding="utf-8", newline="") as csv_file:
        # Recorre cada fila como diccionario
        for row in csv.DictReader(csv_file):
            # Intenta validar la fila
            try:
                # Si es válida se agrega a la lista
                valid_customers.append(Customer.model_validate(row))
            # Si la fila no cumple el esquema
            except ValidationError:
                # Cuenta la fila descartada
                invalid_rows_count += 1

    # Informa cuántas filas se aceptaron y descartaron
    logger.info(
        "Clientes válidos: %d, filas descartadas: %d", len(valid_customers), invalid_rows_count
    )
    # Devuelve los clientes válidos
    return valid_customers


# Arma el SQL para crear la tabla
def build_create_table_statement() -> str:
    """Genera el CREATE TABLE a partir de los campos del esquema Customer."""
    # Lista de columnas en SQL
    column_definitions = []
    # Recorre los campos del esquema
    for field_name, field_info in Customer.model_fields.items():
        # Elige el tipo SQL según el tipo del campo
        sql_type = {int: "INTEGER", float: "REAL"}.get(field_info.annotation, "TEXT")
        # El identificador es la clave primaria
        primary_key = " PRIMARY KEY" if field_name == "customer_id" else ""
        # Agrega la definición de la columna
        column_definitions.append(f"{field_name} {sql_type}{primary_key}")
    # Devuelve el SQL completo
    return f"CREATE TABLE {CUSTOMERS_TABLE_NAME} ({', '.join(column_definitions)})"


# Guarda los clientes en SQLite
def write_customers_to_sqlite(customers: list[Customer], database_path: Path) -> int:
    """Recrea la tabla de clientes y la llena. Es seguro ejecutarlo varias veces."""
    # Crea la carpeta de la base si no existe
    database_path.parent.mkdir(parents=True, exist_ok=True)
    # Nombres de las columnas
    column_names = list(Customer.model_fields.keys())
    # Un marcador por columna para insertar de forma segura
    placeholders = ", ".join("?" for _ in column_names)
    # Arma el SQL de inserción
    insert_statement = (
        f"INSERT INTO {CUSTOMERS_TABLE_NAME} ({', '.join(column_names)}) VALUES ({placeholders})"
    )

    # Abre la base y confirma los cambios al terminar
    with sqlite3.connect(database_path) as connection:
        # Borra la tabla anterior para empezar limpio
        connection.execute(f"DROP TABLE IF EXISTS {CUSTOMERS_TABLE_NAME}")
        # Crea la tabla nueva
        connection.execute(build_create_table_statement())
        # Inserta todas las filas de una vez
        connection.executemany(
            insert_statement,
            [tuple(customer.model_dump()[name] for name in column_names) for customer in customers],
        )
    # Devuelve cuántos clientes se guardaron
    return len(customers)
