'use client'

import { Task } from '@/lib/api'
import { Card, CardContent, Badge, Progress } from '@/components/ui'
import { formatRelativeTime, getAgentIcon } from '@/lib/utils'
import { Clock, CheckCircle2, XCircle, Loader2 } from 'lucide-react'

interface TaskProgressProps {
  tasks: Task[]
}

export function TaskProgress({ tasks }: TaskProgressProps) {
  const totalProgress = tasks.length > 0
    ? tasks.reduce((acc, task) => acc + task.progress, 0) / tasks.length
    : 0

  return (
    <Card>
      <CardContent>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-white">Generation Progress</h3>
          <span className="text-sm text-slate-400">
            {Math.round(totalProgress)}% Complete
          </span>
        </div>
        
        <Progress value={totalProgress} className="mb-6" />
        
        <div className="space-y-4">
          {tasks.map((task) => (
            <TaskItem key={task.id} task={task} />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function TaskItem({ task }: { task: Task }) {
  const icon = getAgentIcon(task.agent_type)
  
  const StatusIcon = () => {
    switch (task.status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'running':
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
      default:
        return <Clock className="h-4 w-4 text-slate-500" />
    }
  }

  return (
    <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg">
      <span className="text-xl">{icon}</span>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium text-white truncate">
            {task.name}
          </span>
          <Badge variant="status" status={task.status}>
            {task.status}
          </Badge>
        </div>
        
        {task.status === 'running' && (
          <Progress value={task.progress} className="h-1" />
        )}
        
        {task.started_at && (
          <span className="text-xs text-slate-500">
            Started {formatRelativeTime(task.started_at)}
          </span>
        )}
      </div>
      
      <StatusIcon />
    </div>
  )
}
