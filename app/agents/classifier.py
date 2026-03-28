"""Ticket classifier — zero-shot via LLM or keyword fallback."""
import json
from app.core.constants import CATEGORIES, SEVERITY
from app.core.settings import get_settings
from app.utils.logger import get_logger
from app.utils.text_utils import normalize

logger = get_logger(__name__)
settings = get_settings()

CLASSIFY_PROMPT = """You are a customer support ticket classifier.

Classify the following support ticket into EXACTLY ONE category from: {categories}
Also assign a severity from: {severities}

Respond ONLY with valid JSON:
{{"category": "<category>", "severity": "<severity>", "confidence": <0.0-1.0>}}

Ticket:
'''
{ticket_text}
'''
"""

KEYWORD_MAP = {
    "refund":    ["refund", "money back", "charge", "overcharged"],
    "billing":   ["billing", "invoice", "payment", "subscription"],
    "technical": ["error", "bug", "crash", "not working", "broken", "issue"],
    "account":   ["login", "password", "account", "locked", "reset"],
    "shipping":  ["delivery", "shipped", "tracking", "package", "order"],
    "product":   ["feature", "upgrade", "plan", "product"],
}


def _keyword_classify(text: str) -> str:
    text_lower = text.lower()
    for category, keywords in KEYWORD_MAP.items():
        if any(kw in text_lower for kw in keywords):
            return category
    return "general"


class TicketClassifier:
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None and settings.GEMINI_API_KEY:
            try:
                from google import genai
                self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except ImportError:
                logger.warning("classifier.google_genai_not_installed")
        return self._client

    async def classify(self, ticket_text: str) -> dict:
        text = normalize(ticket_text)
        client = self._get_client()
        if client:
            try:
                return await self._llm_classify(client, text)
            except Exception as e:
                logger.warning("classifier.llm_failed", error=str(e))
        return self._fallback_classify(text)

    async def _llm_classify(self, client, text: str) -> dict:
        prompt = CLASSIFY_PROMPT.format(
            categories=", ".join(CATEGORIES),
            severities=", ".join(SEVERITY),
            ticket_text=text[:1500],
        )
        from google import genai
        response = await client.aio.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=100,
                response_mime_type="application/json",
            )
        )
        raw = response.text.strip()
        result = json.loads(raw)
        logger.info("classifier.llm_result", **result)
        return result

    def _fallback_classify(self, text: str) -> dict:
        category = _keyword_classify(text)
        severity = "high" if any(w in text.lower() for w in ["urgent", "critical", "emergency"]) else "medium"
        return {"category": category, "severity": severity, "confidence": 0.7}
