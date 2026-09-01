import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ResultsPanel, type ResultsState } from './ResultsPanel'
import type { OnboardingResponse } from '../api/types'

vi.mock('./DecisionLog', () => ({
  DecisionLog: () => <div>stub-decision-log</div>,
}))
vi.mock('./ResearchSources', () => ({
  ResearchSources: () => <div>stub-research-sources</div>,
}))
vi.mock('./ChecklistView', () => ({
  ChecklistView: () => <div>stub-checklist-view</div>,
}))

const successResult: OnboardingResponse = {
  hire: {
    name: 'Priya Nakamura',
    role: 'Software Engineer II',
    department: 'Engineering',
    location: 'remote',
    start_date: '2026-09-15',
  },
  decision: {
    location_track: 'remote',
    location_steps: [],
    dept_track: 'engineering',
    dept_steps: [],
    explanation: [],
  },
  research_notes: 'notes',
  checklist_markdown: '# Checklist',
  output_path: '/tmp/out.md',
}

describe('ResultsPanel', () => {
  it('shows the idle empty state', () => {
    render(<ResultsPanel state={{ status: 'idle' }} />)

    expect(screen.getByText('No run yet')).toBeInTheDocument()
  })

  it('shows the loading state with the pipeline stages', () => {
    render(<ResultsPanel state={{ status: 'loading' }} />)

    expect(screen.getByText('Running the onboarding crew')).toBeInTheDocument()
    expect(screen.getByText('Intake Agent')).toBeInTheDocument()
    expect(screen.getByText('Research Agent')).toBeInTheDocument()
    expect(screen.getByText('Reporting Agent')).toBeInTheDocument()
  })

  describe('loading state elapsed counter', () => {
    beforeEach(() => vi.useFakeTimers())
    afterEach(() => vi.useRealTimers())

    it('counts elapsed seconds while the crew runs', () => {
      render(<ResultsPanel state={{ status: 'loading' }} />)

      expect(screen.getByText('0s elapsed')).toBeInTheDocument()
      act(() => {
        vi.advanceTimersByTime(3000)
      })
      expect(screen.getByText('3s elapsed')).toBeInTheDocument()
    })
  })

  it('shows the error message and no retry action when onRetry is omitted', () => {
    render(<ResultsPanel state={{ status: 'error', message: 'boom' }} />)

    expect(screen.getByText('Run failed')).toBeInTheDocument()
    expect(screen.getByText('boom')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /try again/i })).not.toBeInTheDocument()
  })

  it('calls onRetry when Try again is clicked', async () => {
    const onRetry = vi.fn()
    const user = userEvent.setup()

    render(<ResultsPanel state={{ status: 'error', message: 'boom' }} onRetry={onRetry} />)
    await user.click(screen.getByRole('button', { name: /try again/i }))

    expect(onRetry).toHaveBeenCalledOnce()
  })

  it('renders the decision log, research sources, and checklist on success', () => {
    const state: ResultsState = { status: 'success', result: successResult }

    render(<ResultsPanel state={state} />)

    expect(screen.getByText('stub-decision-log')).toBeInTheDocument()
    expect(screen.getByText('stub-research-sources')).toBeInTheDocument()
    expect(screen.getByText('stub-checklist-view')).toBeInTheDocument()
  })
})
