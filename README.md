# SystemCrafter AI - Orchestrator

An autonomous AI "CTO" that interprets product descriptions and auto-generates production-capable full-stack applications.

## Features

- **Multi-Agent Architecture**: Specialized agents for requirements, architecture, API design, DB design, code generation, and deployment
- **OpenAPI-First**: Generate OpenAPI specs that drive both backend and frontend generation
- **Full Stack Output**: FastAPI backend + Next.js frontend + Postgres DB + Docker infrastructure
- **Audit Trails**: Complete decision logs and artifact history
- **Recovery System**: Automatic failure analysis and patch suggestions

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key (or compatible LLM endpoint)

### Local Development

```bash
# Clone the repository
git clone <repo-url>
cd systemcrafter-orchestrator

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Start with Docker Compose
docker-compose up --build

# Or run locally with Poetry
poetry install
poetry run uvicorn orchestrator.main:app --reload
```

### Using SystemCrafter

1. Open http://localhost:3000 (UI) or http://localhost:8000/docs (API)
2. Submit a product description
3. Watch as agents generate your application
4. Find your generated project in `projects/<project-id>/`
5. Run `docker-compose up` in the generated project

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend UI (Next.js)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator API (FastAPI)                 │
│  - Project Management                                        │
│  - Agent Coordination                                        │
│  - WebSocket Updates                                         │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │  Redis   │        │ Postgres │        │  Vector  │
    │  Queue   │        │    DB    │        │   DB     │
    └──────────┘        └──────────┘        └──────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Agent Workers                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Requirement │ │   System    │ │     API     │           │
│  │ Interpreter │ │  Architect  │ │   Designer  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  Database   │ │   Backend   │ │  Frontend   │           │
│  │  Designer   │ │  Generator  │ │  Generator  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │    Infra    │ │   Builder   │ │  QA Agent   │           │
│  │  Engineer   │ │  /Deployer  │ │  /Recovery  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

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
