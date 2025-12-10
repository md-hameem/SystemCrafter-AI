'use client'

import { Artifact } from '@/lib/api'
import { Card, CardContent, CardHeader, Button } from '@/components/ui'
import { formatRelativeTime, cn } from '@/lib/utils'
import { apiClient } from '@/lib/api'
import { 
  FileCode, 
  FileJson, 
  FileText, 
  FileImage, 
  Download,
  FolderOpen,
  File
} from 'lucide-react'

interface ArtifactBrowserProps {
  artifacts: Artifact[]
}

export function ArtifactBrowser({ artifacts }: ArtifactBrowserProps) {
  const handleDownload = async (artifact: Artifact) => {
    try {
      const blob = await apiClient.downloadArtifact(artifact.id)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = artifact.name
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'code':
        return <FileCode className="h-5 w-5 text-blue-400" />
      case 'json':
      case 'config':
        return <FileJson className="h-5 w-5 text-yellow-400" />
      case 'diagram':
      case 'image':
        return <FileImage className="h-5 w-5 text-purple-400" />
      case 'documentation':
        return <FileText className="h-5 w-5 text-green-400" />
      default:
        return <File className="h-5 w-5 text-slate-400" />
    }
  }

  // Group artifacts by type
  const groupedArtifacts = artifacts.reduce((acc, artifact) => {
    const type = artifact.artifact_type
    if (!acc[type]) {
      acc[type] = []
    }
    acc[type].push(artifact)
    return acc
  }, {} as Record<string, Artifact[]>)

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <FolderOpen className="h-5 w-5 text-primary-500" />
          <h3 className="text-lg font-semibold text-white">Generated Artifacts</h3>
        </div>
      </CardHeader>
      <CardContent>
        {artifacts.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            No artifacts generated yet
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(groupedArtifacts).map(([type, items]) => (
              <div key={type}>
                <h4 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">
                  {type.replace('_', ' ')}
                </h4>
                <div className="space-y-2">
                  {items.map((artifact) => (
                    <div
                      key={artifact.id}
                      className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors"
                    >
                      <div className="flex items-center gap-3 min-w-0 flex-1">
                        {getFileIcon(artifact.artifact_type)}
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-white truncate">
                            {artifact.name}
                          </p>
                          <p className="text-xs text-slate-500">
                            {formatRelativeTime(artifact.created_at)}
                          </p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDownload(artifact)}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
