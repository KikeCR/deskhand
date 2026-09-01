import ReactMarkdown from 'react-markdown'
import { cn } from '../lib/cn'

interface MarkdownContentProps {
  content: string
  className?: string
}

export function MarkdownContent({ content, className }: MarkdownContentProps) {
  return (
    <div className={cn('flex flex-col gap-3 text-sm leading-relaxed', className)}>
      <ReactMarkdown
        components={{
          h1: ({ children }) => <h1 className="text-lg font-semibold tracking-tight">{children}</h1>,
          h2: ({ children }) => (
            <h2 className="mt-2 text-sm font-semibold tracking-tight text-foreground">{children}</h2>
          ),
          h3: ({ children }) => <h3 className="text-sm font-semibold">{children}</h3>,
          p: ({ children }) => <p className="text-foreground">{children}</p>,
          ul: ({ children }) => <ul className="flex flex-col gap-1.5 pl-1">{children}</ul>,
          li: ({ children }) => (
            <li className="flex gap-2">
              <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-muted-foreground" />
              <span>{children}</span>
            </li>
          ),
          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
          code: ({ children }) => (
            <code className="rounded bg-muted px-1 py-0.5 font-mono text-xs">{children}</code>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
