import type { HireProfile, OnboardingResponse } from './types'

export class ApiError extends Error {}

// Empty string keeps requests relative in local dev, where Vite's dev
// server proxies /api to the backend (see vite.config.ts). In production
// there's no such proxy, so a deployed frontend sets VITE_API_BASE_URL to
// the backend's absolute URL (e.g. https://deskhand-api.onrender.com).
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

/**
 * Pings /api/health with a generous timeout, so callers can tell "backend
 * is genuinely down" apart from "backend is asleep on a free-tier host and
 * waking up" before claiming a run will take its usual 15-40 seconds.
 */
export async function checkHealth(timeoutMs = 60_000): Promise<boolean> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`, { signal: controller.signal })
    return res.ok
  } catch {
    return false
  } finally {
    clearTimeout(timeout)
  }
}

export async function fetchSampleHires(): Promise<HireProfile[]> {
  const res = await fetch(`${API_BASE_URL}/api/sample-hires`)
  if (!res.ok) throw new ApiError('Failed to load sample hires')
  return res.json()
}

export async function runOnboarding(hire: HireProfile): Promise<OnboardingResponse> {
  const res = await fetch(`${API_BASE_URL}/api/onboarding/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(hire),
  })
  if (!res.ok) throw new ApiError('The onboarding run failed. Please try again.')
  return res.json()
}
