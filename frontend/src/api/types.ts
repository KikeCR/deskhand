export interface HireProfile {
  name: string
  role: string
  department: string
  location: string
  start_date: string
}

export interface Decision {
  location_track: string
  location_steps: string[]
  dept_track: string
  dept_steps: string[]
  explanation: string[]
}

export interface OnboardingResponse {
  hire: HireProfile
  decision: Decision
  research_notes: string
  checklist_markdown: string
  output_path: string
}
