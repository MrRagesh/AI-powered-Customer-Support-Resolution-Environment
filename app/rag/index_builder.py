"""Build FAISS index from KB documents."""
from typing import List
from app.rag.embeddings import embed
from app.rag.vector_store import get_vector_store
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def build_index_from_docs(docs: List[dict]) -> int:
    """
    docs: list of {"id": str, "content": str}
    Returns number of documents indexed.
    """
    if not docs:
        logger.warning("index_builder.empty_docs")
        return 0

    store = get_vector_store()
    ids    = [d["id"] for d in docs]
    texts  = [d["content"] for d in docs]
    vecs   = embed(texts)
    store.add(ids, vecs, texts)
    store.save()
    logger.info("index_builder.done", indexed=len(docs))
    return len(docs)
