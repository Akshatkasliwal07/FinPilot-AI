from functools import lru_cache
from uuid import uuid4

import chromadb

from ai.config.settings import (
    CHROMA_COLLECTION,
    CHROMA_PERSIST_DIRECTORY,
)
from ai.embeddings import embed_documents, embed_text


@lru_cache(maxsize=1)
def get_collection():
    """
    Create or retrieve the persistent FinPilot ChromaDB collection.
    """
    CHROMA_PERSIST_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    client = chromadb.PersistentClient(
        path=str(CHROMA_PERSIST_DIRECTORY),
    )

    return client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def upsert_documents(
    documents: list[str],
    metadatas: list[dict] | None = None,
    ids: list[str] | None = None,
) -> list[str]:
    """
    Store text documents, metadata, and embeddings in ChromaDB.
    """
    if not documents:
        raise ValueError("At least one document is required.")

    if metadatas is not None and len(metadatas) != len(documents):
        raise ValueError(
            "The metadata count must match the document count."
        )

    if ids is not None and len(ids) != len(documents):
        raise ValueError(
            "The ID count must match the document count."
        )

    document_ids = ids or [
        str(uuid4())
        for _ in documents
    ]

    embeddings = embed_documents(documents)

    collection = get_collection()

    collection.upsert(
        ids=document_ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return document_ids


def search_documents(
    query: str,
    limit: int = 4,
    where: dict | None = None,
) -> list[dict]:
    """
    Find the most relevant stored documents for a search query.
    """
    if not query or not query.strip():
        raise ValueError("Query must be a non-empty string.")

    if limit < 1 or limit > 20:
        raise ValueError("Limit must be between 1 and 20.")

    collection = get_collection()

    query_arguments = {
        "query_embeddings": [embed_text(query)],
        "n_results": limit,
        "include": ["documents", "metadatas", "distances"],
    }

    if where:
        query_arguments["where"] = where

    result = collection.query(**query_arguments)

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    ids = result.get("ids", [[]])[0]

    return [
        {
            "id": document_id,
            "document": document,
            "metadata": metadata or {},
            "distance": distance,
        }
        for document_id, document, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
        )
    ]