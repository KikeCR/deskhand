import { Hand } from '@phosphor-icons/react'
import { cn } from '../lib/cn'

interface LogoProps {
  className?: string
}

export function Logo({ className }: LogoProps) {
  return (
    <span
      className={cn(
        'flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground',
        className,
      )}
    >
      <Hand size={18} weight="fill" />
    </span>
  )
}
