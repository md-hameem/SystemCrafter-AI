# Architecture Overview

## System Design

SystemCrafter AI follows a modular, event-driven architecture with clear separation of concerns between the orchestrator, agents, and user interface.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│   ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│   │  Dashboard  │  │ Project View │  │  Real-time Updates  │   │
│   └─────────────┘  └──────────────┘  └─────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Orchestrator (FastAPI)                      │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│   │   Auth   │  │ Projects │  │  Tasks   │  │  WebSocket   │   │
│   │   API    │  │   API    │  │   API    │  │   Manager    │   │
│   └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
│                         │                                        │
│                         ▼                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              Orchestrator Service                        │   │
│   │    ┌─────────────────────────────────────────────────┐  │   │
│   │    │            Agent Pipeline                        │  │   │
│   │    │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐    │  │   │
│   │    │  │ R  │→│ A  │→│API │→│ DB │→│ BE │→│ FE │    │  │   │
│   │    │  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘    │  │   │
│   │    │     ↓      ↓      ↓      ↓      ↓      ↓       │  │   │
│   │    │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────────────┐   │  │   │
│   │    │  │Infra│→│Build│→│ QA │→│Deploy│→│ Recovery │   │  │   │
│   │    │  └────┘ └────┘ └────┘ └────┘ └────────────┘   │  │   │
│   │    └─────────────────────────────────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
    ┌──────────┐      ┌──────────┐        ┌──────────┐
    │PostgreSQL│      │  Redis   │        │ OpenAI   │
    │ Database │      │  Cache   │        │   API    │
    └──────────┘      └──────────┘        └──────────┘
```

## Components

### 1. Frontend (Next.js)

The frontend provides a modern, responsive interface for:
- User authentication
- Project management
- Real-time progress monitoring
- Artifact browsing and download

**Key Technologies:**
- Next.js 14 with App Router
- TanStack Query for server state
- Zustand for client state
- WebSocket for real-time updates
- Tailwind CSS for styling

### 2. Orchestrator (FastAPI)

The orchestrator is the central coordination layer that:
- Handles HTTP API requests
- Manages authentication and authorization
- Coordinates agent execution pipeline
- Broadcasts real-time updates via WebSocket

**Components:**
- **Auth API** - JWT-based authentication
- **Projects API** - CRUD operations for projects
- **Tasks API** - Task and artifact management
- **WebSocket Manager** - Real-time communication with Redis pub/sub
- **Orchestrator Service** - Agent pipeline coordination

### 3. Agent System

Agents are specialized AI modules that each perform a specific task in the generation pipeline.

#### Agent Pipeline Flow

```
1. RequirementInterpreter
   └─> Analyzes description, extracts features, user stories
   
2. SystemArchitect
   └─> Designs architecture, selects tech stack, creates diagrams
   
3. APIDesigner
   └─> Creates OpenAPI 3.0 specification
   
4. DBDesigner
   └─> Designs schema, creates ER diagram, generates migrations
   
5. BackendGenerator
   └─> Generates FastAPI backend code
   
6. FrontendGenerator
   └─> Generates Next.js frontend code
   
7. InfraEngineer
   └─> Creates Docker, docker-compose, K8s configs
   
8. Builder
   └─> Runs builds, linters, formatters
   
9. QAAgent
   └─> Executes smoke tests, E2E tests
   
10. Deployer
    └─> Deploys to target environment
    
11. RecoveryAgent (on failure)
    └─> Analyzes errors, suggests fixes
```

#### Base Agent Interface

```python
class BaseAgent(ABC):
    def __init__(self, session: AsyncSession, project_id: str):
        self.session = session
        self.project_id = project_id
        self.client = AsyncOpenAI()
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task."""
        pass
    
    async def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Make a call to the LLM."""
        pass
    
    async def save_artifact(self, name: str, content: str, type: str):
        """Save a generated artifact."""
        pass
```

### 4. Data Layer

#### PostgreSQL Database

Stores persistent data:
- Users and authentication
- Projects and their metadata
- Tasks and execution history
- Artifacts and generated files
- Logs and audit trail

**Schema:**
```
users
  ├── id (UUID, PK)
  ├── email (unique)
  ├── hashed_password
  ├── full_name
  ├── is_active
  └── created_at

projects
  ├── id (UUID, PK)
  ├── user_id (FK → users)
  ├── name
  ├── description
  ├── status (enum)
  ├── tech_stack (JSON)
  ├── generated_artifacts (JSON)
  ├── created_at
  └── updated_at

tasks
  ├── id (UUID, PK)
  ├── project_id (FK → projects)
  ├── name
  ├── agent_type
  ├── status (enum)
  ├── progress (int)
  ├── result (JSON)
  ├── error_message
  ├── started_at
  ├── completed_at
  └── created_at

artifacts
  ├── id (UUID, PK)
  ├── project_id (FK → projects)
  ├── task_id (FK → tasks)
  ├── name
  ├── artifact_type
  ├── file_path
  ├── content
  ├── metadata (JSON)
  └── created_at

log_entries
  ├── id (UUID, PK)
  ├── task_id (FK → tasks)
  ├── level
  ├── message
  ├── timestamp
  └── details (JSON)
```

#### Redis

Used for:
- WebSocket pub/sub messaging
- Session caching
- Rate limiting
- Background job queues

### 5. External Services

#### OpenAI API

Powers all AI agents with:
- GPT-4 for complex reasoning tasks
- GPT-3.5-turbo for simpler operations
- Configurable model selection per agent

## Data Flow

### Project Creation Flow

```
1. User submits project name + description
2. API creates project in "draft" status
3. Response returned to client
```

### Generation Flow

```
1. User triggers "Start Generation"
2. Orchestrator creates task queue
3. For each agent in pipeline:
   a. Create task in "pending" status
   b. Set task to "running"
   c. Broadcast status via WebSocket
   d. Execute agent with context from previous agents
   e. Save artifacts
   f. Set task to "completed" or "failed"
   g. Broadcast completion
4. Update project status
5. If failures, trigger RecoveryAgent
```

### WebSocket Message Flow

```
┌──────────┐     ┌────────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│  FastAPI   │────▶│  Redis   │────▶│ All      │
│          │     │  WebSocket │     │  Pub/Sub │     │ Clients  │
└──────────┘     └────────────┘     └──────────┘     └──────────┘
     ▲                                                     │
     └─────────────────────────────────────────────────────┘
```

## Security

### Authentication
- JWT tokens with configurable expiration
- Password hashing with bcrypt
- Secure cookie storage for tokens

### Authorization
- User-scoped project access
- Resource ownership validation
- Rate limiting on all endpoints

### Data Protection
- Input validation with Pydantic
- SQL injection prevention via ORM
- XSS protection in frontend

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers behind load balancer
- Redis for shared state and messaging
- PostgreSQL read replicas for heavy reads

### Background Processing
- Agent execution in background tasks
- Redis-backed job queues
- Async/await throughout

### Caching Strategy
- Redis caching for frequently accessed data
- Cache invalidation on mutations
- CDN for static assets

## Monitoring & Observability

### Logging
- Structured JSON logging
- Correlation IDs for request tracing
- Log levels: DEBUG, INFO, WARNING, ERROR

### Metrics
- Request latency histograms
- Agent execution times
- Error rates by endpoint

### Health Checks
- `/health` endpoint for load balancers
- Database connectivity check
- Redis connectivity check
