# 🤖 AI Customer Support OpenEnv

[![OpenEnv Compliant](https://img.shields.io/badge/OpenEnv-Compliant-brightgreen)]()
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-teal)]()
[![Docker](https://img.shields.io/badge/docker-ready-blue)]()

> A production-grade, **OpenEnv-compliant** AI Customer Support Resolution Environment.
> Agents classify tickets, retrieve knowledge via RAG (FAISS), generate responses, and resolve or escalate issues across multiple difficulty levels with deterministic grading.
> Now featuring a **Unified Dashboard**, **Live Assistant Chatbot**, and **Native Voice TTS**!

---

## ✨ Features

- **OpenEnv Validation Engine:** Strict step-by-step state management and reward calculation.
- **Unified UI Dashboard:** Seamlessly toggle between Manual Agent Evaluation bounds and the automated Live Chat interface.
- **Live Assistant Chatbot:** A fully autonomous agent that converses with customers, categorizes intents, queries the Vector DB, and handles escalations.
- **Native Voice (TTS):** The Live Assistant speaks directly to users leveraging zero-latency Web Speech APIs, equipped with high-quality female voice profiles.
- **RAG Architecture:** FAISS-powered vector store hooked directly into SQLite for rich, policy-backed agent responses.

---

## 🚀 Quick Start

```bash
# 1. Clone & configure
cp .env.example .env
# Edit .env — set API_KEY and LLM Keys (e.g. GEMINI_API_KEY / OPENAI_API_KEY)

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Launch the Server
uvicorn app.main:app --reload --port 7860

# 4. Access the Dashboard
# → http://localhost:7860/ui
```

### Docker
```bash
make build
make run
```

---

## 🏗️ Architecture

```
Client (Web Dashboard / Chatbot)
       ↓
    FastAPI (Routes / Core)
       ↓
 AI Agents (Classifier, Retriever, Generator)
       ↓
State Manager + Reward Engine (OpenEnv)
       ↓
 Graders + FAISS Vector Store + SQLite DB
```

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/ui` | Unified Web Dashboard & Chat Interface |
| `POST` | `/api/chat` | Autonomous Agent Chatbot Endpoint |
| `POST` | `/env/reset` | Start a new episode |
| `POST` | `/env/step` | Submit action, get observation+reward |
| `GET`  | `/env/state/{session_id}` | Current state snapshot |
| `GET`  | `/tasks` | List available tasks |
| `POST` | `/grader` | Grade a completed episode |
| `POST` | `/baseline` | Run rule-based baseline on all tasks |
| `GET`  | `/health` | Health check |

**Auth:** programmatic endpoints require `Authorization: Bearer <API_KEY>`.

---

## 🗂️ Project Structure

```
ai-support-openenv/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── api/                 # Routes (chat, env, tasks, grader, baseline)
│   ├── env/                 # OpenEnv core (step/reset/state/reward)
│   ├── agents/              # Classifier, Retriever, Generator (Gemini/OpenAI)
│   ├── tasks/               # Easy, Medium, Hard task definitions
│   ├── graders/             # Deterministic graders per task
│   ├── models/              # Pydantic domain models
│   ├── services/            # Business logic
│   ├── db/                  # SQLite + SQLAlchemy repositories
│   ├── rag/                 # FAISS vector store + embeddings
│   └── core/                # Settings, constants, exceptions
├── frontend/                # 🎨 Unified Web Dashboard & Chatbot UI
│   ├── index.html           # Main View with Toggles
│   ├── script.js            # Combined Logic & TTS Voice Engine
│   └── style.css            # Styles & Layout System
├── baseline/                # Deterministic baseline agent
├── tests/                   # pytest async test suite
├── scripts/                 # Seed, validate, generate tools
├── openenv.yaml             # OpenEnv spec file
├── Dockerfile               # Production container
└── README.md
```

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

## 🔧 Configuration

All config via `.env` (see `.env.example`):

- `API_KEY` — Bearer token for application auth
- `GEMINI_API_KEY` / `OPENAI_API_KEY` — LLM capability keys
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
