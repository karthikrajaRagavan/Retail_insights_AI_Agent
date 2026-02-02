import logging
from pinecone import Pinecone

from ..config import PINECONE_API_KEY, PINECONE_INDEX, PINECONE_HOST, PINECONE_NAMESPACE
from .embeddings import get_embedding

logger = logging.getLogger(__name__)

_pinecone = None
_index = None


def get_pinecone_index():
    global _pinecone, _index

    if _index is None:
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not set in environment")
        if not PINECONE_INDEX and not PINECONE_HOST:
            raise ValueError("PINECONE_INDEX or PINECONE_HOST must be set in .env")

        logger.info(f"Connecting to Pinecone index: {PINECONE_INDEX}")
        _pinecone = Pinecone(api_key=PINECONE_API_KEY)
        _index = _pinecone.Index(name=PINECONE_INDEX or None, host=PINECONE_HOST or None)
        logger.info("Pinecone connection established")

    return _index


def search_documents(query: str, top_k: int = 5) -> list[dict]:
    if not query or not query.strip():
        return []

    logger.info(f"Searching knowledge base: {query[:50]}...")

    query_embedding = get_embedding(query)
    index = get_pinecone_index()
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        namespace=PINECONE_NAMESPACE,
        include_metadata=True
    )

    documents = []
    for match in results.matches:
        documents.append({
            "id": match.id,
            "score": match.score,
            "text": match.metadata.get("text", ""),
            "source": match.metadata.get("source", ""),
            "title": match.metadata.get("title", ""),
        })

    logger.info(f"Found {len(documents)} relevant documents")
    return documents


def delete_namespace():
    index = get_pinecone_index()
    index.delete(delete_all=True, namespace=PINECONE_NAMESPACE)
    logger.info(f"Deleted all vectors in namespace: {PINECONE_NAMESPACE}")
