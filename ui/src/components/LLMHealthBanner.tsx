"use client"

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { getLLMHealth } from '@/lib/llm'

export function LLMHealthBanner() {
  const { data } = useQuery({
    queryKey: ['llm', 'health'],
    queryFn: getLLMHealth,
    refetchInterval: 15000,
    refetchOnWindowFocus: false,
  })

  if (!data) return null

  if (data.ok) return null

  return (
    <div className="w-full bg-amber-600 text-black px-4 py-2 text-sm flex items-center justify-between">
      <div>
        <strong>LLM Unhealthy:</strong>
        <span className="ml-2">{data.message || 'Unknown issue with LLM provider'}</span>
      </div>
      <div className="text-xs opacity-90">Auto-refreshes</div>
    </div>
  )
}

export default LLMHealthBanner
