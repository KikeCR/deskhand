import { act, renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { useBackendStatus } from './useBackendStatus'
import * as apiClient from '../api/client'

describe('useBackendStatus', () => {
  it('starts as checking, then resolves to online when the backend is reachable', async () => {
    vi.spyOn(apiClient, 'checkHealth').mockResolvedValue(true)

    const { result } = renderHook(() => useBackendStatus())

    expect(result.current.status).toBe('checking')
    await waitFor(() => expect(result.current.status).toBe('online'))
  })

  it('resolves to offline when the backend is unreachable', async () => {
    vi.spyOn(apiClient, 'checkHealth').mockResolvedValue(false)

    const { result } = renderHook(() => useBackendStatus())

    await waitFor(() => expect(result.current.status).toBe('offline'))
  })

  it('recheck() re-runs the health check and can flip offline back to online', async () => {
    const checkHealthSpy = vi.spyOn(apiClient, 'checkHealth').mockResolvedValueOnce(false)

    const { result } = renderHook(() => useBackendStatus())
    await waitFor(() => expect(result.current.status).toBe('offline'))

    checkHealthSpy.mockResolvedValueOnce(true)
    act(() => {
      result.current.recheck()
    })

    expect(result.current.status).toBe('checking')
    await waitFor(() => expect(result.current.status).toBe('online'))
  })
})
