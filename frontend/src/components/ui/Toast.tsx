import { Check } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'

interface ToastProps {
  id?: string
  type?: 'success' | 'error' | 'warning' | 'info'
  message: string
  onDismiss?: () => void
  className?: string
}

const typeConfig = {
  success: { bg: 'bg-urgency-routine', icon: <Check className="w-4 h-4" /> },
  error:   { bg: 'bg-urgency-emergency', icon: '✕' },
  warning: { bg: 'bg-urgency-elevated', icon: '!' },
  info:    { bg: 'bg-primary', icon: 'ℹ' },
}

export function Toast({ type = 'info', message, onDismiss, className }: ToastProps) {
  const { bg, icon } = typeConfig[type]

  return (
    <motion.div
      initial={{ opacity: 0, x: 80 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 80 }}
      className={cn(
        'flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-white shadow-lg',
        bg,
        className
      )}
      role="alert"
      aria-live="polite"
    >
      <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-white/20 text-xs font-bold">
        {icon}
      </span>
      <span className="flex-1">{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="shrink-0 rounded p-0.5 hover:bg-white/20 transition"
          aria-label="Dismiss"
        >
          ✕
        </button>
      )}
    </motion.div>
  )
}

// ── Toast Container ───────────────────────────────────────────────────────────

interface ToastContainerProps {
  toasts: Array<{ id: string; type?: ToastProps['type']; message: string }>
  onDismiss: (id: string) => void
}

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  return (
    <div
      id="toast-container"
      className="fixed bottom-4 right-4 z-50 flex flex-col gap-2"
      aria-label="Notifications"
    >
      <AnimatePresence>
        {toasts.map((t) => (
          <Toast
            key={t.id}
            type={t.type}
            message={t.message}
            onDismiss={() => onDismiss(t.id)}
          />
        ))}
      </AnimatePresence>
    </div>
  )
}
