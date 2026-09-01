import { afterEach, describe, expect, it, vi } from 'vitest'
import { checkHealth } from './client'

describe('checkHealth', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns true when the backend responds ok', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: true }),
    )

    await expect(checkHealth()).resolves.toBe(true)
  })

  it('returns false when the backend responds with an error status', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false }),
    )

    await expect(checkHealth()).resolves.toBe(false)
  })

  it('returns false when the request throws (network error, abort, etc.)', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new Error('network error')),
    )

    await expect(checkHealth()).resolves.toBe(false)
  })
})
