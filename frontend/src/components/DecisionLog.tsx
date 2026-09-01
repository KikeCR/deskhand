import { Briefcase, GitBranch, MapPin } from '@phosphor-icons/react'
import type { Decision } from '../api/types'
import { Badge } from './ui/Badge'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { cn } from '../lib/cn'

const TRACK_LABELS: Record<string, string> = {
  remote: 'Remote',
  in_office: 'In-office',
  engineering: 'Engineering',
  sales: 'Sales',
  general: 'General',
}

function label(track: string): string {
  return TRACK_LABELS[track] ?? track
}

interface DecisionLogProps {
  decision: Decision
}

export function DecisionLog({ decision }: DecisionLogProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Decision log</CardTitle>
        <p className="text-sm text-muted-foreground">
          Two independent, rule-based branches decide which onboarding steps this hire gets.
          This is plain code, not a model guess, so the same inputs always produce the same
          branch.
        </p>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <TrackCard
            icon={<MapPin size={18} weight="regular" />}
            eyebrow="Location track"
            trackName={label(decision.location_track)}
            steps={decision.location_steps}
            variant="location"
          />
          <TrackCard
            icon={<Briefcase size={18} weight="regular" />}
            eyebrow="Department track"
            trackName={label(decision.dept_track)}
            steps={decision.dept_steps}
            variant="department"
          />
        </div>

        <div className="flex flex-col gap-1.5 rounded-lg bg-muted px-4 py-3">
          <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
            <GitBranch size={14} weight="regular" />
            Decision trace
          </div>
          {decision.explanation.map((line) => (
            <p key={line} className="font-mono text-xs leading-relaxed text-foreground">
              {line}
            </p>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

interface TrackCardProps {
  icon: React.ReactNode
  eyebrow: string
  trackName: string
  steps: string[]
  variant: 'location' | 'department'
}

function TrackCard({ icon, eyebrow, trackName, steps, variant }: TrackCardProps) {
  return (
    <div
      className={cn(
        'flex flex-col gap-3 rounded-lg border border-border p-4',
        variant === 'location' ? 'border-t-2 border-t-track-location' : 'border-t-2 border-t-track-department',
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground">{eyebrow}</span>
        <Badge variant={variant}>
          {icon}
          {trackName}
        </Badge>
      </div>
      <ul className="flex flex-col gap-1.5">
        {steps.map((step) => (
          <li key={step} className="flex gap-2 text-sm leading-snug">
            <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-muted-foreground" />
            {step}
          </li>
        ))}
      </ul>
    </div>
  )
}
