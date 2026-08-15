from functools import lru_cache

from sentence_transformers import SentenceTransformer

from ai.config.settings import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Loads the embedding model once per application process.
    """
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_text(text: str) -> list[float]:
    """
    Convert one non-empty text string into a normalized vector.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text must be a non-empty string.")

    vector = get_embedding_model().encode(
        text.strip(),
        normalize_embeddings=True,
    )

    return vector.tolist()


def embed_documents(texts: list[str]) -> list[list[float]]:
    """
    Convert multiple non-empty text strings into normalized vectors.
    """
    if not texts:
        return []

    cleaned_texts = []

    for text in texts:
        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                "Every document must be a non-empty string."
            )

        cleaned_texts.append(text.strip())

    vectors = get_embedding_model().encode(
        cleaned_texts,
        normalize_embeddings=True,
    )

    return vectors.tolist()