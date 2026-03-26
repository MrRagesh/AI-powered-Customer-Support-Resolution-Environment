"""Sentence-transformer embedding wrapper."""
from typing import List
import numpy as np
from functools import lru_cache
from app.core.settings import get_settings


@lru_cache(maxsize=1)
def _load_model():
    from sentence_transformers import SentenceTransformer
    settings = get_settings()
    return SentenceTransformer(settings.EMBEDDING_MODEL)


def embed(texts: List[str]) -> np.ndarray:
    model = _load_model()
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=False)


def embed_query(text: str) -> np.ndarray:
    return embed([text])[0]
