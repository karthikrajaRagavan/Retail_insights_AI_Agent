import logging
from openai import OpenAI

from ..config import OPENAI_API_KEY, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def get_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")

    client = _get_client()
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text.strip())
    return response.data[0].embedding


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    cleaned = [t.strip() for t in texts if t and t.strip()]
    if not cleaned:
        return []

    client = _get_client()
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=cleaned)
    return [item.embedding for item in response.data]
