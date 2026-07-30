import { HeartPulse } from 'lucide-react'
import { usePWAInstall } from '@/hooks/use-pwa-install'
import { Button } from '@/components/ui/Button'
import { motion, AnimatePresence } from 'framer-motion'

export function InstallNotice() {
  const { isInstallable, promptInstall } = usePWAInstall()

  return (
    <AnimatePresence>
      {isInstallable && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="bg-primary/10 border-b border-primary/20 overflow-hidden"
        >
          <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6 lg:px-8 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="text-xl"><HeartPulse className="w-4 h-4" /></span>
              <div>
                <p className="text-sm font-semibold text-primary">Install FirstAid+</p>
                <p className="text-xs text-muted-foreground hidden sm:block">
                  Add to your home screen for quick offline access and a better experience.
                </p>
              </div>
            </div>
            <Button 
              size="sm" 
              onClick={promptInstall}
              className="whitespace-nowrap shadow-sm text-xs h-8"
            >
              Install Now
            </Button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
