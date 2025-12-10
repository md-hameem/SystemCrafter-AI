'use client'

import Link from 'next/link'
import { Project } from '@/lib/api'
import { Card, CardContent, CardFooter, Badge } from '@/components/ui'
import { formatRelativeTime } from '@/lib/utils'
import { ArrowRight, Calendar, FileCode } from 'lucide-react'

interface ProjectCardProps {
  project: Project
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Link href={`/dashboard/projects/${project.id}`}>
      <Card className="hover:border-primary-500/50 transition-colors cursor-pointer h-full">
        <CardContent className="flex flex-col h-full">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-lg font-semibold text-white truncate flex-1">
              {project.name}
            </h3>
            <Badge variant="status" status={project.status}>
              {project.status.replace('_', ' ')}
            </Badge>
          </div>
          
          <p className="text-slate-400 text-sm mb-4 line-clamp-3 flex-1">
            {project.description}
          </p>
          
          <div className="flex items-center gap-4 text-xs text-slate-500">
            <div className="flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" />
              <span>{formatRelativeTime(project.created_at)}</span>
            </div>
            {project.generated_artifacts && (
              <div className="flex items-center gap-1">
                <FileCode className="h-3.5 w-3.5" />
                <span>Has artifacts</span>
              </div>
            )}
          </div>
        </CardContent>
        
        <CardFooter className="flex justify-end">
          <span className="text-primary-500 text-sm flex items-center gap-1 group-hover:gap-2 transition-all">
            View Details
            <ArrowRight className="h-4 w-4" />
          </span>
        </CardFooter>
      </Card>
    </Link>
  )
}
