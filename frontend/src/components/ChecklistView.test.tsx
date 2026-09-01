import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { ChecklistView } from './ChecklistView'

describe('ChecklistView', () => {
  it('renders markdown headings and list items', () => {
    const markdown = [
      '# Week 1 Onboarding Checklist',
      '',
      '## IT & Equipment',
      '',
      '- Ship a laptop home.',
      '- Install the VPN client.',
    ].join('\n')

    render(<ChecklistView checklistMarkdown={markdown} outputPath="/tmp/out.md" />)

    expect(screen.getByRole('heading', { name: 'Week 1 Onboarding Checklist' })).toBeInTheDocument()
    expect(screen.getByText('IT & Equipment')).toBeInTheDocument()
    expect(screen.getByText('Ship a laptop home.')).toBeInTheDocument()
  })

  it('shows the output path the checklist was written to', () => {
    render(<ChecklistView checklistMarkdown="# Checklist" outputPath="/tmp/priya_onboarding_checklist.md" />)

    expect(screen.getByText('/tmp/priya_onboarding_checklist.md')).toBeInTheDocument()
  })
})
