import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

export type VoiceState = 'IDLE' | 'LISTENING' | 'PROCESSING' | 'SPEAKING'

interface VoiceWaveProps {
  state: VoiceState
}

export function VoiceWave({ state }: VoiceWaveProps) {
  // Determine color and animation properties based on state
  let ringColors = ''
  let centerColor = ''
  let isAnimating = false

  switch (state) {
    case 'LISTENING':
      ringColors = 'border-green-500/50'
      centerColor = 'bg-green-500'
      isAnimating = true
      break
    case 'PROCESSING':
      ringColors = 'border-yellow-500/50'
      centerColor = 'bg-yellow-500'
      isAnimating = true
      break
    case 'SPEAKING':
      ringColors = 'border-purple-500/50'
      centerColor = 'bg-purple-500'
      isAnimating = true
      break
    case 'IDLE':
    default:
      ringColors = 'border-gray-500/20'
      centerColor = 'bg-gray-500'
      isAnimating = false
      break
  }

  return (
    <div className="relative flex h-40 w-40 sm:h-64 sm:w-64 items-center justify-center">
      {/* Outer Pulse Rings */}
      <motion.div
        className={cn('absolute inset-0 rounded-full border-[3px] sm:border-4', ringColors)}
        animate={
          isAnimating
            ? { scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }
            : { scale: 1, opacity: 0.2 }
        }
        transition={{
          duration: state === 'PROCESSING' ? 1 : 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      <motion.div
        className={cn('absolute inset-2 sm:inset-4 rounded-full border-[3px] sm:border-4', ringColors)}
        animate={
          isAnimating
            ? { scale: [1, 1.3, 1], opacity: [0.7, 0, 0.7] }
            : { scale: 1, opacity: 0.4 }
        }
        transition={{
          duration: state === 'PROCESSING' ? 1 : 2,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 0.2,
        }}
      />

      {/* Center Core */}
      <motion.div
        className={cn('h-16 w-16 sm:h-24 sm:w-24 rounded-full shadow-xl shadow-current', centerColor)}
        animate={
          isAnimating
            ? { scale: state === 'SPEAKING' ? [1, 1.1, 1] : 1 }
            : { scale: 1 }
        }
        transition={{
          duration: 0.5,
          repeat: Infinity,
          repeatType: 'reverse',
          ease: 'easeInOut',
        }}
      />
    </div>
  )
}
