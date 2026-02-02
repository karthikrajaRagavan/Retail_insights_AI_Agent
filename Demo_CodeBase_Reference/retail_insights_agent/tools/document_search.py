import logging

from ..config import RETRIEVAL_TOP_K
from ..vectorstore import search_documents as vector_search

logger = logging.getLogger(__name__)


def search_knowledge_base(query: str, num_results: int = RETRIEVAL_TOP_K) -> dict:
    if not query or not query.strip():
        return {"success": False, "documents": [], "error": "Empty query provided"}

    logger.info(f"Searching knowledge base: {query[:50]}...")

    try:
        results = vector_search(query, top_k=num_results)

        documents = []
        for doc in results:
            documents.append({
                "content": doc["text"],
                "source": doc["source"],
                "title": doc["title"],
                "relevance_score": round(doc["score"], 3),
            })

        return {"success": True, "documents": documents, "count": len(documents), "query": query}

    except Exception as e:
        logger.error(f"Knowledge base search failed: {e}")
        return {"success": False, "documents": [], "error": str(e)}
