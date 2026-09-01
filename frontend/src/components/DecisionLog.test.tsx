import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { DecisionLog } from './DecisionLog'
import type { Decision } from '../api/types'

const remoteEngineeringDecision: Decision = {
  location_track: 'remote',
  location_steps: ['Ship a laptop home.', 'Install the VPN client.'],
  dept_track: 'engineering',
  dept_steps: ['Accept the GitHub org invite.'],
  explanation: [
    "Location='remote' matched track 'remote' -> added 2 IT/equipment step(s).",
    "Department='Engineering' matched track 'engineering' -> added 1 tool-access step(s).",
  ],
}

describe('DecisionLog', () => {
  it('renders both tracks with their matched labels', () => {
    render(<DecisionLog decision={remoteEngineeringDecision} />)

    expect(screen.getByText('Remote')).toBeInTheDocument()
    expect(screen.getByText('Engineering')).toBeInTheDocument()
  })

  it('renders every step for both tracks', () => {
    render(<DecisionLog decision={remoteEngineeringDecision} />)

    expect(screen.getByText('Ship a laptop home.')).toBeInTheDocument()
    expect(screen.getByText('Install the VPN client.')).toBeInTheDocument()
    expect(screen.getByText('Accept the GitHub org invite.')).toBeInTheDocument()
  })

  it('renders the raw decision trace explanation lines', () => {
    render(<DecisionLog decision={remoteEngineeringDecision} />)

    expect(screen.getByText(/Location='remote' matched track 'remote'/)).toBeInTheDocument()
    expect(
      screen.getByText(/Department='Engineering' matched track 'engineering'/),
    ).toBeInTheDocument()
  })

  it('renders different content for an in-office sales decision', () => {
    const salesDecision: Decision = {
      location_track: 'in_office',
      location_steps: ['Pick up your badge at the front desk.'],
      dept_track: 'sales',
      dept_steps: ['Get provisioned in the CRM.'],
      explanation: [
        "Location='in_office' matched track 'in_office' -> added 1 IT/equipment step(s).",
        "Department='Sales' matched track 'sales' -> added 1 tool-access step(s).",
      ],
    }

    render(<DecisionLog decision={salesDecision} />)

    expect(screen.getByText('In-office')).toBeInTheDocument()
    expect(screen.getByText('Sales')).toBeInTheDocument()
    expect(screen.getByText('Get provisioned in the CRM.')).toBeInTheDocument()
  })
})
