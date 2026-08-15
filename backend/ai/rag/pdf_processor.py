from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


def extract_pdf_pages(pdf_path: str | Path) -> list[dict]:
    """
    Extract readable text from every page in a PDF.

    Returns:
        [
            {
                "text": "...",
                "metadata": {
                    "source": "report.pdf",
                    "page": 1
                }
            }
        ]
    """
    path = Path(pdf_path)

    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    reader = PdfReader(str(path))

    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not supported.")

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()

        if text:
            pages.append(
                {
                    "text": text,
                    "metadata": {
                        "source": path.name,
                        "page": page_number,
                    },
                }
            )

    if not pages:
        raise ValueError(
            "No readable text was found. "
            "This may be a scanned PDF and require OCR."
        )

    return pages


def chunk_pdf_pages(
    pages: list[dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[dict]:
    """
    Split extracted PDF pages into retrievable text chunks.
    """
    if chunk_size < 200:
        raise ValueError("chunk_size must be at least 200.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be non-negative and smaller than chunk_size."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []

    for page in pages:
        text = page.get("text", "")
        metadata = page.get("metadata", {})

        if not text:
            continue

        page_chunks = splitter.split_text(text)

        for chunk_index, chunk_text in enumerate(page_chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": chunk_index,
            }

            chunks.append(
                {
                    "text": chunk_text,
                    "metadata": chunk_metadata,
                }
            )

    return chunks