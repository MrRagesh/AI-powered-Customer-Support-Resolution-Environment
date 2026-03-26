"""Text preprocessing utilities."""
import re
import unicodedata


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\t\r\n]+", " ", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def truncate(text: str, max_chars: int = 4000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "…"


def extract_keywords(text: str) -> list:
    stop = {"i", "me", "my", "the", "a", "an", "is", "it", "to", "and",
            "or", "but", "in", "on", "at", "of", "for", "with", "not"}
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    return [w for w in words if w not in stop]


def is_toxic(text: str) -> bool:
    """Lightweight heuristic toxicity check."""
    toxic_patterns = [r"\b(kill|hate|stupid|idiot|damn|hell)\b"]
    return any(re.search(p, text, re.I) for p in toxic_patterns)
