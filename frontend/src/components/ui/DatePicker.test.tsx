import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { DatePicker } from './DatePicker'

vi.mock('react-day-picker', () => ({
  // A minimal stand-in for the real calendar grid: exposes one button that
  // invokes onSelect with a fixed date, so these tests cover DatePicker's
  // own ISO conversion and popover behavior without depending on the real
  // library's DOM structure.
  DayPicker: ({ onSelect }: { onSelect?: (date: Date) => void }) => (
    <button type="button" onClick={() => onSelect?.(new Date(2026, 9, 1))}>
      Pick Oct 1, 2026
    </button>
  ),
}))

describe('DatePicker', () => {
  it('shows the placeholder when no value is set', () => {
    render(<DatePicker value="" onChange={vi.fn()} />)

    expect(screen.getByText('Select a date')).toBeInTheDocument()
  })

  it('displays a formatted date when a value is set', () => {
    render(<DatePicker value="2026-10-01" onChange={vi.fn()} />)

    expect(screen.getByText('Oct 1, 2026')).toBeInTheDocument()
  })

  it('opens the calendar on click and reports the selected date as ISO', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()

    render(<DatePicker value="" onChange={onChange} />)

    await user.click(screen.getByRole('button', { name: /select a date/i }))
    await user.click(screen.getByRole('button', { name: /pick oct 1, 2026/i }))

    expect(onChange).toHaveBeenCalledWith('2026-10-01')
  })

  it('closes the calendar after a date is selected', async () => {
    const user = userEvent.setup()

    render(<DatePicker value="" onChange={vi.fn()} />)

    await user.click(screen.getByRole('button', { name: /select a date/i }))
    await user.click(screen.getByRole('button', { name: /pick oct 1, 2026/i }))

    expect(screen.queryByRole('button', { name: /pick oct 1, 2026/i })).not.toBeInTheDocument()
  })
})
