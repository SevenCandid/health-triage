import { motion, AnimatePresence } from 'framer-motion'
import { useNetworkStore } from '@/stores/network-store'
import { useOnlineStatus } from '@/hooks/use-online-status'

export function OfflineBanner() {
  // Register the listener — safe to call multiple times
  const isOnline = useOnlineStatus()
  const hasPendingSync = useNetworkStore((s) => s.hasPendingSync)

  return (
    <AnimatePresence>
      {!isOnline && (
        <motion.div
          key="offline-banner"
          initial={{ y: -48, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -48, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 260, damping: 20 }}
          role="status"
          aria-live="polite"
          className="flex items-center justify-center gap-2 bg-urgency-elevated px-4 py-2 text-sm font-medium text-white"
        >
          <span className="h-2 w-2 animate-pulse rounded-full bg-white" />
          You are offline
          {hasPendingSync && ' · Assessments will sync when reconnected'}
        </motion.div>
      )}
    </AnimatePresence>
  )
}
