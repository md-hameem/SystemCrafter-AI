import { cn, getStatusColor } from '@/lib/utils'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'status'
  status?: string
  className?: string
}

export function Badge({ children, variant = 'default', status, className }: BadgeProps) {
  const statusClass = status ? getStatusColor(status) : ''
  
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        variant === 'default' && 'bg-slate-700 text-slate-300',
        variant === 'status' && statusClass,
        className
      )}
    >
      {children}
    </span>
  )
}
