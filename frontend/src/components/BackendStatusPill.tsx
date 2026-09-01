import { CheckCircle, CircleNotch, WarningCircle } from '@phosphor-icons/react'
import type { BackendStatus } from '../hooks/useBackendStatus'
import { Button } from './ui/Button'

interface BackendStatusPillProps {
  status: BackendStatus
  onRetry: () => void
}

export function BackendStatusPill({ status, onRetry }: BackendStatusPillProps) {
  if (status === 'online') {
    return (
      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <CheckCircle size={14} weight="fill" className="text-success" />
        Backend ready
      </div>
    )
  }

  if (status === 'checking') {
    return (
      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <CircleNotch size={14} weight="bold" className="motion-safe:animate-spin shrink-0" />
        Connecting to the backend. This can take up to a minute if it's been idle.
      </div>
    )
  }

  return (
    <div className="flex items-center justify-between gap-3 rounded-lg bg-destructive/10 px-3 py-2">
      <div className="flex items-center gap-1.5 text-xs text-destructive">
        <WarningCircle size={14} weight="fill" />
        Backend unreachable
      </div>
      <Button variant="ghost" size="sm" onClick={onRetry}>
        Retry
      </Button>
    </div>
  )
}
