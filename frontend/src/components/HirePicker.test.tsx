import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { HirePicker } from './HirePicker'
import * as apiClient from '../api/client'
import type { HireProfile } from '../api/types'

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

describe('HirePicker', () => {
  it('lists the bundled sample hires and runs the selected one', async () => {
    vi.spyOn(apiClient, 'fetchSampleHires').mockResolvedValue(sampleHires)
    const onRun = vi.fn()
    const user = userEvent.setup()

    render(<HirePicker onRun={onRun} isRunning={false} />)

    await screen.findByText('Priya Nakamura')
    await user.click(screen.getByText('Marcus Delgado'))
    await user.click(screen.getByRole('button', { name: /run onboarding/i }))

    expect(onRun).toHaveBeenCalledWith(sampleHires[1])
  })

  it('disables the run button for an incomplete custom hire', async () => {
    vi.spyOn(apiClient, 'fetchSampleHires').mockResolvedValue(sampleHires)
    const user = userEvent.setup()

    render(<HirePicker onRun={vi.fn()} isRunning={false} />)

    await screen.findByText('Priya Nakamura')
    await user.click(screen.getByText('Custom hire'))

    expect(screen.getByRole('button', { name: /run onboarding/i })).toBeDisabled()
  })

  it('enables the run button once a custom hire is fully filled in', async () => {
    vi.spyOn(apiClient, 'fetchSampleHires').mockResolvedValue(sampleHires)
    const onRun = vi.fn()
    const user = userEvent.setup()

    render(<HirePicker onRun={onRun} isRunning={false} />)

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

  it('shows an error message when sample hires fail to load', async () => {
    vi.spyOn(apiClient, 'fetchSampleHires').mockRejectedValue(new Error('network error'))

    render(<HirePicker onRun={vi.fn()} isRunning={false} />)

    expect(await screen.findByText(/could not load sample hires/i)).toBeInTheDocument()
  })
})
