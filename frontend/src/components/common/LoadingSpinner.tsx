import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  label?: string
  fullScreen?: boolean
}

const sizeMap = {
  sm: 'w-8 h-4',
  md: 'w-16 h-8',
  lg: 'w-24 h-12',
}

export function LoadingSpinner({
  size = 'md',
  className,
  label = 'Loading...',
  fullScreen = false,
}: LoadingSpinnerProps) {
  const spinner = (
    <div className={cn('flex flex-col items-center justify-center gap-4', className)}>
      <div
        className={cn('relative flex items-center justify-center', sizeMap[size])}
        role="status"
        aria-label={label}
      >
        <svg
          viewBox="0 0 100 50"
          className="absolute inset-0 w-full h-full text-primary drop-shadow-[0_0_8px_rgba(var(--primary),0.8)]"
          preserveAspectRatio="none"
        >
          {/* Faded background path */}
          <path
            d="M 0 25 L 25 25 L 35 10 L 45 40 L 55 5 L 65 40 L 75 25 L 100 25"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="opacity-20"
          />
          {/* Animated tracing path */}
          <motion.path
            d="M 0 25 L 25 25 L 35 10 L 45 40 L 55 5 L 65 40 L 75 25 L 100 25"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0, pathOffset: 1 }}
            animate={{ pathLength: 1, pathOffset: 0 }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        </svg>
      </div>
      {label && (
        <p className="text-sm font-medium text-muted-foreground animate-pulse tracking-wide">
          {label}
        </p>
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
      <LoadingSpinner size="lg" label="Preparing assessment..." />
    </div>
  )
}
