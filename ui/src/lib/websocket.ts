import { useEffect, useRef, useCallback } from 'react'

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

// =============================================================================
// Types
// =============================================================================

export interface WebSocketMessage {
  type: 
    | 'project_status'
    | 'task_started'
    | 'task_progress'
    | 'task_completed'
    | 'task_failed'
    | 'artifact_created'
    | 'log'
    | 'error'
  project_id: string
  task_id?: string
  status?: string
  progress?: number
  error?: string
  log?: {
    id?: string
    task_id?: string
    level: string
    message: string
    timestamp: string
  }
  artifact?: {
    id: string
    name: string
    artifact_type: string
  }
  data?: Record<string, unknown>
}

// =============================================================================
// Hook
// =============================================================================

export function useProjectWebSocket(
  projectId: string,
  token: string | null,
  onMessage: (message: WebSocketMessage) => void
) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  const connect = useCallback(() => {
    if (!projectId || !token) return

    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close()
    }

    const wsUrl = `${WS_BASE_URL}/api/v1/ws/${projectId}?token=${token}`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('[WebSocket] Connected to project:', projectId)
      reconnectAttempts.current = 0
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as WebSocketMessage
        onMessage(data)
      } catch (error) {
        console.error('[WebSocket] Failed to parse message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('[WebSocket] Error:', error)
    }

    ws.onclose = (event) => {
      console.log('[WebSocket] Disconnected:', event.code, event.reason)

      // Attempt to reconnect with exponential backoff
      if (reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttempts.current++
          connect()
        }, delay)
      }
    }

    wsRef.current = ws
  }, [projectId, token, onMessage])

  useEffect(() => {
    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connect])

  return wsRef.current
}

// =============================================================================
// Utility Functions
// =============================================================================

export function createWebSocketConnection(
  projectId: string,
  token: string,
  handlers: {
    onOpen?: () => void
    onMessage?: (message: WebSocketMessage) => void
    onError?: (error: Event) => void
    onClose?: (event: CloseEvent) => void
  }
): WebSocket {
  const wsUrl = `${WS_BASE_URL}/api/v1/ws/${projectId}?token=${token}`
  const ws = new WebSocket(wsUrl)

  if (handlers.onOpen) {
    ws.onopen = handlers.onOpen
  }

  if (handlers.onMessage) {
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as WebSocketMessage
        handlers.onMessage!(data)
      } catch (error) {
        console.error('[WebSocket] Failed to parse message:', error)
      }
    }
  }

  if (handlers.onError) {
    ws.onerror = handlers.onError
  }

  if (handlers.onClose) {
    ws.onclose = handlers.onClose
  }

  return ws
}
