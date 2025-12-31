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

    // Avoid creating a new connection if one is already open or connecting
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      console.debug('[WebSocket] connection already open or connecting - skipping new connect')
      return
    }

    const wsUrl = `${WS_BASE_URL}/api/v1/ws/${projectId}?token=${token}`
    console.debug('[WebSocket] connecting to', wsUrl)
    // Close any previous connection (if in CLOSING/DEAD state)
    try {
      wsRef.current?.close()
    } catch (err) {
      // ignore
    }

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('[WebSocket] Connected to project:', projectId)
      reconnectAttempts.current = 0
    }

    ws.onmessage = (event) => {
      // Skip heartbeat pong responses
      if (event.data === 'pong') {
        return
      }
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
      console.warn('[WebSocket] Disconnected:', event.code, event.reason)

      // Only attempt reconnect for non-normal closures
      if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttempts.current++
          connect()
        }, delay)
      }
    }

    // Heartbeat ping to keep the connection alive and detect stale sockets
    const heartbeat = setInterval(() => {
      try {
        if (ws.readyState === WebSocket.OPEN) ws.send('ping')
      } catch (err) {
        // ignore
      }
    }, 15000)

    // Clean up heartbeat when socket closes
    ws.addEventListener('close', () => clearInterval(heartbeat))

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
      // Skip heartbeat pong responses
      if (event.data === 'pong') {
        return
      }
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
