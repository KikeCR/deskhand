import { useEffect, useState } from 'react'
import { Buildings, House, UserCircle } from '@phosphor-icons/react'
import { fetchSampleHires } from '../api/client'
import type { HireProfile } from '../api/types'
import { Button } from './ui/Button'
import { Card, CardContent } from './ui/Card'
import { cn } from '../lib/cn'

const EMPTY_CUSTOM_HIRE: HireProfile = {
  name: '',
  role: '',
  department: '',
  location: 'remote',
  start_date: '',
}

interface HirePickerProps {
  onRun: (hire: HireProfile) => void
  isRunning: boolean
}

export function HirePicker({ onRun, isRunning }: HirePickerProps) {
  const [sampleHires, setSampleHires] = useState<HireProfile[]>([])
  const [loadError, setLoadError] = useState(false)
  const [selectedName, setSelectedName] = useState<string | 'custom' | null>(null)
  const [customHire, setCustomHire] = useState<HireProfile>(EMPTY_CUSTOM_HIRE)

  useEffect(() => {
    fetchSampleHires()
      .then((hires) => {
        setSampleHires(hires)
        setSelectedName(hires[0]?.name ?? 'custom')
      })
      .catch(() => setLoadError(true))
  }, [])

  const selectedHire =
    selectedName === 'custom'
      ? customHire
      : (sampleHires.find((h) => h.name === selectedName) ?? null)

  const isCustomValid = Object.values(customHire).every((v) => v.trim().length > 0)
  const canRun = selectedName === 'custom' ? isCustomValid : selectedHire !== null

  return (
    <Card>
      <CardContent className="flex flex-col gap-5 pt-5">
        <div>
          <h2 className="text-sm font-semibold tracking-tight">New hire</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Pick a bundled sample hire or enter a custom profile.
          </p>
        </div>

        {loadError && (
          <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
            Could not load sample hires. Is the backend running?
          </p>
        )}

        <div className="flex flex-col gap-2">
          {sampleHires.map((hire) => (
            <button
              key={hire.name}
              type="button"
              onClick={() => setSelectedName(hire.name)}
              className={cn(
                'flex items-center gap-3 rounded-lg border px-3 py-2.5 text-left transition-colors cursor-pointer',
                selectedName === hire.name
                  ? 'border-primary bg-primary/5'
                  : 'border-border hover:bg-muted',
              )}
            >
              {hire.location === 'remote' ? (
                <House className="shrink-0 text-muted-foreground" size={20} />
              ) : (
                <Buildings className="shrink-0 text-muted-foreground" size={20} />
              )}
              <span className="flex flex-col">
                <span className="text-sm font-medium">{hire.name}</span>
                <span className="text-xs text-muted-foreground">
                  {hire.role} &middot; {hire.department}
                </span>
              </span>
            </button>
          ))}

          <button
            type="button"
            onClick={() => setSelectedName('custom')}
            className={cn(
              'flex items-center gap-3 rounded-lg border px-3 py-2.5 text-left transition-colors cursor-pointer',
              selectedName === 'custom'
                ? 'border-primary bg-primary/5'
                : 'border-border hover:bg-muted',
            )}
          >
            <UserCircle className="shrink-0 text-muted-foreground" size={20} />
            <span className="text-sm font-medium">Custom hire</span>
          </button>
        </div>

        {selectedName === 'custom' && (
          <div className="flex flex-col gap-3 border-t border-border pt-4">
            <Field label="Name">
              <input
                className={inputClass}
                value={customHire.name}
                onChange={(e) => setCustomHire({ ...customHire, name: e.target.value })}
                placeholder="Jordan Reyes"
              />
            </Field>
            <Field label="Role">
              <input
                className={inputClass}
                value={customHire.role}
                onChange={(e) => setCustomHire({ ...customHire, role: e.target.value })}
                placeholder="Support Engineer"
              />
            </Field>
            <Field label="Department">
              <input
                className={inputClass}
                value={customHire.department}
                onChange={(e) => setCustomHire({ ...customHire, department: e.target.value })}
                placeholder="Engineering"
              />
            </Field>
            <Field label="Location">
              <select
                className={inputClass}
                value={customHire.location}
                onChange={(e) => setCustomHire({ ...customHire, location: e.target.value })}
              >
                <option value="remote">Remote</option>
                <option value="in_office">In-office</option>
              </select>
            </Field>
            <Field label="Start date">
              <input
                type="date"
                className={inputClass}
                value={customHire.start_date}
                onChange={(e) => setCustomHire({ ...customHire, start_date: e.target.value })}
              />
            </Field>
          </div>
        )}

        <Button
          disabled={!canRun || isRunning}
          onClick={() => selectedHire && onRun(selectedHire)}
        >
          {isRunning ? 'Running the crew...' : 'Run onboarding'}
        </Button>
      </CardContent>
    </Card>
  )
}

const inputClass =
  'h-9 rounded-md border border-border bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring'

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      {children}
    </label>
  )
}
