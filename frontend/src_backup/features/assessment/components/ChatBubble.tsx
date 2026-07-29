import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface ChatBubbleProps {
  role: 'USER' | 'SYSTEM'
  message: string
  animate?: boolean
}

export function ChatBubble({ role, message, animate = true }: ChatBubbleProps) {
  const isUser = role === 'USER'

  return (
    <motion.div
      initial={animate ? { opacity: 0, y: 5, scale: 0.98 } : false}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: 'spring', stiffness: 260, damping: 24, mass: 0.8 }}
      className={cn('flex w-full mb-3 gap-3', isUser ? 'justify-end' : 'justify-start items-start')}
    >
      {!isUser && (
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-cyan-400 text-white text-[10px] font-bold shadow-sm mt-0.5">
          TA
        </div>
      )}

      <div
        className={cn(
          'max-w-[78%] rounded-2xl px-4 py-3 text-sm leading-relaxed',
          isUser
            ? 'rounded-br-sm bg-primary text-primary-foreground shadow-md'
            : 'rounded-bl-sm bg-muted text-foreground'
        )}
      >
        {message}
      </div>
    </motion.div>
  )
}
