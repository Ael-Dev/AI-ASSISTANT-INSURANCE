"""Cargar el CSV de clientes en SQLite. No usa embeddings.

Uso: uv run python scripts/index_crm.py
"""

# Librería estándar
import logging

# Módulos del proyecto
from src.config.settings import get_settings
from src.tools.crm_loader import read_customers_from_csv, write_customers_to_sqlite

# Logger de este script
logger = logging.getLogger("index_crm")


def main() -> None:
    # Cargar la configuración y el formato de los logs
    settings = get_settings()
    logging.basicConfig(level=settings.log_level, format="%(levelname)s %(message)s")

    # Leer y validar los clientes del CSV
    customers = read_customers_from_csv(settings.customers_csv_path)
    # Guardar los clientes en SQLite
    stored_customers_count = write_customers_to_sqlite(customers, settings.sqlite_database_path)
    # Informar cuántos clientes se guardaron
    logger.info("Clientes guardados en SQLite: %d", stored_customers_count)


# Correr solo si se ejecuta el archivo directamente
if __name__ == "__main__":
    main()
