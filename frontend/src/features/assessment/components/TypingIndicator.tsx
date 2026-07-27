import { motion } from 'framer-motion'

export function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="flex w-full mb-4 justify-start"
    >
      <div className="mr-2 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs shadow-sm">
        HT
      </div>
      <div className="flex max-w-[85%] items-center gap-1.5 rounded-2xl rounded-tl-sm bg-muted/60 px-4 py-4 border border-border/50 shadow-sm">
        <motion.div
          className="h-2 w-2 rounded-full bg-muted-foreground/60"
          animate={{ y: [0, -5, 0] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
        />
        <motion.div
          className="h-2 w-2 rounded-full bg-muted-foreground/60"
          animate={{ y: [0, -5, 0] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
        />
        <motion.div
          className="h-2 w-2 rounded-full bg-muted-foreground/60"
          animate={{ y: [0, -5, 0] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
        />
      </div>
    </motion.div>
  )
}
