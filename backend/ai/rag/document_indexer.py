import hashlib
from pathlib import Path

from ai.models.response import success_response
from ai.rag.pdf_processor import (
    chunk_pdf_pages,
    extract_pdf_pages,
)
from ai.vectorstore import (
    search_documents,
    upsert_documents,
)


def _create_chunk_id(
    source: str,
    page: int,
    chunk_index: int,
    text: str,
) -> str:
    raw_value = f"{source}:{page}:{chunk_index}:{text}"

    return hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()


def index_pdf(
    pdf_path: str | Path,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> dict:
    """
    Extract, chunk, embed, and persist one PDF in ChromaDB.
    """
    pages = extract_pdf_pages(pdf_path)

    chunks = chunk_pdf_pages(
        pages,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    ids = [
        _create_chunk_id(
            source=chunk["metadata"]["source"],
            page=chunk["metadata"]["page"],
            chunk_index=chunk["metadata"]["chunk_index"],
            text=chunk["text"],
        )
        for chunk in chunks
    ]

    document_ids = upsert_documents(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )

    return success_response(
        "PDF indexed successfully.",
        {
            "source": Path(pdf_path).name,
            "pages_indexed": len(pages),
            "chunks_indexed": len(chunks),
            "document_ids": document_ids,
        },
    )


def search_pdf(
    query: str,
    source: str,
    limit: int = 4,
) -> dict:
    """
    Retrieve relevant chunks from one indexed PDF.
    """
    results = search_documents(
        query=query,
        limit=limit,
        where={"source": source},
    )

    return success_response(
        "Relevant PDF sections retrieved.",
        {
            "query": query,
            "source": source,
            "results": results,
        },
    )