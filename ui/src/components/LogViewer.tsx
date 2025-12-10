'use client'

import { useEffect, useRef } from 'react'
import { TaskLog } from '@/lib/api'
import { Card, CardContent, CardHeader } from '@/components/ui'
import { cn } from '@/lib/utils'
import { Terminal } from 'lucide-react'

interface LogViewerProps {
  logs: TaskLog[]
  maxHeight?: string
  autoScroll?: boolean
}

export function LogViewer({ logs, maxHeight = '400px', autoScroll = true }: LogViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  const getLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'error':
        return 'text-red-400'
      case 'warning':
        return 'text-yellow-400'
      case 'info':
        return 'text-blue-400'
      case 'success':
        return 'text-green-400'
      default:
        return 'text-slate-400'
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Terminal className="h-5 w-5 text-primary-500" />
          <h3 className="text-lg font-semibold text-white">Logs</h3>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div
          ref={containerRef}
          className="font-mono text-xs overflow-auto bg-slate-900 p-4"
          style={{ maxHeight }}
        >
          {logs.length === 0 ? (
            <div className="text-slate-500 text-center py-8">
              No logs yet...
            </div>
          ) : (
            logs.map((log, index) => (
              <div key={log.id || index} className="flex gap-2 py-1 hover:bg-slate-800/50">
                <span className="text-slate-600 shrink-0">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span className={cn('shrink-0 uppercase w-16', getLevelColor(log.level))}>
                  [{log.level}]
                </span>
                <span className="text-slate-300 break-all">
                  {log.message}
                </span>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}
