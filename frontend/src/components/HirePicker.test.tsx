import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { HirePicker } from './HirePicker'
import * as apiClient from '../api/client'
import type { HireProfile } from '../api/types'
import type { BackendStatus } from '../hooks/useBackendStatus'

vi.mock('./ui/DatePicker', () => ({
  // HirePicker's own tests care about form orchestration, not calendar
  // internals (that's DatePicker.test.tsx's job), so stand in with a plain
  // labeled input that reports whatever string is typed as the ISO value.
  DatePicker: ({ value, onChange }: { value: string; onChange: (v: string) => void }) => (
    <input aria-label="Start date" value={value} onChange={(e) => onChange(e.target.value)} />
  ),
}))

const sampleHires: HireProfile[] = [
  {
    name: 'Priya Nakamura',
    role: 'Software Engineer II',
    department: 'Engineering',
    location: 'remote',
    start_date: '2026-09-15',
  },
  {
    name: 'Marcus Delgado',
    role: 'Account Executive',
    department: 'Sales',
    location: 'in_office',
    start_date: '2026-09-08',
  },
]

function renderHirePicker(overrides: {
  onRun?: (hire: HireProfile) => void
  isRunning?: boolean
  backendStatus?: BackendStatus
  onRetryBackend?: () => void
} = {}) {
  return render(
    <HirePicker
      onRun={overrides.onRun ?? vi.fn()}
      isRunning={overrides.isRunning ?? false}
      backendStatus={overrides.backendStatus ?? 'online'}
      onRetryBackend={overrides.onRetryBackend ?? vi.fn()}
    />,
  )
}

describe('HirePicker', () => {
  it('lists the bundled sample hires and runs the selected one', async () => {
    vi.spyOn(apiClient, 'fetchSampleHires').mockResolvedValue(sampleHires)
    const onRun = vi.fn()
    const user = userEvent.setup()

    renderHirePicker({ onRun })

    await screen.findByText('Priya Nakamura')
    await user.click(screen.getByText('Marcus Delgado'))
    await user.click(screen.getByRole('button', { name: /run onboarding/i }))

    expect(onRun).toHaveBeenCalledWith(sampleHires[1])
  })

  it('disables the run button for an incomplete custom hire', async () => {
    vi.spyOn(apiClient, 'fetchSampleHires').mockResolvedValue(sampleHires)
    const user = userEvent.setup()

    renderHirePicker()

    await screen.findByText('Priya Nakamura')
    await user.click(screen.getByText('Custom hire'))

    expect(screen.getByRole('button', { name: /run onboarding/i })).toBeDisabled()
  })

  it('enables the run button once a custom hire is fully filled in', async () => {
    vi.spyOn(apiClient, 'fetchSampleHires').mockResolvedValue(sampleHires)
    const onRun = vi.fn()
    const user = userEvent.setup()

    renderHirePicker({ onRun })

    await screen.findByText('Priya Nakamura')
    await user.click(screen.getByText('Custom hire'))

    await user.type(screen.getByPlaceholderText('Jordan Reyes'), 'Alex Kim')
    await user.type(screen.getByPlaceholderText('Support Engineer'), 'Data Analyst')
    await user.type(screen.getByPlaceholderText('Engineering'), 'Data')
    await user.type(screen.getByLabelText('Start date'), '2026-10-01')

    const runButton = screen.getByRole('button', { name: /run onboarding/i })
    await waitFor(() => expect(runButton).toBeEnabled())

    await user.click(runButton)
    expect(onRun).toHaveBeenCalledWith({
      name: 'Alex Kim',
      role: 'Data Analyst',
      department: 'Data',
      location: 'remote',
      start_date: '2026-10-01',
    })
  })

  it('keeps the run button disabled for a malformed start date', async () => {
    vi.spyOn(apiClient, 'fetchSampleHires').mockResolvedValue(sampleHires)
    const user = userEvent.setup()

    renderHirePicker()

    await screen.findByText('Priya Nakamura')
    await user.click(screen.getByText('Custom hire'))

    await user.type(screen.getByPlaceholderText('Jordan Reyes'), 'Alex Kim')
    await user.type(screen.getByPlaceholderText('Support Engineer'), 'Data Analyst')
    await user.type(screen.getByPlaceholderText('Engineering'), 'Data')
    await user.type(screen.getByLabelText('Start date'), 'not a date')

    expect(screen.getByRole('button', { name: /run onboarding/i })).toBeDisabled()
  })

  it('shows an error message when sample hires fail to load', async () => {
    vi.spyOn(apiClient, 'fetchSampleHires').mockRejectedValue(new Error('network error'))

    renderHirePicker()

    expect(await screen.findByText(/could not load sample hires/i)).toBeInTheDocument()
  })

  it('retries loading sample hires when Retry is clicked', async () => {
    const fetchSpy = vi.spyOn(apiClient, 'fetchSampleHires')
    fetchSpy.mockRejectedValueOnce(new Error('network error'))
    fetchSpy.mockResolvedValueOnce(sampleHires)
    const user = userEvent.setup()

    renderHirePicker()

    await screen.findByText(/could not load sample hires/i)
    await user.click(screen.getByRole('button', { name: /retry/i }))

    await screen.findByText('Priya Nakamura')
    expect(screen.queryByText(/could not load sample hires/i)).not.toBeInTheDocument()
  })

  it('disables the run button while the backend status is checking', async () => {
    vi.spyOn(apiClient, 'fetchSampleHires').mockResolvedValue(sampleHires)

    renderHirePicker({ backendStatus: 'checking' })

    await screen.findByText('Priya Nakamura')
    expect(screen.getByRole('button', { name: /waiting for backend/i })).toBeDisabled()
  })

  it('disables the run button and offers a retry when the backend is offline', async () => {
    vi.spyOn(apiClient, 'fetchSampleHires').mockResolvedValue(sampleHires)
    const onRetryBackend = vi.fn()
    const user = userEvent.setup()

    renderHirePicker({ backendStatus: 'offline', onRetryBackend })

    await screen.findByText('Priya Nakamura')
    expect(screen.getByRole('button', { name: /waiting for backend/i })).toBeDisabled()
    expect(screen.getByText(/backend unreachable/i)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /^retry$/i }))
    expect(onRetryBackend).toHaveBeenCalledOnce()
  })

  it('keeps the run button disabled even for a fully valid hire when the backend is offline', async () => {
    vi.spyOn(apiClient, 'fetchSampleHires').mockResolvedValue(sampleHires)
    const user = userEvent.setup()

    renderHirePicker({ backendStatus: 'offline' })

    await screen.findByText('Priya Nakamura')
    await user.click(screen.getByText('Priya Nakamura'))

    expect(screen.getByRole('button', { name: /waiting for backend/i })).toBeDisabled()
  })
})
