import re


def _split_long_text(text: str, chunk_size: int) -> list[str]:
    return [
        text[index : index + chunk_size]
        for index in range(0, len(text), chunk_size)
        if text[index : index + chunk_size].strip()
    ]


def split_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    cleaned_text = text.strip()
    if not cleaned_text:
        return []

    safe_chunk_size = max(chunk_size, 100)
    safe_overlap = min(max(overlap, 0), safe_chunk_size // 2)
    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n+", cleaned_text)
        if paragraph.strip()
    ]

    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        parts = (
            _split_long_text(paragraph, safe_chunk_size)
            if len(paragraph) > safe_chunk_size
            else [paragraph]
        )
        for part in parts:
            candidate = f"{current}\n\n{part}".strip() if current else part
            if len(candidate) <= safe_chunk_size:
                current = candidate
                continue

            if current:
                chunks.append(current)
                prefix = current[-safe_overlap:] if safe_overlap else ""
                current = f"{prefix}{part}".strip()
            else:
                chunks.append(part)
                current = ""

    if current:
        chunks.append(current)

    return [chunk.strip() for chunk in chunks if chunk.strip()]
