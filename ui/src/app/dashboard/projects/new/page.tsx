'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { apiClient } from '@/lib/api'
import { Button, Input, Textarea, Card, CardContent, CardHeader } from '@/components/ui'
import { ArrowLeft, Sparkles, Lightbulb } from 'lucide-react'
import Link from 'next/link'

const projectSchema = z.object({
  name: z.string().min(3, 'Project name must be at least 3 characters'),
  description: z.string().min(50, 'Please provide a detailed description (at least 50 characters)'),
})

type ProjectFormData = z.infer<typeof projectSchema>

const exampleDescriptions = [
  {
    title: 'E-Commerce Platform',
    description: `Build a modern e-commerce platform with the following features:
- User authentication and profiles
- Product catalog with categories and search
- Shopping cart and checkout flow
- Payment integration with Stripe
- Order management and tracking
- Admin dashboard for inventory management
- Email notifications for orders`
  },
  {
    title: 'Task Management App',
    description: `Create a collaborative task management application:
- Team workspaces with role-based access
- Kanban boards with drag-and-drop
- Task assignments and due dates
- Real-time updates and notifications
- Comments and file attachments
- Time tracking and reporting
- Calendar view and integrations`
  },
  {
    title: 'Social Media Dashboard',
    description: `Develop a social media analytics dashboard:
- Multi-platform integration (Twitter, Instagram, Facebook)
- Real-time metrics and engagement tracking
- Scheduled post management
- Audience insights and demographics
- Automated reporting and exports
- Competitor analysis features
- Content performance recommendations`
  },
]

export default function NewProjectPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
  })

  const createMutation = useMutation({
    mutationFn: (data: ProjectFormData) => apiClient.createProject(data),
    onSuccess: (project) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      router.push(`/dashboard/projects/${project.id}`)
    },
    onError: (err) => {
      setError(err instanceof Error ? err.message : 'Failed to create project')
    },
  })

  const onSubmit = (data: ProjectFormData) => {
    setError(null)
    createMutation.mutate(data)
  }

  const applyExample = (example: typeof exampleDescriptions[0]) => {
    setValue('name', example.title)
    setValue('description', example.description)
  }

  return (
    <div className="p-6 lg:p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link
          href="/dashboard/projects"
          className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Projects
        </Link>
        <h1 className="text-3xl font-bold text-white mb-2">Create New Project</h1>
        <p className="text-slate-400">
          Describe your application and let AI generate the complete architecture.
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Form */}
        <div className="lg:col-span-2">
          <Card>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {error && (
                  <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-500 text-sm">
                    {error}
                  </div>
                )}

                <Input
                  label="Project Name"
                  placeholder="My Awesome App"
                  error={errors.name?.message}
                  {...register('name')}
                />

                <Textarea
                  label="Product Description"
                  placeholder="Describe your application in detail. Include the main features, user types, and any specific requirements. The more detail you provide, the better the generated architecture will be."
                  rows={12}
                  error={errors.description?.message}
                  {...register('description')}
                />

                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <Sparkles className="h-4 w-4 text-primary-500" />
                  <span>
                    AI will analyze your description and generate architecture, APIs, database schema, and code.
                  </span>
                </div>

                <div className="flex gap-4 pt-4">
                  <Button
                    type="submit"
                    size="lg"
                    isLoading={createMutation.isPending}
                    className="flex-1"
                  >
                    Create Project
                  </Button>
                  <Link href="/dashboard/projects">
                    <Button variant="secondary" size="lg">
                      Cancel
                    </Button>
                  </Link>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Examples Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-yellow-500" />
                <h3 className="font-semibold text-white">Example Ideas</h3>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-slate-400">
                Click an example to use it as a starting point:
              </p>
              {exampleDescriptions.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => applyExample(example)}
                  className="w-full text-left p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors"
                >
                  <h4 className="font-medium text-white mb-1">{example.title}</h4>
                  <p className="text-xs text-slate-500 line-clamp-2">
                    {example.description.split('\n')[0]}
                  </p>
                </button>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
