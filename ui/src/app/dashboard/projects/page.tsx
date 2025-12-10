'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import { apiClient } from '@/lib/api'
import { Button, Card, CardContent } from '@/components/ui'
import { ProjectCard } from '@/components'
import { Plus, Search, FolderKanban } from 'lucide-react'
import { useState } from 'react'

export default function ProjectsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const queryClient = useQueryClient()

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => apiClient.getProjects(0, 100),
  })

  const filteredProjects = projects?.filter((project) =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="p-6 lg:p-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-1">Projects</h1>
          <p className="text-slate-400">
            Manage and monitor your AI-generated projects
          </p>
        </div>
        <Link href="/dashboard/projects/new">
          <Button size="lg">
            <Plus className="h-5 w-5 mr-2" />
            New Project
          </Button>
        </Link>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
        <input
          type="text"
          placeholder="Search projects..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {/* Projects Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="h-56 animate-pulse">
              <CardContent>
                <div className="h-4 bg-slate-700 rounded w-2/3 mb-4" />
                <div className="h-3 bg-slate-700 rounded w-full mb-2" />
                <div className="h-3 bg-slate-700 rounded w-4/5" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredProjects && filteredProjects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="text-center py-16">
            <FolderKanban className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-white mb-2">
              {searchQuery ? 'No matching projects' : 'No projects yet'}
            </h3>
            <p className="text-slate-400 mb-6 max-w-md mx-auto">
              {searchQuery
                ? 'Try adjusting your search query to find what you\'re looking for.'
                : 'Create your first project to start generating production-ready code with AI.'}
            </p>
            {!searchQuery && (
              <Link href="/dashboard/projects/new">
                <Button size="lg">
                  <Plus className="h-5 w-5 mr-2" />
                  Create Your First Project
                </Button>
              </Link>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
