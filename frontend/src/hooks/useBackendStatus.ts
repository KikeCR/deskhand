import { useCallback, useEffect, useState } from 'react'
import { checkHealth } from '../api/client'

export type BackendStatus = 'checking' | 'online' | 'offline'

/**
 * Confirms the backend is actually reachable before the UI claims a run
 * will take its usual 15-40 seconds. On a free-tier host the backend can
 * be asleep and take up to a minute just to wake up on the first request,
 * which is a different wait than the crew itself running, and worth
 * telling the user about separately.
 */
export function useBackendStatus() {
  const [status, setStatus] = useState<BackendStatus>('checking')

  const check = useCallback(() => {
    setStatus('checking')
    checkHealth().then((ok) => setStatus(ok ? 'online' : 'offline'))
  }, [])

  useEffect(() => {
    check()
  }, [check])

  return { status, recheck: check }
}
