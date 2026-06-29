# Wizan (وِزان)

> **Cognitive Load-Aware Productivity Platform for Students**

Wizan is an AI-powered platform that measures a student's daily cognitive capacity and uses that score to drive adaptive task scheduling, AI-assisted planning, a RAG-based study assistant, and voice interaction — helping students work *with* their mental state instead of against it.

---

## Table of Contents

- [Problem](#problem)
- [Solution](#solution)
- [Target Market](#target-market)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Celery & Redis Setup](#celery--redis-setup)
  - [Docker Setup](#docker-setup-recommended)
- [Environment Variables](#environment-variables)
- [Team](#team)
---

## Problem

Students juggle a high volume of academic tasks every day, but most productivity tools assume a person has a *constant* level of mental energy. In reality, focus and cognitive capacity fluctuate daily — and sometimes hourly — due to sleep, stress, workload, and burnout. The result:

- Students overcommit on low-capacity days and underperform or burn out.
- Generic to-do apps and planners ignore mental state entirely.
- Study tools don't adapt tone, pacing, or task difficulty to how a student is *actually* feeling that day.
- There is no reliable, structured way for a student to communicate "how much can I realistically take on today?" to the tools they use.

## Solution

Wizan introduces a **Cognitive Score Engine**: a short morning quiz that produces a daily score (0–100) representing the student's available cognitive capacity. This score becomes the central signal that drives every other part of the platform:

| Score-Driven Behavior | Description |
|---|---|
| **Task Regulation** | Tasks are automatically marked allowed / postponed based on today's score, with an override option |
| **Adaptive Planning** | An AI agent breaks tasks into sub-steps with a tone (calm / urgent / supportive) matched to the score |
| **RAG Study Assistant** | Answers study questions using the student's own course material (PDFs), with citations |
| **Voice Input & TTS** | Students can add tasks by voice and have their daily plan read back to them |

Wizan doesn't just track tasks — it tracks *capacity*, and plans around it.

## Target Market

- **Primary:** University and higher-institute students managing heavy, irregular academic workloads (exams, projects, multiple courses).
- **Secondary:** Bilingual (Arabic/English) student populations in the MENA region needing full RTL support.
- **Tertiary:** Self-paced learners, bootcamp students, and graduate researchers who need structured study support combined with workload-aware planning.

---

## Key Features

| # | Feature | Summary |
|---|---|---|
| 1 | Project Setup & Auth | Django + DRF backend, React + Vite frontend, JWT auth, bilingual RTL/LTR UI |
| 2 | Cognitive Score Engine | Morning quiz → 0–100 score → score history, injected into every downstream AI prompt |
| 3 | Smart Task Dashboard | Task Regulator Agent: allows/postpones tasks based on score with manual override |
| 4 | AI Planning Agent | Decomposes tasks into sub-steps with adaptive tone and structured JSON output |
| 5 | RAG Study Assistant | Hybrid (dense + BM25) retrieval over ingested course PDFs with cited answers |
| 6 | Voice Input & TTS | Voice-to-task input and text-to-speech daily plan readout |
| 7 | Security & Guardrails | Rate limiting, prompt-injection defense, PII filtering, circuit breaker/fallback |
| 8 | Observability & Evaluation | Langfuse tracing, RAGAS evaluation, adversarial test suite, full delivery pipeline |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              CLIENT (Browser)                            │
│   React + Vite + Tailwind CSS  •  Bilingual (AR/EN) + RTL  •  i18next    │
└───────────────────────────────────┬────────────────────────────────────--┘
                                     │ REST (JWT)
┌────────────────────────────────────▼──────────────────────────────────────┐
│                           BACKEND — Django 5 + DRF                       │
│  ┌────────────┐  ┌──────────────────┐  ┌───────────────────────────────┐ │
│  │   Auth      │  │ Cognitive Score  │  │   Security & Guardrails       │ │
│  │ (SimpleJWT) │  │ Engine           │  │ rate-limit / prompt-injection │ │
│  └────────────┘  └──────────────────┘  └───────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │            LangChain Multi-Agent Orchestration Layer               │  │
│  │   Task Regulator Agent · Planning Agent · Resource (RAG) Agent     │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└───────┬───────────────────────┬──────────────────────────┬───────────────┘
        │                       │                          │
┌───────▼────────┐   ┌──────────▼───────────┐   ┌──────────▼──────────────┐
│ Supabase /      │   │ ITI Student Bedrock   │   │ Celery + Redis          │
│ PostgreSQL +    │   │ Gateway (Llama 3.3    │   │ Async tasks, scoring     │
│ pgvector        │   │ 70B / DeepSeek V3) +  │   │ jobs, background agents  │
│                 │   │ Gemini embeddings +   │   │                          │
│                 │   │ Groq                  │   │                          │
└─────────────────┘   └───────────────────────┘   └──────────────────────────┘
                                     │
                       ┌─────────────▼─────────────┐
                       │ Langfuse + RAGAS           │
                       │ Observability & Evaluation │
                       └────────────────────────────┘
```

**Flow summary:**
1. Student logs in (JWT) → takes the morning quiz → backend computes the cognitive score.
2. The score is persisted and injected into every subsequent AI agent prompt for that session/day.
3. The **Task Regulator Agent** uses the score to decide which tasks are allowed today.
4. The **Planning Agent** decomposes new tasks into steps, adapting tone to the score.
5. The **Resource (RAG) Agent** answers study questions from ingested course PDFs via hybrid retrieval (dense + BM25 + reranking), returning cited sources.
6. Voice input is transcribed and routed into the Planning Agent pipeline; TTS reads the daily plan back.
7. All AI calls pass through guardrails (rate limiting, prompt-injection defense) and are traced via Langfuse, with quality measured via RAGAS.

---

## Tech Stack

### Backend
| Component | Technology |
|---|---|
| Framework | Django 5 + Django REST Framework |
| Auth | JWT (SimpleJWT) |
| AI Orchestration | LangChain (multi-agent) |
| LLM Provider | ITI Student Bedrock Gateway (Llama 3.3 70B primary, DeepSeek V3 fallback), Groq |
| Embeddings | Gemini `gemini-embedding-001` (768-dim) |
| Security | `django-ratelimit`, custom prompt-injection guard, `presidio-analyzer` (PII) |
| Async / Background Jobs | Celery + Redis |
| Observability | Langfuse, RAGAS |
| Testing | pytest |

### Frontend
| Component | Technology |
|---|---|
| Framework | React + Vite |
| Styling | Tailwind CSS |
| Internationalization | react-i18next (Arabic/English, RTL support) |
| Routing | react-router-dom |
| UI Components | shadcn-style theme tokens |

### Database
| Component | Technology |
|---|---|
| Database | PostgreSQL (via Supabase) |
| Vector Store | pgvector |

### DevOps
| Component | Technology |
|---|---|
| Containerization | Docker + Docker Compose |
| Version Control | Git (feature branches, patch-based delivery) |
| API Testing | Postman |
| Documentation | python-docx, pptxgenjs, ReportLab |

---

## Project Structure

```
wizan/
├── backend/
│   ├── ai/
│   │   ├── llm.py                  # safe_llm_call — unified LLM call path
│   │   ├── prompt_guard.py         # assert_safe() / wrap_user_text()
│   │   ├── agents/
│   │   │   ├── task_regulator.py
│   │   │   ├── planning_agent.py
│   │   │   └── resource_agent.py
│   │   └── rag.py                  # retrieval + Groq direct call path
│   ├── cognitive/                  # quiz, scoring, score history
│   ├── tasks/                      # tasks, task_steps, overrides
│   ├── voice/                      # VoiceAddTaskView, transcription
│   ├── security/                   # rate limiting, audit logs, PII filtering
│   ├── observability/              # Langfuse tracing, RAGAS eval harness
│   ├── users/                      # auth, JWT
│   ├── config/                     # Django settings, Celery config
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── QuizPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── TasksPage.jsx
│   │   │   └── ChatPage.jsx
│   │   ├── components/
│   │   ├── locales/                 # i18n (en / ar)
│   │   ├── styles/                  # CSS files (no inline styles)
│   │   └── api/                     # API client, token handling
│   ├── index.html
│   └── package.json
│
├── docker-compose.yml
├── .env.example
└── README.md
```

> **Note:** Folder names above reflect logical ownership areas described in the project plan; align with the actual repository structure in `develop` before publishing.

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or a Supabase project)
- Redis (for Celery)
- Docker & Docker Compose (recommended)

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/MariamAsall/wizan.git
cd wizan/backend

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Fill in DB credentials, SBG_API_KEY, GEMINI_API_KEY, etc.

# 5. Run migrations
python manage.py migrate

# 6. Create a superuser (optional)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

The API will be available at `http://localhost:8000`.

### Frontend Setup

```bash
cd wizan/frontend

# 1. Install dependencies
npm install

# 2. Configure environment variables
cp .env.example .env
# Set VITE_API_BASE_URL=http://localhost:8000

# 3. Start the development server
npm run dev
```

The app will be available at `http://localhost:5173`.

### Celery & Redis Setup

Celery handles background jobs (e.g. score processing, async agent tasks).

```bash
# 1. Start Redis (if not using Docker)
redis-server

# 2. From the backend/ directory, start a Celery worker
celery -A config worker --loglevel=info

# 3. (Optional) Start Celery Beat for scheduled tasks
celery -A config beat --loglevel=info
```

By default, `CELERY_BROKER_URL` points to `redis://redis:6379/0` (Docker Compose default). Override it in `.env` for local, non-Docker Redis (e.g. `redis://localhost:6379/0`).

### Docker Setup (Recommended)

```bash
# From the project root
docker-compose up --build
```

This will start the backend, frontend, PostgreSQL/Redis (if included locally), and Celery worker as defined in `docker-compose.yml`.

---

## Environment Variables

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key |
| `DATABASE_URL` | PostgreSQL/Supabase connection string |
| `SBG_API_KEY` | Bearer token for ITI Student Bedrock Gateway |
| `GEMINI_API_KEY` | Gemini API key (embeddings, voice) |
| `GROQ_API_KEY` | Groq API key |
| `CELERY_BROKER_URL` | Redis URL for Celery (default: `redis://redis:6379/0`) |
| `VITE_API_BASE_URL` | Frontend → backend API base URL |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` | Langfuse observability keys |

> Never commit real secrets. Use `.env.example` as a template and keep `.env` in `.gitignore`.

---

## Team

| Member | Role | Ownership Area |
|---|---|---|
| **Mariam** | Backend Developer | Backend security, AI evaluation, backend integration |
| **Mohamed** | Frontend / DevOps | Frontend hardening, delivery, infrastructure |
| **Nada** | Frontend Developer | Frontend |
| **Mariam** | AI/Backend | Embeddings and ingestion pipeline |
| **Aml** | Database/Infrastructure | Database and infrastructure |
| **Samy** | AI/Backend | Retrieval agent and speech-to-text |

---


## License

This project was developed as part of an ITI capstone program. License terms to be defined by the team.
