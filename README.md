# SystemCrafter AI - Orchestrator

<div align="center">

![SystemCrafter AI](https://img.shields.io/badge/SystemCrafter-AI-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-green?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=for-the-badge&logo=next.js)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**An autonomous AI "CTO" that interprets product descriptions and auto-generates production-capable full-stack applications.**

[Features](#features) • [Quick Start](#quick-start) • [Architecture](#architecture) • [API](#api-endpoints) • [Agents](#agents) • [Contributing](#contributing)

</div>

---

## 🚀 Features

- **🤖 Multi-Agent Architecture**: 12 specialized AI agents for requirements analysis, architecture design, API design, database modeling, code generation, testing, and deployment
- **📋 OpenAPI-First**: Generates OpenAPI 3.0 specs that drive both backend and frontend code generation
- **🏗️ Full Stack Output**: Complete applications with FastAPI backend + Next.js frontend + PostgreSQL + Docker infrastructure
- **📊 Real-Time Progress**: WebSocket-based live updates on generation progress
- **📝 Audit Trails**: Complete decision logs and artifact history for every generation step
- **🔧 Recovery System**: Automatic failure analysis and intelligent patch suggestions
- **🐳 Docker-Ready**: Generated projects include production-ready Docker configurations
- **🔐 Secure**: JWT authentication, rate limiting, and secure defaults

## 📋 Prerequisites

- **Python 3.11+** - Core runtime
- **Node.js 20+** - Frontend development
- **Docker & Docker Compose** - Container orchestration
- **OpenAI API Key** - Powers AI agents (or compatible LLM endpoint)
- **PostgreSQL 15+** - Primary database (or use Docker)
- **Redis 7+** - Task queue and caching (or use Docker)

## 🏁 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/md-hameem/SystemCrafter-AI.git
cd SystemCrafter-AI/systemcrafter-orchestrator

# Copy environment file and configure
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Start all services
docker-compose up --build

# Access the application
# - Frontend UI: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Backend setup
cd systemcrafter-orchestrator
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start PostgreSQL and Redis (using Docker)
docker-compose up -d db redis

# Run database migrations
poetry run alembic upgrade head

# Start the backend
poetry run uvicorn orchestrator.main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (new terminal)
cd ui
npm install
npm run dev
```

### 🎯 Using SystemCrafter

1. **Register/Login** at http://localhost:3000
2. **Create a new project** with a detailed product description
3. **Watch real-time progress** as agents analyze and generate your application
4. **Download or access** your generated project in `projects/<project-id>/`
5. **Run** `docker-compose up` in the generated project directory

#### Example Product Description:
```
Build a task management app with user authentication, project organization,
due dates, priority levels, and team collaboration features. Include a
dashboard with statistics and a calendar view.
```

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend UI (Next.js 14)                  │
│  • TailwindCSS • TanStack Query • Zustand • WebSocket       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Orchestrator API (FastAPI)                  │
│  • JWT Auth • WebSocket Updates • OpenAPI 3.0               │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │  Redis   │        │ Postgres │        │ ChromaDB │
    │  Queue   │        │    DB    │        │ (Vector) │
    └──────────┘        └──────────┘        └──────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI Agent Pipeline                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Requirement │ │   System    │ │     API     │           │
│  │ Interpreter │ │  Architect  │ │   Designer  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  Database   │ │   Backend   │ │  Frontend   │           │
│  │  Designer   │ │  Generator  │ │  Generator  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │    Infra    │ │   Builder   │ │  Deployer   │           │
│  │  Engineer   │ │   Agent     │ │   Agent     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐                           │
│  │  QA Agent   │ │  Recovery   │                           │
│  │             │ │   Agent     │                           │
│  └─────────────┘ └─────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

## 🤖 Agents

| Agent | Purpose |
|-------|---------|
| **Requirement Interpreter** | Analyzes product descriptions, extracts features, user stories, and acceptance criteria |
| **System Architect** | Designs system architecture, selects technologies, defines service boundaries |
| **API Designer** | Creates OpenAPI 3.0 specifications with endpoints, schemas, and security |
| **Database Designer** | Models database schema with tables, relationships, indexes, and migrations |
| **Backend Generator** | Generates FastAPI code with routes, services, models, and tests |
| **Frontend Generator** | Creates Next.js UI with components, pages, state management, and styling |
| **Infra Engineer** | Produces Docker configs, CI/CD pipelines, and infrastructure as code |
| **Builder Agent** | Compiles, builds, and validates generated code |
| **Deployer Agent** | Handles deployment to Docker, Kubernetes, or cloud platforms |
| **QA Agent** | Runs tests, validates functionality, and reports issues |
| **Recovery Agent** | Analyzes failures and suggests fixes |

## 📁 Project Structure

```
systemcrafter-orchestrator/
├── orchestrator/          # FastAPI service
│   ├── api/              # API routes
│   ├── core/             # Core configuration
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── services/         # Business logic
├── agents/               # Agent implementations
│   ├── base.py          # Base agent class
│   ├── requirement_interpreter/
│   ├── system_architect/
│   ├── api_designer/
│   ├── db_designer/
│   ├── backend_generator/
│   ├── frontend_generator/
│   ├── infra_engineer/
│   ├── builder/
│   ├── deployer/
│   ├── qa_agent/
│   └── recovery_agent/
├── templates/            # Jinja2 project templates
├── tests/               # Test suite
├── docker-compose.yml
└── README.md
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `DATABASE_URL` | Postgres connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `GITHUB_TOKEN` | GitHub API token for repo creation | Optional |
| `SECRET_KEY` | JWT signing key | Required |

## License

MIT License
