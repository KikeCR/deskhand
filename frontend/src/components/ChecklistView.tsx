import { ListChecks } from '@phosphor-icons/react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { MarkdownContent } from './MarkdownContent'

interface ChecklistViewProps {
  checklistMarkdown: string
  outputPath: string
}

export function ChecklistView({ checklistMarkdown, outputPath }: ChecklistViewProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-1.5">
          <ListChecks size={16} weight="regular" />
          Onboarding checklist
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          The Reporting Agent's final artifact, written to{' '}
          <code className="font-mono text-xs text-foreground">{outputPath}</code>.
        </p>
      </CardHeader>
      <CardContent>
        <MarkdownContent content={checklistMarkdown} />
      </CardContent>
    </Card>
  )
}
