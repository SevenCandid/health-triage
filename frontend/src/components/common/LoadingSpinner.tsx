import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  label?: string
  fullScreen?: boolean
}

const sizeMap = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-4',
}

export function LoadingSpinner({
  size = 'md',
  className,
  label = 'Loading...',
  fullScreen = false,
}: LoadingSpinnerProps) {
  const spinner = (
    <div className={cn('flex flex-col items-center justify-center gap-4', className)}>
      <motion.div
        animate={{ scale: [0.9, 1.1, 0.9], opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        className={cn(
          'rounded-full bg-primary/20 flex items-center justify-center',
          sizeMap[size].replace('border-2', '').replace('border-4', '')
        )}
        role="status"
        aria-label={label}
      >
        <div className="w-1/2 h-1/2 rounded-full bg-primary/80" />
      </motion.div>
      {label && (
        <p className="text-sm font-medium text-muted-foreground animate-pulse">{label}</p>
      )}
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/60 backdrop-blur-md">
        {spinner}
      </div>
    )
  }

  return spinner
}

/** Suspense-compatible page-level loading fallback */
export function PageLoader() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <LoadingSpinner size="lg" label="Loading page..." />
    </div>
  )
}
