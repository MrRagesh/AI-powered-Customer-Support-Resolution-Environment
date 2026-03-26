# 🤖 AI Customer Support OpenEnv

[![OpenEnv Compliant](https://img.shields.io/badge/OpenEnv-Compliant-brightgreen)]()
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-teal)]()
[![Docker](https://img.shields.io/badge/docker-ready-blue)]()

> A production-grade, **OpenEnv-compliant** AI Customer Support Resolution Environment.
> Agents classify tickets, retrieve knowledge, generate responses, and resolve or escalate
> issues across three difficulty levels with deterministic grading.

---

## 🚀 Quick Start

```bash
# 1. Clone & configure
cp .env.example .env
# Edit .env — set API_KEY and optionally OPENAI_API_KEY

# 2. Install
pip install -r requirements.txt

# 3. Launch
make dev
# → http://localhost:7860/docs

# 4. Run baseline
make baseline
```

### Docker
```bash
make build
make run
```

---

## 🏗️ Architecture

```
Client → FastAPI → SupportEnvironment
                       ↓
               AI Agents (Classifier, Retriever, Generator)
                       ↓
               State Manager + Reward Engine
                       ↓
               Graders + FAISS Vector Store
                       ↓
               SQLite DB + Structured Logs
```

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/env/reset` | Start a new episode |
| `POST` | `/env/step` | Submit action, get observation+reward |
| `GET`  | `/env/state/{session_id}` | Current state snapshot |
| `GET`  | `/tasks` | List available tasks |
| `POST` | `/grader` | Grade a completed episode |
| `POST` | `/baseline` | Run rule-based baseline on all tasks |
| `GET`  | `/health` | Health check |

**Auth:** All endpoints require `Authorization: Bearer <API_KEY>`.

---

## 🎯 Tasks

| Task ID | Difficulty | Max Steps | Description |
|---------|-----------|-----------|-------------|
| `support-easy-v1` | Easy | 5 | Single-turn refund/billing ticket |
| `support-medium-v1` | Medium | 10 | Multi-turn technical troubleshooting |
| `support-hard-v1` | Hard | 20 | Complex multi-intent, requires escalation |

---

## 🔄 Agent Action Space

| Action | Content Required | Description |
|--------|-----------------|-------------|
| `classify` | ✅ | Classify ticket category |
| `retrieve` | ✅ | Search knowledge base |
| `respond` | ✅ | Send response to customer |
| `clarify` | ✅ | Ask clarifying question |
| `resolve` | ❌ | Mark as resolved |
| `escalate` | ❌ | Escalate to human agent |

---

## 💰 Reward Structure

| Event | Reward |
|-------|--------|
| Each step | -0.05 (penalty) |
| Correct classification | +0.10 |
| Knowledge retrieval | +0.05 |
| Resolution | +1.00 + efficiency bonus |
| Escalation | +0.10 |
| Failure / max steps | -0.50 |

---

## 🧪 Example Session

```python
import httpx

headers = {"Authorization": "Bearer YOUR_API_KEY"}

with httpx.Client(base_url="http://localhost:7860", headers=headers) as c:
    # 1. Reset
    r = c.post("/env/reset", json={"task_id": "support-easy-v1"})
    session_id = r.json()["session_id"]

    # 2. Classify
    c.post("/env/step", json={
        "session_id": session_id,
        "action": {"type": "classify", "content": "I need a refund for my order"}
    })

    # 3. Retrieve KB
    c.post("/env/step", json={
        "session_id": session_id,
        "action": {"type": "retrieve", "content": "refund policy timeline"}
    })

    # 4. Respond & Resolve
    c.post("/env/step", json={
        "session_id": session_id,
        "action": {"type": "resolve"}
    })

    # 5. Grade
    r = c.post("/grader", json={"session_id": session_id})
    print(r.json())
    # {"score": 95, "passed": true, "breakdown": {...}}
```

---

## 🗂️ Project Structure

```
ai-support-openenv/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── api/                 # Routes, schemas, grader, baseline
│   ├── env/                 # OpenEnv core (step/reset/state/reward)
│   ├── agents/              # Classifier, Retriever, Generator
│   ├── tasks/               # Easy, Medium, Hard task definitions
│   ├── graders/             # Deterministic graders per task
│   ├── models/              # Pydantic domain models
│   ├── services/            # Business logic
│   ├── db/                  # SQLAlchemy + repositories
│   ├── rag/                 # FAISS vector store + embeddings
│   └── core/                # Settings, constants, exceptions
├── baseline/                # Deterministic baseline agent
├── tests/                   # pytest async test suite
├── scripts/                 # Seed, validate, generate
├── openenv.yaml             # OpenEnv spec file
├── Dockerfile               # Production container
└── README.md
```

---

## 🔧 Configuration

All config via `.env` (see `.env.example`):

- `API_KEY` — Bearer token for auth
- `OPENAI_API_KEY` — Optional; enables full LLM capability (fallback responses without it)
- `LLM_MODEL` — Default: `gpt-4o-mini`
- `DATABASE_URL` — Default: SQLite (swap to PostgreSQL for production)
- `FAISS_INDEX_PATH` — Vector index storage path

---

## 🧪 Testing

```bash
make test
# or
pytest tests/ -v --asyncio-mode=auto
```

---

## ✅ OpenEnv Compliance Validation

```bash
make validate
```

Expected output:
```
OpenEnv Validation Results
════════════════════════════════════════
  health                    ✅ PASS
  list_tasks                ✅ PASS
  reset                     ✅ PASS
  step                      ✅ PASS
  state                     ✅ PASS
  grader                    ✅ PASS
  baseline                  ✅ PASS
════════════════════════════════════════
  Overall: ✅ ALL PASS
```

---

## 🚢 Deploy to Hugging Face Spaces

1. Create a Space (Docker SDK)
2. Push this repo
3. Set Space secrets: `API_KEY`, `OPENAI_API_KEY`
4. Space auto-builds and runs on port `7860`

---

## 📊 Baseline Results (Rule-based Agent)

| Task | Score | Passed |
|------|-------|--------|
| Easy | ~85 | ✅ |
| Medium | ~72 | ✅ |
| Hard | ~65 | ✅ |
| **Mean** | **~74** | **✅** |

---

## 🗺️ Roadmap

- **Phase 1** ✅ Core engine, 3 tasks, API, graders, baseline
- **Phase 2** 🔜 Multi-turn memory, improved reward shaping, PostgreSQL
- **Phase 3** 🔜 Monitoring dashboard, analytics, multi-language support
