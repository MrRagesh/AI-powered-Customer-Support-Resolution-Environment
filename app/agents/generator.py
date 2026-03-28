from typing import List
from app.models.observation import KBResult
from app.core.settings import get_settings
from app.utils.logger import get_logger
from app.utils.text_utils import truncate

logger = get_logger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are a helpful, empathetic customer support AI.
Your goal is to resolve customer issues accurately and efficiently.
Use the provided knowledge base excerpts when relevant.
Always be professional, concise, and solution-focused.
If you cannot resolve the issue, acknowledge it and offer escalation.
"""

RESPONSE_PROMPT = """Customer ticket ({category}):
'''{ticket_text}'''

Knowledge Base Context:
{kb_context}

Conversation so far:
{history}

Generate a helpful resolution response. Be specific and actionable.
If the issue is resolved, say so clearly. If you need more information, ask one targeted question.
"""

FALLBACK_RESPONSES = {
    "refund":    "I understand your refund concern. Our team processes refunds within 5-7 business days. Please check your email for a confirmation. If not received, reply with your order number.",
    "billing":   "Thank you for reaching out about billing. I can see your account details. Please allow 24 hours for billing updates to reflect. Contact us if the issue persists.",
    "technical": "I apologize for the technical difficulty. Please try clearing your cache and cookies, then restart. If the issue continues, our engineering team will investigate.",
    "account":   "For account security, please use our password reset link. If your account is locked, it will auto-unlock in 30 minutes. Contact us if you need immediate assistance.",
    "shipping":  "I understand the frustration with delivery. Your package status is being monitored. Delays can occur due to carrier conditions. I'll escalate this if it doesn't arrive within 2 days.",
    "general":   "Thank you for contacting support. I've reviewed your request and will do my best to assist. Could you provide more details about your specific issue?",
}


class ResponseGenerator:
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None and settings.GEMINI_API_KEY:
            try:
                from google import genai
                self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except ImportError:
                pass
        return self._client

    async def generate(
        self,
        ticket_text: str,
        category: str,
        kb_results: List[KBResult],
        conversation_history: List[dict],
    ) -> str:
        client = self._get_client()
        if client:
            try:
                return await self._llm_generate(client, ticket_text, category, kb_results, conversation_history)
            except Exception as e:
                logger.warning("generator.llm_failed", error=str(e))
        return self._fallback_generate(category)

    async def _llm_generate(self, client, ticket_text, category, kb_results, history) -> str:
        kb_context = "\n".join(
            f"[{r.doc_id[:8]}] {r.snippet}" for r in kb_results
        ) or "No relevant KB articles found."

        history_str = "\n".join(
            f"{t['role'].upper()}: {t['content']}" for t in history[-6:]
        ) or "No prior conversation."

        user_content = RESPONSE_PROMPT.format(
            category=category,
            ticket_text=truncate(ticket_text, 800),
            kb_context=truncate(kb_context, 1200),
            history=history_str,
        )

        from google import genai
        response = await client.aio.models.generate_content(
            model=settings.LLM_MODEL,
            contents=user_content,
            config=genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=settings.LLM_TEMPERATURE,
                max_output_tokens=settings.LLM_MAX_TOKENS,
            )
        )
        return response.text.strip()

    def _fallback_generate(self, category: str) -> str:
        return FALLBACK_RESPONSES.get(category, FALLBACK_RESPONSES["general"])
