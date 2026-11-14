# Librerías externas
import pytest

# Módulos del proyecto
from src.config.settings import Settings


# Recurso reutilizable entre pruebas
@pytest.fixture
# Configuración aislada para pruebas
def settings_for_tests(tmp_path) -> Settings:
    """Configuración que escribe el vector store en una carpeta temporal."""
    # Usar una carpeta temporal y fragmentos pequeños
    return Settings(
        vector_store_directory=tmp_path / "vectorstore",
        chunk_size=400,
        chunk_overlap=50,
    )
