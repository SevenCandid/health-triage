import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

import { type UrgencyLevel } from '@/types'

interface AssessmentSession {
  sessionId: string | null
  currentSymptoms: string[]
  currentQuestion: {
    id: string
    node_id: string
    question_text_en: string
    question_text_tw?: string
    question_type: string
    options?: { id: string; option_value: string; label_en: string; label_tw?: string }[]
  } | null
  answers: Record<string, string>
  result: {
    severity: UrgencyLevel
    recommendations: string[]
    explanation: string
    is_emergency: boolean
  } | null
  isComplete: boolean
  startedAt: Date | null
}

interface AssessmentState extends AssessmentSession {
  startSession: (sessionId: string) => void
  setSymptoms: (symptoms: string[]) => void
  setCurrentQuestion: (question: AssessmentSession['currentQuestion']) => void
  addAnswer: (questionId: string, answer: string) => void
  setResult: (result: AssessmentSession['result']) => void
  completeSession: () => void
  resetSession: () => void
}

const initialSession: AssessmentSession = {
  sessionId: null,
  currentSymptoms: [],
  currentQuestion: null,
  answers: {},
  result: null,
  isComplete: false,
  startedAt: null,
}

export const useAssessmentStore = create<AssessmentState>()(
  persist(
    (set) => ({
      ...initialSession,

      startSession: (sessionId) =>
        set({ sessionId, startedAt: new Date(), isComplete: false, answers: {}, result: null }),

      setSymptoms: (symptoms) => set({ currentSymptoms: symptoms }),

      setCurrentQuestion: (question) => set({ currentQuestion: question }),

      addAnswer: (questionId, answer) =>
        set((state) => ({
          answers: { ...state.answers, [questionId]: answer },
        })),

      setResult: (result) => set({ result }),

      completeSession: () => set({ isComplete: true, currentQuestion: null }),

      resetSession: () => set(initialSession),
    }),
    {
      name: 'health-triage-assessment',
      storage: createJSONStorage(() => sessionStorage),
    }
  )
)
