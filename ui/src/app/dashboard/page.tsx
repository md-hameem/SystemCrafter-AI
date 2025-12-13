'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { apiClient } from '@/lib/api'
import { useAuthStore } from '@/lib/store'
import { Button, Card, CardContent } from '@/components/ui'
import { ProjectCard } from '@/components'
import { Plus, FolderKanban, Sparkles, TrendingUp } from 'lucide-react'

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user)

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => apiClient.getProjects(0, 6),
  })

  const activeStatuses = ['analyzing', 'designing', 'generating', 'building', 'deploying'] as const
  const stats = {
    totalProjects: projects?.length || 0,
    completed: projects?.filter((p) => p.status === 'completed').length || 0,
    inProgress: projects?.filter((p) => activeStatuses.includes(p.status as typeof activeStatuses[number])).length || 0,
  }

  return (
    <div className="p-6 lg:p-8">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Welcome back{user?.full_name ? `, ${user.full_name}` : ''}! 👋
        </h1>
        <p className="text-slate-400">
          Ready to build something amazing? Start a new project or continue where you left off.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <Card>
          <CardContent className="flex items-center gap-4">
            <div className="p-3 bg-primary-600/20 rounded-lg">
              <FolderKanban className="h-6 w-6 text-primary-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{stats.totalProjects}</p>
              <p className="text-sm text-slate-400">Total Projects</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center gap-4">
            <div className="p-3 bg-green-600/20 rounded-lg">
              <Sparkles className="h-6 w-6 text-green-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{stats.completed}</p>
              <p className="text-sm text-slate-400">Completed</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center gap-4">
            <div className="p-3 bg-blue-600/20 rounded-lg">
              <TrendingUp className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{stats.inProgress}</p>
              <p className="text-sm text-slate-400">In Progress</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Projects */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Recent Projects</h2>
          <Link href="/dashboard/projects">
            <Button variant="ghost" size="sm">
              View All
            </Button>
          </Link>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(3)].map((_, i) => (
              <Card key={i} className="h-48 animate-pulse">
                <CardContent>
                  <div className="h-4 bg-slate-700 rounded w-2/3 mb-4" />
                  <div className="h-3 bg-slate-700 rounded w-full mb-2" />
                  <div className="h-3 bg-slate-700 rounded w-4/5" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : projects && projects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.slice(0, 6).map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="text-center py-12">
              <FolderKanban className="h-12 w-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">
                No projects yet
              </h3>
              <p className="text-slate-400 mb-6">
                Create your first project to get started with AI-powered architecture generation.
              </p>
              <Link href="/dashboard/projects/new">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Project
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-4">
          <Link href="/dashboard/projects/new">
            <Button size="lg">
              <Plus className="h-5 w-5 mr-2" />
              New Project
            </Button>
          </Link>
          <Link href="/dashboard/projects">
            <Button variant="secondary" size="lg">
              <FolderKanban className="h-5 w-5 mr-2" />
              Browse Projects
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
