import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Combines class names with tailwind-merge for proper precedence
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format a date to relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date: string | Date): string {
  const now = new Date()
  const then = new Date(date)
  const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000)

  if (diffInSeconds < 60) {
    return 'just now'
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60)
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`
  }

  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`
  }

  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) {
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`
  }

  const diffInWeeks = Math.floor(diffInDays / 7)
  if (diffInWeeks < 4) {
    return `${diffInWeeks} week${diffInWeeks > 1 ? 's' : ''} ago`
  }

  const diffInMonths = Math.floor(diffInDays / 30)
  if (diffInMonths < 12) {
    return `${diffInMonths} month${diffInMonths > 1 ? 's' : ''} ago`
  }

  const diffInYears = Math.floor(diffInDays / 365)
  return `${diffInYears} year${diffInYears > 1 ? 's' : ''} ago`
}

/**
 * Get status color class based on status value
 */
export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'completed':
    case 'success':
      return 'bg-green-500/20 text-green-400 border-green-500/50'
    case 'running':
    case 'in_progress':
    case 'analyzing':
    case 'designing':
    case 'generating':
    case 'building':
    case 'deploying':
      return 'bg-blue-500/20 text-blue-400 border-blue-500/50'
    case 'failed':
    case 'error':
      return 'bg-red-500/20 text-red-400 border-red-500/50'
    case 'queued':
    case 'pending':
      return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50'
    case 'retrying':
      return 'bg-orange-500/20 text-orange-400 border-orange-500/50'
    default:
      return 'bg-slate-500/20 text-slate-400 border-slate-500/50'
  }
}

/**
 * Get agent icon emoji based on agent type
 */
export function getAgentIcon(agentType: string): string {
  switch (agentType.toLowerCase()) {
    case 'requirement_interpreter':
      return '📋'
    case 'system_architect':
      return '🏗️'
    case 'api_designer':
      return '🔌'
    case 'db_designer':
      return '🗄️'
    case 'backend_generator':
      return '⚙️'
    case 'frontend_generator':
      return '🎨'
    case 'infra_engineer':
      return '☁️'
    case 'builder':
      return '🔨'
    case 'deployer':
      return '🚀'
    case 'qa_agent':
      return '🧪'
    case 'recovery_agent':
      return '🔧'
    default:
      return '🤖'
  }
}

/**
 * Capitalize first letter of a string
 */
export function capitalize(str: string): string {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

/**
 * Truncate a string to a maximum length
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str
  return str.slice(0, maxLength - 3) + '...'
}
