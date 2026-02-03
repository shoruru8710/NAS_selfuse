"""Text chunking for RAG indexing."""

from app.config import settings


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    """Split text into overlapping chunks.

    Args:
        text: Full text to chunk
        chunk_size: Approximate characters per chunk (default from settings)
        overlap: Characters of overlap between chunks (default from settings)

    Returns:
        List of text chunks
    """
    if not text.strip():
        return []

    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at a sentence boundary
        if end < len(text):
            # Look for sentence-ending punctuation near the boundary
            for sep in ("\n\n", "\n", "。", ". ", "！", "？", "! ", "? "):
                boundary = text.rfind(sep, start + chunk_size // 2, end + overlap)
                if boundary != -1:
                    end = boundary + len(sep)
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = max(start + 1, end - overlap)

    return chunks
