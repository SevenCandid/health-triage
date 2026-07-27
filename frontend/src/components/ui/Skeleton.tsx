import { type HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'rect' | 'circle'
  lines?: number
}

export function Skeleton({ variant = 'rect', lines = 1, className, ...props }: SkeletonProps) {
  if (variant === 'text' && lines > 1) {
    return (
      <div className="flex flex-col gap-2" {...props}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={cn(
              'animate-pulse rounded bg-muted',
              i === lines - 1 ? 'w-3/4' : 'w-full',
              'h-4',
              className
            )}
          />
        ))}
      </div>
    )
  }

  return (
    <div
      className={cn(
        'animate-pulse bg-muted',
        variant === 'circle' ? 'rounded-full' : 'rounded-lg',
        variant === 'text' && 'h-4 w-full rounded',
        className
      )}
      {...props}
    />
  )
}

// Pre-composed skeletons for common usage patterns
export function CardSkeleton() {
  return (
    <div className="rounded-xl border border-border p-6 space-y-4">
      <Skeleton variant="text" className="h-5 w-1/2" />
      <Skeleton variant="text" lines={3} />
      <Skeleton className="h-10 w-28" />
    </div>
  )
}
