import { MagnifyingGlass } from '@phosphor-icons/react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { MarkdownContent } from './MarkdownContent'

interface ResearchSourcesProps {
  researchNotes: string
}

export function ResearchSources({ researchNotes }: ResearchSourcesProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-1.5">
          <MagnifyingGlass size={16} weight="regular" />
          Research sources
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Grounded excerpts the Research Agent pulled from the company docs via the RAG tool,
          each cited to its source document.
        </p>
      </CardHeader>
      <CardContent>
        <MarkdownContent content={researchNotes} />
      </CardContent>
    </Card>
  )
}
