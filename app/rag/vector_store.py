"""FAISS vector store wrapper."""
import os
import pickle
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
from app.core.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    def __init__(self):
        self.settings = get_settings()
        self._index = None
        self._doc_ids: List[str] = []
        self._doc_texts: List[str] = []

    def _lazy_import_faiss(self):
        try:
            import faiss
            return faiss
        except ImportError:
            raise RuntimeError("faiss-cpu not installed. Run: pip install faiss-cpu")

    def add(self, doc_ids: List[str], embeddings: np.ndarray, texts: List[str]) -> None:
        faiss = self._lazy_import_faiss()
        dim = embeddings.shape[1]
        if self._index is None:
            self._index = faiss.IndexFlatIP(dim)
        self._index.add(embeddings.astype(np.float32))
        self._doc_ids.extend(doc_ids)
        self._doc_texts.extend(texts)
        logger.info("vector_store.add", count=len(doc_ids), total=len(self._doc_ids))

    def search(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple[str, str, float]]:
        if self._index is None or self._index.ntotal == 0:
            return []
        faiss = self._lazy_import_faiss()
        q = query_vec.reshape(1, -1).astype(np.float32)
        scores, indices = self._index.search(q, min(top_k, self._index.ntotal))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                results.append((self._doc_ids[idx], self._doc_texts[idx], float(score)))
        return results

    def save(self) -> None:
        faiss = self._lazy_import_faiss()
        path = Path(self.settings.FAISS_INDEX_PATH)
        path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(path / "index.bin"))
        with open(path / "meta.pkl", "wb") as f:
            pickle.dump({"doc_ids": self._doc_ids, "doc_texts": self._doc_texts}, f)
        logger.info("vector_store.saved", path=str(path))

    def load(self) -> bool:
        faiss = self._lazy_import_faiss()
        path = Path(self.settings.FAISS_INDEX_PATH)
        index_file = path / "index.bin"
        meta_file  = path / "meta.pkl"
        if not index_file.exists():
            return False
        self._index = faiss.read_index(str(index_file))
        with open(meta_file, "rb") as f:
            meta = pickle.load(f)
        self._doc_ids   = meta["doc_ids"]
        self._doc_texts = meta["doc_texts"]
        logger.info("vector_store.loaded", size=self._index.ntotal)
        return True

    @property
    def size(self) -> int:
        return self._index.ntotal if self._index else 0


# Module-level singleton
_vector_store: Optional[VectorStore] = None

def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
