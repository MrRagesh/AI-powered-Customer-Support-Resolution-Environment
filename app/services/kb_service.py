"""Knowledge base service — seed and retrieve documents."""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.kb_repo import KBRepository
from app.rag.index_builder import build_index_from_docs
from app.rag.vector_store import get_vector_store
from app.utils.logger import get_logger

logger = get_logger(__name__)


KB_SEED_DATA = [
    {"title": "Refund Policy",      "category": "refund",    "content": "Refunds are processed within 5-7 business days. To request a refund, log into your account and navigate to Orders > Request Refund. You will receive an email confirmation once processed.", "tags": ["refund", "policy"]},
    {"title": "Billing FAQ",        "category": "billing",   "content": "For billing inquiries, check your invoice in Account > Billing. Duplicate charges are automatically reversed within 48 hours. Contact billing@support.com for manual adjustments.", "tags": ["billing", "invoice"]},
    {"title": "Account Unlock",     "category": "account",   "content": "Locked accounts auto-unlock after 30 minutes. To manually unlock, use Forgot Password. If the issue persists, contact support with your user ID.", "tags": ["account", "locked"]},
    {"title": "App Crash Fix",      "category": "technical", "content": "If the app crashes on load: (1) Clear browser cache, (2) Disable extensions, (3) Try incognito mode, (4) Update to the latest version. If crashes persist, collect the error log from DevTools and submit a bug report.", "tags": ["crash", "technical"]},
    {"title": "API Rate Limits",    "category": "technical", "content": "Our API enforces 1000 requests/minute per key. Rate limit exceeded returns HTTP 429. Implement exponential backoff: wait 2^n seconds before retrying. Contact us for enterprise tier limits.", "tags": ["api", "rate-limit"]},
    {"title": "Shipping Delays",    "category": "shipping",  "content": "Standard shipping takes 5-10 business days. Express is 2-3 days. Once shipped, you receive a tracking number via email. Delays beyond 14 days qualify for free re-shipment.", "tags": ["shipping", "delivery"]},
    {"title": "Password Reset",     "category": "account",   "content": "Go to Login > Forgot Password. Enter your email. Check spam if you don't receive the reset email within 5 minutes. Reset links expire after 1 hour.", "tags": ["password", "reset"]},
    {"title": "Subscription Plans", "category": "billing",   "content": "Plans: Free (100 requests), Pro ($29/mo, 10K requests), Enterprise (custom). Downgrade takes effect at next billing cycle. No partial refunds on annual plans.", "tags": ["subscription", "plans"]},
    {"title": "Data Export",        "category": "technical", "content": "Export your data via Settings > Export. CSV and JSON formats supported. Large exports (>1GB) are queued and emailed when ready. GDPR deletion requests are processed within 30 days.", "tags": ["export", "data"]},
    {"title": "Escalation Process", "category": "escalation","content": "Issues unresolved after 48 hours are auto-escalated to senior support. For urgent production issues, use our emergency hotline. Escalated tickets receive a dedicated agent within 2 hours.", "tags": ["escalation", "urgent"]},
]


class KBService:
    def __init__(self, db: AsyncSession):
        self.repo = KBRepository(db)

    async def seed(self) -> int:
        existing = await self.repo.all()
        if existing:
            logger.info("kb_service.already_seeded", count=len(existing))
            return len(existing)
        ids = []
        for item in KB_SEED_DATA:
            doc_id = await self.repo.add_document(
                title=item["title"], content=item["content"],
                category=item["category"], tags=item["tags"],
            )
            ids.append({"id": doc_id, "content": item["content"]})
        indexed = await build_index_from_docs(ids)
        logger.info("kb_service.seeded", count=indexed)
        return indexed

    async def rebuild_index(self) -> int:
        docs = await self.repo.all()
        data = [{"id": d.id, "content": d.content} for d in docs]
        return await build_index_from_docs(data)
