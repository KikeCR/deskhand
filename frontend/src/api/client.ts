import type { HireProfile, OnboardingResponse } from './types'

export class ApiError extends Error {}

export async function fetchSampleHires(): Promise<HireProfile[]> {
  const res = await fetch('/api/sample-hires')
  if (!res.ok) throw new ApiError('Failed to load sample hires')
  return res.json()
}

export async function runOnboarding(hire: HireProfile): Promise<OnboardingResponse> {
  const res = await fetch('/api/onboarding/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(hire),
  })
  if (!res.ok) throw new ApiError('The onboarding run failed. Please try again.')
  return res.json()
}
