import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '../lib/cn'

interface MarkdownContentProps {
  content: string
  className?: string
}

export function MarkdownContent({ content, className }: MarkdownContentProps) {
  return (
    <div className={cn('flex flex-col gap-3 text-sm leading-relaxed', className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => <h1 className="text-lg font-semibold tracking-tight">{children}</h1>,
          h2: ({ children }) => (
            <h2 className="mt-2 text-sm font-semibold tracking-tight text-foreground">{children}</h2>
          ),
          h3: ({ children }) => <h3 className="text-sm font-semibold">{children}</h3>,
          h4: ({ children }) => <h4 className="text-sm font-semibold">{children}</h4>,
          p: ({ children }) => <p className="text-foreground">{children}</p>,
          ul: ({ children }) => <ul className="flex flex-col gap-1.5 pl-1">{children}</ul>,
          ol: ({ children }) => (
            <ol className="flex flex-col gap-1.5 pl-1 list-decimal marker:text-muted-foreground">
              {children}
            </ol>
          ),
          li: ({ children, className: liClassName }) => {
            // GFM task-list items get react-markdown's own "task-list-item"
            // class and render their own <input type="checkbox">; only
            // decorate plain list items with our bullet dot, otherwise
            // every checklist row grows a redundant dot next to its box.
            const isTaskItem = liClassName?.includes('task-list-item')
            if (isTaskItem) {
              return <li className={cn('flex items-start gap-2', liClassName)}>{children}</li>
            }
            return (
              <li className="flex gap-2">
                <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-muted-foreground" />
                <span>{children}</span>
              </li>
            )
          },
          input: ({ checked }) => (
            <input
              type="checkbox"
              checked={checked ?? false}
              disabled
              readOnly
              className="mt-1 h-3.5 w-3.5 shrink-0 accent-primary"
            />
          ),
          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
          code: ({ children }) => (
            <code className="rounded bg-muted px-1 py-0.5 font-mono text-xs">{children}</code>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-left text-sm">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="border-b border-border px-2 py-1.5 font-semibold">{children}</th>
          ),
          td: ({ children }) => <td className="border-b border-border px-2 py-1.5">{children}</td>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
