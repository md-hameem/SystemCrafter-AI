import Cookies from 'js-cookie'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// =============================================================================
// Types
// =============================================================================

export interface User {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  created_at: string
}

export interface Project {
  id: string
  name: string
  description: string
  status: 'pending' | 'analyzing' | 'designing' | 'generating' | 'building' | 'deploying' | 'completed' | 'failed'
  owner_id: string
  stack_preferences: Record<string, unknown> | null
  constraints: Record<string, unknown> | null
  repo_url: string | null
  local_path: string | null
  generated_artifacts?: boolean
  created_at: string
  updated_at: string
  completed_at: string | null
}

export interface Task {
  id: string
  project_id: string
  agent_type: string
  name: string
  status: 'queued' | 'running' | 'completed' | 'failed' | 'retrying'
  input_data: Record<string, unknown> | null
  output_data: Record<string, unknown> | null
  started_at: string | null
  completed_at: string | null
  duration_seconds: number | null
  error_message: string | null
  retry_count: number
  progress: number
  created_at: string
}

export interface TaskLog {
  id?: string
  task_id?: string
  level: string
  message: string
  timestamp: string
}

export interface Artifact {
  id: string
  project_id: string
  task_id: string | null
  artifact_type: string
  name: string
  file_path: string | null
  content: string | null
  metadata: Record<string, unknown> | null
  created_at: string
}

export interface CreateProjectData {
  name: string
  description: string
  stack_preferences?: {
    backend?: string
    frontend?: string
    database?: string
    cache?: string
    deployment?: string
  }
  constraints?: {
    language?: string
    hosting?: string
    budget?: string
    timeline?: string
    compliance?: string[]
  }
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

// =============================================================================
// API Client
// =============================================================================

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private getAuthHeaders(): HeadersInit {
    const token = Cookies.get('access_token')
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    return headers
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options.headers,
      },
    })

    if (!response.ok) {
      let errorMessage = 'Request failed'
      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorData.message || errorMessage
      } catch {
        errorMessage = response.statusText || errorMessage
      }
      throw new Error(errorMessage)
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null as T
    }

    return response.json()
  }

  // =========================================================================
  // Auth
  // =========================================================================

  async login(email: string, password: string): Promise<AuthResponse> {
    return this.request<AuthResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  }

  async register(
    email: string,
    password: string,
    fullName?: string
  ): Promise<User> {
    return this.request<User>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
      }),
    })
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/v1/auth/me')
  }

  // =========================================================================
  // Projects
  // =========================================================================

  async getProjects(skip = 0, limit = 100): Promise<Project[]> {
    const data = await this.request<any>(
      `/api/v1/projects?skip=${skip}&limit=${limit}`
    )

    // Backend returns a paginated response with an `items` array.
    if (data == null) return []
    if (Array.isArray(data)) return data
    if (Array.isArray(data.items)) return data.items
    return []
  }

  async getProject(id: string): Promise<Project> {
    return this.request<Project>(`/api/v1/projects/${id}`)
  }

  async createProject(data: CreateProjectData): Promise<Project> {
    return this.request<Project>('/api/v1/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateProject(
    id: string,
    data: Partial<CreateProjectData>
  ): Promise<Project> {
    return this.request<Project>(`/api/v1/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteProject(id: string): Promise<void> {
    return this.request<void>(`/api/v1/projects/${id}`, {
      method: 'DELETE',
    })
  }

  async startGeneration(projectId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(
      `/api/v1/projects/${projectId}/start`,
      {
        method: 'POST',
      }
    )
  }

  // =========================================================================
  // Tasks
  // =========================================================================

  async getProjectTasks(projectId: string): Promise<Task[]> {
    return this.request<Task[]>(`/api/v1/tasks/project/${projectId}`)
  }

  async getTask(taskId: string): Promise<Task> {
    return this.request<Task>(`/api/v1/tasks/${taskId}`)
  }

  // =========================================================================
  // Artifacts
  // =========================================================================

  async getProjectArtifacts(projectId: string): Promise<Artifact[]> {
    return this.request<Artifact[]>(`/api/v1/projects/${projectId}/artifacts`)
  }

  async downloadArtifact(artifactId: string): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/artifacts/${artifactId}/download`,
      {
        headers: this.getAuthHeaders(),
      }
    )

    if (!response.ok) {
      throw new Error('Failed to download artifact')
    }

    return response.blob()
  }

  async downloadProjectArtifacts(projectId: string): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/projects/${projectId}/download`,
      {
        headers: this.getAuthHeaders(),
      }
    )

    if (!response.ok) {
      throw new Error('Failed to download project artifacts')
    }

    return response.blob()
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
