import React from 'react'
import { cn } from '@/lib/utils'
import { type UrgencyLevel, URGENCY_STYLES } from '@/types'

interface UrgencyBadgeProps {
  level: UrgencyLevel
  className?: string
  pulse?: boolean
}

const URGENCY_LABELS: Record<string, React.ReactNode | string> = {
  EMERGENCY: 'Emergency',
  HIGH: 'High',
  MEDIUM: 'Medium',
  LOW: 'Low',
  RED: 'Emergency',
  ORANGE: 'Urgent',
  YELLOW: 'Elevated',
  GREEN: 'Routine',
}

export function UrgencyBadge({ level, className, pulse = false }: UrgencyBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wider',
        URGENCY_STYLES[level].badge,
        className
      )}
    >
      {pulse && (
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-white opacity-75" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-white" />
        </span>
      )}
      {URGENCY_LABELS[level]}
    </span>
  )
}
