import { useState } from 'react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import type { FollowUpQuestion } from '@/types'

interface QuestionCardProps {
  question: FollowUpQuestion
  onSubmit: (answer: string | string[]) => void
  isSubmitting?: boolean
}

export function QuestionCard({ question, onSubmit, isSubmitting }: QuestionCardProps) {
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [textValue, setTextValue] = useState('')

  const handleSingleSelect = (id: string) => {
    setSelectedIds([id])
    onSubmit(id)
  }

  const handleMultiSelectToggle = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    )
  }

  const handleMultiSubmit = () => {
    if (selectedIds.length > 0) onSubmit(selectedIds)
  }

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (textValue.trim()) onSubmit(textValue.trim())
  }

  const renderInputs = () => {
    switch (question.question_type) {
      case 'BOOLEAN':
        return (
          <div className="flex gap-2">
            <button
              onClick={() => handleSingleSelect('yes')}
              disabled={isSubmitting}
              className="flex-1 rounded-xl border border-green-500/30 bg-green-500/5 py-3 text-sm font-semibold text-green-600 transition-colors hover:bg-green-500/15 dark:text-green-400"
            >
              ✓ Yes
            </button>
            <button
              onClick={() => handleSingleSelect('no')}
              disabled={isSubmitting}
              className="flex-1 rounded-xl border border-red-500/30 bg-red-500/5 py-3 text-sm font-semibold text-red-600 transition-colors hover:bg-red-500/15 dark:text-red-400"
            >
              ✕ No
            </button>
          </div>
        )

      case 'SINGLE_CHOICE':
      case 'SINGLE_SELECT':
        return (
          <div className="flex flex-col gap-2">
            {question.options?.map((opt) => (
              <button
                key={opt.id || opt.option_value}
                onClick={() => handleSingleSelect(opt.option_value)}
                disabled={isSubmitting}
                className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-left text-sm font-medium transition-all ${
                  selectedIds.includes(opt.option_value)
                    ? 'border-primary bg-primary/10 text-primary'
                    : 'border-border bg-background hover:border-primary/40 hover:bg-primary/5 text-foreground'
                }`}
              >
                <span className="h-4 w-4 shrink-0 rounded-full border-2 flex items-center justify-center border-current">
                  {selectedIds.includes(opt.option_value) && (
                    <span className="h-2 w-2 rounded-full bg-current" />
                  )}
                </span>
                {opt.label_en}
              </button>
            ))}
          </div>
        )

      case 'MULTI_SELECT':
      case 'MULTIPLE_CHOICE':
        return (
          <div className="flex flex-col gap-3">
            <div className="flex flex-col gap-2">
              {question.options?.map((opt) => {
                const isSelected = selectedIds.includes(opt.option_value)
                return (
                  <button
                    key={opt.id || opt.option_value}
                    onClick={() => handleMultiSelectToggle(opt.option_value)}
                    disabled={isSubmitting}
                    className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-left text-sm font-medium transition-all ${
                      isSelected
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-border bg-background hover:border-primary/40 hover:bg-primary/5 text-foreground'
                    }`}
                  >
                    <span className={`h-4 w-4 shrink-0 rounded border-2 flex items-center justify-center text-xs ${isSelected ? 'bg-primary border-primary text-primary-foreground' : 'border-current'}`}>
                      {isSelected && '✓'}
                    </span>
                    {opt.label_en}
                  </button>
                )
              })}
            </div>
            <Button
              onClick={handleMultiSubmit}
              disabled={selectedIds.length === 0 || isSubmitting}
              className="w-full rounded-xl"
            >
              Confirm Selection ({selectedIds.length})
            </Button>
          </div>
        )

      case 'TEXT':
      default:
        return (
          <form onSubmit={handleTextSubmit} className="flex gap-2">
            <Input
              value={textValue}
              onChange={(e) => setTextValue(e.target.value)}
              placeholder="Type your answer..."
              disabled={isSubmitting}
              className="flex-1 rounded-xl"
              autoFocus
            />
            <Button type="submit" disabled={!textValue.trim() || isSubmitting} className="rounded-xl">
              Send
            </Button>
          </form>
        )
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="w-full"
    >
      {renderInputs()}
    </motion.div>
  )
}
