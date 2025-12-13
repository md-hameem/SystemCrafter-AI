'use client'

import { useEffect, useState, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import Cookies from 'js-cookie'
import { apiClient, Task, TaskLog } from '@/lib/api'
import { useProjectWebSocket, WebSocketMessage } from '@/lib/websocket'
import { Button, Card, CardContent, CardHeader, Badge } from '@/components/ui'
import { TaskProgress, LogViewer, ArtifactBrowser } from '@/components'
import { formatRelativeTime } from '@/lib/utils'
import { 
  ArrowLeft, 
  Play, 
  Trash2, 
  Edit2,
  Download,
  RefreshCw
} from 'lucide-react'

export default function ProjectDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const projectId = params.id as string
  
  const [tasks, setTasks] = useState<Task[]>([])
  const [logs, setLogs] = useState<TaskLog[]>([])
  const [isGenerating, setIsGenerating] = useState(false)

  // Fetch project
  const { data: project, isLoading: projectLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => apiClient.getProject(projectId),
  })

  // Fetch tasks
  const { data: fetchedTasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['tasks', projectId],
    queryFn: () => apiClient.getProjectTasks(projectId),
    refetchInterval: isGenerating ? 5000 : false,
  })

  // Fetch artifacts
  const { data: artifacts, refetch: refetchArtifacts } = useQuery({
    queryKey: ['artifacts', projectId],
    queryFn: () => apiClient.getProjectArtifacts(projectId),
  })

  // Update tasks when fetched
  useEffect(() => {
    if (fetchedTasks) {
      setTasks(fetchedTasks)
      // Check if any task is running
      const hasRunningTask = fetchedTasks.some((t) => t.status === 'running')
      setIsGenerating(hasRunningTask)
    }
  }, [fetchedTasks])

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'task_started':
        setIsGenerating(true)
        setTasks((prev) => 
          prev.map((t) => 
            t.id === message.task_id 
              ? { ...t, status: 'running' as const, progress: 0 }
              : t
          )
        )
        break
      case 'task_progress':
        setTasks((prev) =>
          prev.map((t) =>
            t.id === message.task_id
              ? { ...t, progress: message.progress || t.progress }
              : t
          )
        )
        break
      case 'task_completed':
        setTasks((prev) =>
          prev.map((t) =>
            t.id === message.task_id
              ? { ...t, status: 'completed' as const, progress: 100 }
              : t
          )
        )
        refetchArtifacts()
        break
      case 'task_failed':
        setTasks((prev) =>
          prev.map((t) =>
            t.id === message.task_id
              ? { ...t, status: 'failed' as const, error_message: message.error || null }
              : t
          )
        )
        setIsGenerating(false)
        break
      case 'log':
        if (message.log) {
          setLogs((prev) => [...prev, message.log!])
        }
        break
    }
  }, [refetchArtifacts])

  // WebSocket connection
  const token = Cookies.get('access_token')
  useProjectWebSocket(projectId, token || null, handleWebSocketMessage)

  // Start generation mutation
  const startMutation = useMutation({
    mutationFn: () => apiClient.startGeneration(projectId),
    onSuccess: () => {
      setIsGenerating(true)
      setLogs([])
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] })
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: () => apiClient.deleteProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      router.push('/dashboard/projects')
    },
  })

  if (projectLoading) {
    return (
      <div className="p-6 lg:p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-700 rounded w-1/3 mb-4" />
          <div className="h-4 bg-slate-700 rounded w-2/3" />
        </div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="p-6 lg:p-8">
        <Card>
          <CardContent className="text-center py-12">
            <h2 className="text-xl font-semibold text-white mb-2">Project Not Found</h2>
            <p className="text-slate-400 mb-4">The project you're looking for doesn't exist.</p>
            <Link href="/dashboard/projects">
              <Button>Back to Projects</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8">
        <Link
          href="/dashboard/projects"
          className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Projects
        </Link>
        
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-white">{project.name}</h1>
              <Badge variant="status" status={project.status}>
                {project.status.replace('_', ' ')}
              </Badge>
            </div>
            <p className="text-slate-400 max-w-2xl">{project.description}</p>
            <p className="text-sm text-slate-500 mt-2">
              Created {formatRelativeTime(project.created_at)}
            </p>
          </div>
          
          <div className="flex gap-3">
            {project.status === 'pending' && (
              <Button
                onClick={() => startMutation.mutate()}
                isLoading={startMutation.isPending || isGenerating}
              >
                <Play className="h-4 w-4 mr-2" />
                {isGenerating ? 'Generating...' : 'Start Generation'}
              </Button>
            )}
            {project.status === 'completed' && (
              <Button variant="secondary">
                <Download className="h-4 w-4 mr-2" />
                Download All
              </Button>
            )}
            <Button variant="ghost" size="sm">
              <Edit2 className="h-4 w-4" />
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={() => {
                if (confirm('Are you sure you want to delete this project?')) {
                  deleteMutation.mutate()
                }
              }}
              isLoading={deleteMutation.isPending}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Tasks Progress */}
        <div className="space-y-6">
          <TaskProgress tasks={tasks} />
          
          {/* Logs */}
          <LogViewer logs={logs} maxHeight="300px" />
        </div>

        {/* Artifacts */}
        <div>
          <ArtifactBrowser artifacts={artifacts || []} />
        </div>
      </div>
    </div>
  )
}
