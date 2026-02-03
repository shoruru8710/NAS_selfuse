"""Text extraction from various file formats."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text(file_path: str, mime_type: str) -> str:
    """Extract text content from a file.

    Supports:
    - text/plain, text/markdown: direct read
    - application/pdf: basic text extraction
    - Future: Office documents, etc.
    """
    path = Path(file_path)

    if mime_type in ("text/plain", "text/markdown"):
        return path.read_text(encoding="utf-8", errors="replace")

    if mime_type == "application/pdf":
        return _extract_pdf(path)

    logger.warning(f"Unsupported MIME type for extraction: {mime_type}")
    return ""


def _extract_pdf(path: Path) -> str:
    """Extract text from PDF. Requires PyPDF2 or similar."""
    try:
        import PyPDF2

        text_parts = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                text_parts.append(f"[Page {i + 1}]\n{page_text}")
        return "\n\n".join(text_parts)
    except ImportError:
        logger.warning("PyPDF2 not installed, skipping PDF extraction")
        return ""
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return ""
