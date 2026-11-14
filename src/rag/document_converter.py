"""Conversión de PDFs a Markdown con MarkItDown."""

import logging
from pathlib import Path

from markitdown import MarkItDown

logger = logging.getLogger(__name__)


def convert_pdfs_to_markdown(source_directory: Path, target_directory: Path) -> list[Path]:
    """Convierte cada PDF a un .md con el mismo nombre y devuelve las rutas generadas."""
    target_directory.mkdir(parents=True, exist_ok=True)
    converter = MarkItDown()
    markdown_paths: list[Path] = []

    for pdf_path in sorted(source_directory.glob("*.pdf")):
        conversion_result = converter.convert(str(pdf_path))
        markdown_path = target_directory / f"{pdf_path.stem}.md"
        markdown_path.write_text(conversion_result.text_content, encoding="utf-8")
        markdown_paths.append(markdown_path)
        logger.info("Convertido: %s", pdf_path.name)

    return markdown_paths
