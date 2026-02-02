import logging
import re
from pathlib import Path
from typing import Generator

from ..config import BASE_DIR, PINECONE_NAMESPACE, CHUNK_SIZE, CHUNK_OVERLAP
from .store import get_pinecone_index
from .embeddings import get_embeddings_batch

logger = logging.getLogger(__name__)

DOCUMENTS_DIR = BASE_DIR / "data" / "documents"


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if not text:
        return []

    text = re.sub(r'\s+', ' ', text).strip()

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # try to break at sentence boundary
        if end < len(text):
            for sep in ['. ', '! ', '? ', '\n']:
                last_sep = text.rfind(sep, start, end)
                if last_sep > start + chunk_size // 2:
                    end = last_sep + 1
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def _parse_document(filepath: Path) -> dict:
    content = filepath.read_text(encoding='utf-8')
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else filepath.stem

    return {"title": title, "source": filepath.name, "content": content}


def _prepare_vectors(documents: list[dict]) -> Generator[dict, None, None]:
    for doc in documents:
        chunks = _chunk_text(doc["content"])
        if not chunks:
            continue

        embeddings = get_embeddings_batch(chunks)

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            yield {
                "id": f"{doc['source']}_{i}",
                "values": embedding,
                "metadata": {
                    "text": chunk,
                    "source": doc["source"],
                    "title": doc["title"],
                    "chunk_index": i,
                }
            }


def load_documents(directory: Path = None) -> int:
    doc_dir = directory or DOCUMENTS_DIR

    if not doc_dir.exists():
        logger.warning(f"Documents directory not found: {doc_dir}")
        return 0

    md_files = list(doc_dir.glob("*.md"))
    if not md_files:
        logger.warning(f"No markdown files found in: {doc_dir}")
        return 0

    logger.info(f"Loading {len(md_files)} documents from {doc_dir}")

    documents = [_parse_document(f) for f in md_files]
    vectors = list(_prepare_vectors(documents))

    if not vectors:
        logger.warning("No vectors generated from documents")
        return 0

    index = get_pinecone_index()
    batch_size = 100

    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch, namespace=PINECONE_NAMESPACE)
        logger.info(f"Upserted batch {i // batch_size + 1}: {len(batch)} vectors")

    logger.info(f"Successfully loaded {len(vectors)} vectors to Pinecone")
    return len(vectors)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    count = load_documents()
    print(f"Loaded {count} vectors")
