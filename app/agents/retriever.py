"""Knowledge Base retriever using FAISS vector search."""
from typing import List
from app.models.observation import KBResult
from app.rag.embeddings import embed_query
from app.rag.vector_store import get_vector_store
from app.core.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeRetriever:
    def __init__(self):
        self.settings = get_settings()

    def retrieve(self, query: str, top_k: int | None = None) -> List[KBResult]:
        k = top_k or self.settings.FAISS_TOP_K
        store = get_vector_store()
        if store.size == 0:
            logger.warning("retriever.empty_index")
            return []
        q_vec = embed_query(query)
        raw = store.search(q_vec, top_k=k)
        results = []
        for doc_id, text, score in raw:
            snippet = text[:200] + ("…" if len(text) > 200 else "")
            results.append(KBResult(
                doc_id=doc_id,
                title=f"KB Doc {doc_id[:8]}",
                snippet=snippet,
                score=round(score, 4),
            ))
        logger.info("retriever.results", count=len(results), query=query[:60])
        return results
