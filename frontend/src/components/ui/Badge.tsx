import type { HTMLAttributes } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../lib/cn'

const badgeVariants = cva(
  'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 font-mono text-xs font-medium',
  {
    variants: {
      variant: {
        location: 'bg-track-location/15 text-track-location',
        department: 'bg-track-department/15 text-track-department',
        muted: 'bg-muted text-muted-foreground',
        success: 'bg-success/15 text-success',
      },
    },
    defaultVariants: {
      variant: 'muted',
    },
  },
)

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />
}
