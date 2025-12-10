# API Documentation

## Overview

The SystemCrafter API provides endpoints for managing projects, tasks, and artifacts in the AI-powered code generation system.

**Base URL:** `http://localhost:8000`

**Authentication:** Bearer JWT Token

## Authentication

### Register a New User

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Login

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer"
}
```

### Get Current User

```http
GET /api/auth/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Projects

### List Projects

```http
GET /api/projects?skip=0&limit=20
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (int): Number of records to skip (pagination)
- `limit` (int): Maximum number of records to return

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "My Project",
    "description": "An e-commerce platform...",
    "status": "draft",
    "tech_stack": null,
    "generated_artifacts": null,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### Create Project

```http
POST /api/projects
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "E-Commerce Platform",
  "description": "Build a modern e-commerce platform with user authentication, product catalog, shopping cart..."
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "E-Commerce Platform",
  "description": "Build a modern e-commerce platform...",
  "status": "draft",
  "tech_stack": null,
  "generated_artifacts": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Get Project

```http
GET /api/projects/{project_id}
Authorization: Bearer <token>
```

### Update Project

```http
PUT /api/projects/{project_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description..."
}
```

### Delete Project

```http
DELETE /api/projects/{project_id}
Authorization: Bearer <token>
```

**Response:** `204 No Content`

### Start Code Generation

```http
POST /api/projects/{project_id}/generate
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Generation started"
}
```

This triggers the AI pipeline to analyze the project description and generate code.

## Tasks

Tasks represent individual AI agent operations within a project.

### Get Project Tasks

```http
GET /api/tasks/project/{project_id}
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "project_id": "uuid",
    "name": "Requirement Analysis",
    "agent_type": "requirement_interpreter",
    "status": "completed",
    "progress": 100,
    "result": {"features": [...], "user_stories": [...]},
    "error_message": null,
    "started_at": "2024-01-15T10:31:00Z",
    "completed_at": "2024-01-15T10:32:00Z",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

**Task Statuses:**
- `pending` - Waiting to be processed
- `running` - Currently being executed
- `completed` - Successfully finished
- `failed` - Encountered an error

### Get Task Details

```http
GET /api/tasks/{task_id}
Authorization: Bearer <token>
```

### Get Task Logs

```http
GET /api/tasks/{task_id}/logs
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "task_id": "uuid",
    "level": "info",
    "message": "Starting requirement analysis...",
    "timestamp": "2024-01-15T10:31:00Z",
    "details": null
  }
]
```

## Artifacts

### Get Project Artifacts

```http
GET /api/projects/{project_id}/artifacts
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "project_id": "uuid",
    "task_id": "uuid",
    "name": "main.py",
    "artifact_type": "code",
    "file_path": "/artifacts/project-uuid/main.py",
    "content": null,
    "metadata": {"language": "python", "lines": 150},
    "created_at": "2024-01-15T10:35:00Z"
  }
]
```

**Artifact Types:**
- `code` - Source code files
- `config` - Configuration files
- `diagram` - Architecture diagrams
- `documentation` - Markdown/text docs
- `json` - JSON data files

### Download Artifact

```http
GET /api/tasks/artifacts/{artifact_id}/download
Authorization: Bearer <token>
```

**Response:** File download with appropriate content-type

## WebSocket

Connect to receive real-time updates during code generation.

### Connect

```
WS /api/ws/{project_id}?token=<jwt_token>
```

### Message Types

**Task Started:**
```json
{
  "type": "task_started",
  "task_id": "uuid",
  "project_id": "uuid",
  "agent_type": "system_architect"
}
```

**Task Progress:**
```json
{
  "type": "task_progress",
  "task_id": "uuid",
  "progress": 45
}
```

**Task Completed:**
```json
{
  "type": "task_completed",
  "task_id": "uuid",
  "result": {...}
}
```

**Task Failed:**
```json
{
  "type": "task_failed",
  "task_id": "uuid",
  "error": "Error message"
}
```

**Log:**
```json
{
  "type": "log",
  "log": {
    "id": "uuid",
    "task_id": "uuid",
    "level": "info",
    "message": "Processing...",
    "timestamp": "2024-01-15T10:31:00Z",
    "details": null
  }
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Status Codes:**
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

API requests are rate-limited to:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated requests

Headers included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Timestamp when limit resets
