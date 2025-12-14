export interface LLMHealth {
  ok: boolean
  message?: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function getLLMHealth(): Promise<LLMHealth> {
  const res = await fetch(`${API_BASE}/api/v1/llm/health`)
  if (!res.ok) {
    try {
      const body = await res.json()
      return { ok: false, message: body?.message || res.statusText }
    } catch {
      return { ok: false, message: res.statusText }
    }
  }

  try {
    const body = await res.json()
    return { ok: !!body.ok, message: body.message }
  } catch {
    return { ok: false, message: 'Invalid response' }
  }
}
