import pytest

from src.config.settings import Settings


@pytest.fixture
def settings_for_tests(tmp_path) -> Settings:
    """Configuración que escribe el vector store en una carpeta temporal."""
    return Settings(
        vector_store_directory=tmp_path / "vectorstore",
        chunk_size=400,
        chunk_overlap=50,
    )
