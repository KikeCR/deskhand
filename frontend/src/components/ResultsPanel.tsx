import { useEffect, useState } from 'react'
import { ClipboardText, MagnifyingGlass, UsersThree, WarningCircle } from '@phosphor-icons/react'
import type { OnboardingResponse } from '../api/types'
import { Card, CardContent } from './ui/Card'
import { DecisionLog } from './DecisionLog'
import { ResearchSources } from './ResearchSources'
import { ChecklistView } from './ChecklistView'

const PIPELINE_STAGES = [
  { icon: ClipboardText, label: 'Intake Agent', detail: 'Validating the hire profile' },
  { icon: MagnifyingGlass, label: 'Research Agent', detail: 'Searching the RAG vectorstore' },
  { icon: UsersThree, label: 'Reporting Agent', detail: 'Writing the checklist' },
]

export type ResultsState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'success'; result: OnboardingResponse }

export function ResultsPanel({ state }: { state: ResultsState }) {
  if (state.status === 'idle') return <IdleState />
  if (state.status === 'loading') return <LoadingState />
  if (state.status === 'error') return <ErrorState message={state.message} />

  const { result } = state
  return (
    <div className="flex flex-col gap-5">
      <DecisionLog decision={result.decision} />
      <ResearchSources researchNotes={result.research_notes} />
      <ChecklistView checklistMarkdown={result.checklist_markdown} outputPath={result.output_path} />
    </div>
  )
}

function IdleState() {
  return (
    <Card className="border-dashed">
      <CardContent className="flex flex-col items-center gap-2 py-16 text-center">
        <UsersThree size={28} weight="regular" className="text-muted-foreground" />
        <p className="text-sm font-medium">No run yet</p>
        <p className="max-w-xs text-sm text-muted-foreground">
          Pick a hire on the left and run the crew to see the decision log, grounded research,
          and the final checklist here.
        </p>
      </CardContent>
    </Card>
  )
}

function LoadingState() {
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    const id = setInterval(() => setElapsed((s) => s + 1), 1000)
    return () => clearInterval(id)
  }, [])

  return (
    <Card>
      <CardContent className="flex flex-col gap-4 py-6">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium">Running the onboarding crew</p>
          <span className="font-mono text-xs text-muted-foreground">{elapsed}s elapsed</span>
        </div>
        <div className="flex flex-col gap-3">
          {PIPELINE_STAGES.map(({ icon: Icon, label, detail }) => (
            <div key={label} className="flex items-center gap-3">
              <span className="motion-safe:animate-pulse flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                <Icon size={16} weight="regular" />
              </span>
              <span className="flex flex-col">
                <span className="text-sm font-medium">{label}</span>
                <span className="text-xs text-muted-foreground">{detail}</span>
              </span>
            </div>
          ))}
        </div>
        <p className="text-xs text-muted-foreground">
          A full crew run takes roughly 15 to 40 seconds depending on the model.
        </p>
      </CardContent>
    </Card>
  )
}

function ErrorState({ message }: { message: string }) {
  return (
    <Card className="border-destructive/30">
      <CardContent className="flex flex-col items-center gap-2 py-16 text-center">
        <WarningCircle size={28} weight="regular" className="text-destructive" />
        <p className="text-sm font-medium">Run failed</p>
        <p className="max-w-xs text-sm text-muted-foreground">{message}</p>
      </CardContent>
    </Card>
  )
}
