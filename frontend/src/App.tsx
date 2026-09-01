import { useState } from 'react'
import { ArrowRight, ClipboardText, MagnifyingGlass, UsersThree } from '@phosphor-icons/react'
import { runOnboarding } from './api/client'
import type { HireProfile } from './api/types'
import { Footer } from './components/Footer'
import { HirePicker } from './components/HirePicker'
import { Logo } from './components/Logo'
import { ResultsPanel, type ResultsState } from './components/ResultsPanel'
import { useBackendStatus } from './hooks/useBackendStatus'

const PIPELINE = [
  { icon: ClipboardText, label: 'Intake' },
  { icon: MagnifyingGlass, label: 'Research' },
  { icon: UsersThree, label: 'Reporting' },
]

function App() {
  const [state, setState] = useState<ResultsState>({ status: 'idle' })
  const [lastHire, setLastHire] = useState<HireProfile | null>(null)
  const { status: backendStatus, recheck: recheckBackend } = useBackendStatus()

  async function handleRun(hire: HireProfile) {
    setLastHire(hire)
    setState({ status: 'loading' })
    try {
      const result = await runOnboarding(hire)
      setState({ status: 'success', result })
    } catch {
      setState({
        status: 'error',
        message: 'Could not reach the onboarding API. Confirm the backend is running on port 8000.',
      })
    }
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="border-b border-border">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-6 py-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <Logo />
            <div>
              <h1 className="text-lg font-semibold tracking-tight">DeskHand</h1>
              <p className="text-sm text-muted-foreground">
                RAG-grounded, multi-agent onboarding automation
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 font-mono text-xs text-muted-foreground">
            {PIPELINE.map(({ icon: Icon, label }, i) => (
              <span key={label} className="flex items-center gap-2">
                <span className="flex items-center gap-1.5">
                  <Icon size={14} weight="regular" />
                  {label}
                </span>
                {i < PIPELINE.length - 1 && <ArrowRight size={12} weight="regular" />}
              </span>
            ))}
          </div>
        </div>
      </header>

      <main className="mx-auto grid w-full max-w-6xl flex-1 grid-cols-1 items-start gap-6 px-6 py-8 md:grid-cols-[360px_1fr]">
        <div className="md:sticky md:top-8 md:self-start">
          <HirePicker
            onRun={handleRun}
            isRunning={state.status === 'loading'}
            backendStatus={backendStatus}
            onRetryBackend={recheckBackend}
          />
        </div>
        <ResultsPanel state={state} onRetry={lastHire ? () => handleRun(lastHire) : undefined} />
      </main>

      <Footer />
    </div>
  )
}

export default App
