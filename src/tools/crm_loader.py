"""Carga del CSV de clientes hacia SQLite, validando cada fila con Pydantic."""

import csv
import logging
import sqlite3
from pathlib import Path

from pydantic import ValidationError

from src.schemas.customer import Customer

logger = logging.getLogger(__name__)

CUSTOMERS_TABLE_NAME = "customers"


def read_customers_from_csv(csv_path: Path) -> list[Customer]:
    """Lee el CSV y descarta las filas inválidas, como la fila de numeración."""
    valid_customers: list[Customer] = []
    invalid_rows_count = 0

    with csv_path.open(encoding="utf-8", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            try:
                valid_customers.append(Customer.model_validate(row))
            except ValidationError:
                invalid_rows_count += 1

    logger.info(
        "Clientes válidos: %d, filas descartadas: %d", len(valid_customers), invalid_rows_count
    )
    return valid_customers


def build_create_table_statement() -> str:
    """Genera el CREATE TABLE a partir de los campos del esquema Customer."""
    column_definitions = []
    for field_name, field_info in Customer.model_fields.items():
        sql_type = {int: "INTEGER", float: "REAL"}.get(field_info.annotation, "TEXT")
        primary_key = " PRIMARY KEY" if field_name == "customer_id" else ""
        column_definitions.append(f"{field_name} {sql_type}{primary_key}")
    return f"CREATE TABLE {CUSTOMERS_TABLE_NAME} ({', '.join(column_definitions)})"


def write_customers_to_sqlite(customers: list[Customer], database_path: Path) -> int:
    """Recrea la tabla de clientes y la llena. Es seguro ejecutarlo varias veces."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    column_names = list(Customer.model_fields.keys())
    placeholders = ", ".join("?" for _ in column_names)
    insert_statement = (
        f"INSERT INTO {CUSTOMERS_TABLE_NAME} ({', '.join(column_names)}) VALUES ({placeholders})"
    )

    with sqlite3.connect(database_path) as connection:
        connection.execute(f"DROP TABLE IF EXISTS {CUSTOMERS_TABLE_NAME}")
        connection.execute(build_create_table_statement())
        connection.executemany(
            insert_statement,
            [tuple(customer.model_dump()[name] for name in column_names) for customer in customers],
        )
    return len(customers)
