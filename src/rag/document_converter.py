"""Conversión de PDFs a Markdown con MarkItDown."""

# Librería estándar
import logging
from pathlib import Path

# Librerías externas
from markitdown import MarkItDown

# Logger propio de este módulo
logger = logging.getLogger(__name__)


# Convertir todos los PDFs de una carpeta
def convert_pdfs_to_markdown(source_directory: Path, target_directory: Path) -> list[Path]:
    """Convierte cada PDF a un .md con el mismo nombre y devuelve las rutas generadas."""
    # Crear la carpeta de salida si no existe
    target_directory.mkdir(parents=True, exist_ok=True)
    # Crear el conversor
    converter = MarkItDown()
    # Rutas de los Markdown generados
    markdown_paths: list[Path] = []

    # Recorrer los PDFs en orden alfabético
    for pdf_path in sorted(source_directory.glob("*.pdf")):
        # Convertir el PDF a texto Markdown
        conversion_result = converter.convert(str(pdf_path))
        # Ruta de salida con el mismo nombre
        markdown_path = target_directory / f"{pdf_path.stem}.md"
        # Guardar el Markdown en disco
        markdown_path.write_text(conversion_result.text_content, encoding="utf-8")
        # Registrar la ruta generada
        markdown_paths.append(markdown_path)
        # Informar qué PDF se convirtió
        logger.info("Convertido: %s", pdf_path.name)

    # Devolver las rutas generadas
    return markdown_paths
