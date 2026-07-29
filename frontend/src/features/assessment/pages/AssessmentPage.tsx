import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { assessmentApi } from '@/services/api'
import { useAssessmentStore } from '@/stores/assessment-store'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { ChatBubble } from '../components/ChatBubble'
import { TypingIndicator } from '../components/TypingIndicator'
import { QuestionCard } from '../components/QuestionCard'
import { AssessmentNotice } from '../components/AssessmentNotice'
import { getRandomPrompt } from '@/lib/conversations'

interface ChatMessage {
  id: string
  role: 'USER' | 'SYSTEM'
  content: string
}

const COMMON_SYMPTOMS = [
  'Headache', 'Fever', 'Cough', 'Chest pain',
  'Shortness of breath', 'Nausea', 'Fatigue', 'Sore throat',
  'Abdominal pain', 'Dizziness', 'Back pain', 'Rash',
]

export default function AssessmentPage() {
  const navigate = useNavigate()
  const { addToast } = useToast()

  const {
    sessionId,
    currentQuestion,
    isComplete,
    startSession,
    setCurrentQuestion,
    setSymptoms,
    completeSession,
    resetSession,
    resumeSession,
  } = useAssessmentStore()

  const [transcript, setTranscript] = useState<ChatMessage[]>([])
  const [symptomInput, setSymptomInput] = useState('')
  const [showSymptomChips, setShowSymptomChips] = useState(true)
  const [pendingSymptom, setPendingSymptom] = useState<string | null>(null)
  const [pendingSessionId, setPendingSessionId] = useState<string | null>(null)
  const [showPendingConfirmation, setShowPendingConfirmation] = useState(false)
  const [sufficientInfoConfirmation, setSufficientInfoConfirmation] = useState(false)
  const [isTypingSimulated, setIsTypingSimulated] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [transcript, currentQuestion, isComplete])

  // 1. Start Session Mutation
  const startMutation = useMutation({
    mutationFn: assessmentApi.start,
    onSuccess: (res) => {
      startSession(res.data.session_id)
      if (res.data.pending_symptom) {
        setPendingSymptom(res.data.pending_symptom)
        setPendingSessionId(res.data.pending_session_id || null)
        setShowPendingConfirmation(true)
        setTranscript([{
          id: crypto.randomUUID(),
          role: 'SYSTEM',
          content: `Earlier today you mentioned ${res.data.pending_symptom}. Are you still experiencing it?`
        }])
      } else {
        setTranscript([{
          id: crypto.randomUUID(),
          role: 'SYSTEM',
          content: getRandomPrompt('greetings')
        }])
      }
    },
    onError: () => {
      addToast({ type: 'error', message: 'Failed to start conversation. Please try again.' })
    }
  })

  // Start fresh or resume session on page mount
  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search)
    const isResuming = queryParams.get('resume') === 'true'

    if (isResuming && sessionId) {
      // Mark session as active so the input area is visible
      resumeSession()
      assessmentApi.getConversationTranscript(sessionId)
        .then(res => {
          const msgs = res.data.messages.map(m => ({
            id: crypto.randomUUID(),
            role: m.role as 'USER' | 'SYSTEM',
            content: m.content
          }))
          setTranscript(msgs)
          setShowSymptomChips(true)
        })
        .catch(() => {
          resetSession()
          startMutation.mutate(undefined)
        })
    } else {
      resetSession()
      startMutation.mutate(undefined)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // 2. Submit Symptoms Mutation
  const symptomsMutation = useMutation({
    mutationFn: (symptoms: string[]) => assessmentApi.submitSymptoms(sessionId!, symptoms),
    onSuccess: (res) => {
      setShowSymptomChips(false)
      setIsTypingSimulated(true)
      setTimeout(() => {
        setIsTypingSimulated(false)
        if (!res.data.next_question) {
          setSufficientInfoConfirmation(true)
          setTranscript(prev => [...prev, {
            id: crypto.randomUUID(),
            role: 'SYSTEM',
            content: getRandomPrompt('sufficientInfo')
          }])
        } else {
          setCurrentQuestion(res.data.next_question)
          setTranscript(prev => [...prev, {
            id: crypto.randomUUID(),
            role: 'SYSTEM',
            content: res.data.next_question!.question_text_en
          }])
        }
      }, 700)
    },
    onError: () => {
      setTranscript(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'SYSTEM',
        content: getRandomPrompt('errors')
      }])
    }
  })

  // 3. Submit Answer Mutation
  const answerMutation = useMutation({
    mutationFn: ({ answerText, nodeId }: { answerText: string; nodeId: string }) =>
      assessmentApi.submitAnswer(sessionId!, nodeId, answerText),
    onSuccess: (res) => {
      setIsTypingSimulated(true)
      setTimeout(() => {
        setIsTypingSimulated(false)
        if (res.data.is_completed) {
          setSufficientInfoConfirmation(true)
          setTranscript(prev => [...prev, {
            id: crypto.randomUUID(),
            role: 'SYSTEM',
            content: getRandomPrompt('sufficientInfo')
          }])
        } else if (res.data.next_question) {
          setCurrentQuestion(res.data.next_question)
          setTranscript(prev => [...prev, {
            id: crypto.randomUUID(),
            role: 'SYSTEM',
            content: res.data.next_question!.question_text_en
          }])
        }
      }, 600)
    },
    onError: () => {
      setTranscript(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'SYSTEM',
        content: "Something went wrong. Please try again."
      }])
    }
  })

  const isThinking = startMutation.isPending || symptomsMutation.isPending || answerMutation.isPending || isTypingSimulated

  const handleSymptomSubmit = (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!symptomInput.trim()) return
    const input = symptomInput.trim()
    setTranscript(prev => [...prev, { id: crypto.randomUUID(), role: 'USER', content: input }])
    setSymptomInput('')
    setSymptoms([input])
    setShowSymptomChips(false)
    symptomsMutation.mutate([input])
  }

  const handleCommonSymptomClick = (symptom: string) => {
    setTranscript(prev => [...prev, { id: crypto.randomUUID(), role: 'USER', content: symptom }])
    setSymptoms([symptom])
    setShowSymptomChips(false)
    symptomsMutation.mutate([symptom])
  }

  const handleConfirmPending = () => {
    if (!pendingSymptom) return
    setTranscript(prev => [...prev, { id: crypto.randomUUID(), role: 'USER', content: `Yes, I still have it` }])
    setShowPendingConfirmation(false)
    symptomsMutation.mutate([pendingSymptom])
  }

  const handleRejectPending = () => {
    if (pendingSessionId) {
      assessmentApi.resolveSession(pendingSessionId).catch(console.error)
    }
    setTranscript(prev => [
      ...prev,
      { id: crypto.randomUUID(), role: 'USER', content: "No, something else" },
      { id: crypto.randomUUID(), role: 'SYSTEM', content: getRandomPrompt('greetings') }
    ])
    setShowPendingConfirmation(false)
    setShowSymptomChips(true)
  }

  const handleContinueTalking = () => {
    setTranscript(prev => [...prev, { id: crypto.randomUUID(), role: 'USER', content: "Continue talking" }])
    setSufficientInfoConfirmation(false)
    setShowSymptomChips(true)
  }

  const handleGenerateAssessment = () => {
    setSufficientInfoConfirmation(false)
    setTranscript(prev => [...prev, { id: crypto.randomUUID(), role: 'SYSTEM', content: getRandomPrompt('transitions') }])
    setIsTypingSimulated(true)
    setTimeout(() => {
      setIsTypingSimulated(false)
      completeSession()
      navigate(`/assessment/${sessionId}/result`)
    }, 1500)
  }

  const handleAnswerSubmit = (answer: string | string[]) => {
    const answerText = Array.isArray(answer) ? answer.join(',') : answer
    const nodeId = currentQuestion!.node_id
    let displayContent = answerText
    if (currentQuestion?.options) {
      const selectedOpts = currentQuestion.options.filter(o =>
        Array.isArray(answer) ? answer.includes(o.option_value) : o.option_value === answer
      )
      if (selectedOpts.length > 0) displayContent = selectedOpts.map(o => o.label_en).join(', ')
    }
    setTranscript(prev => [...prev, { id: crypto.randomUUID(), role: 'USER', content: displayContent }])
    setCurrentQuestion(null)
    answerMutation.mutate({ answerText, nodeId })
  }

  return (
    /*
     * Full-screen column layout:
     * - Header: fixed height, never scrolls
     * - Chat: flex-1, scrollable
     * - Input: fixed height, always visible at bottom
     */
    <div className="fixed inset-0 flex flex-col bg-background" style={{ top: '3.5rem', bottom: '2.5rem' }}>

      {/* ── Scrollable Chat Area ───────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <div className="mx-auto max-w-2xl flex flex-col gap-4">
          <AssessmentNotice />

          <div className="flex flex-col gap-3">
            {transcript.map((msg) => (
              <ChatBubble key={msg.id} role={msg.role} message={msg.content} />
            ))}
          </div>

          {startMutation.isError && (
            <div className="flex flex-col items-center gap-3 py-8 text-center">
              <p className="text-sm text-muted-foreground">Could not connect to the triage service.</p>
              <Button onClick={() => startMutation.mutate(undefined)} size="lg" className="w-full sm:w-auto h-12 px-8">Retry</Button>
            </div>
          )}

          <div aria-live="polite">
            {isThinking && <TypingIndicator />}
          </div>

          {/* Spacer so last message isn't hidden behind input */}
          <div ref={chatEndRef} className="h-2" />
        </div>
      </div>

      {/* ── Sticky Input Area ─────────────────────────────────────── */}
      <div className="shrink-0 border-t border-border/50 bg-background/95 backdrop-blur-md px-3 pt-2 pb-3">
        <div className="mx-auto max-w-2xl space-y-2">

          {/* Health Memory Confirmation */}
          {showPendingConfirmation && !isThinking && (
            <div className="flex gap-3 justify-center py-2">
              <Button onClick={handleConfirmPending} className="flex-1 max-w-[200px] h-11 rounded-xl">
                Yes, I still have it
              </Button>
              <Button onClick={handleRejectPending} variant="outline" className="flex-1 max-w-[200px] h-11 rounded-xl">
                No, something else
              </Button>
            </div>
          )}

          {/* Sufficient Info Confirmation */}
          {sufficientInfoConfirmation && !isThinking && (
            <div className="flex gap-3 justify-center py-2">
              <Button onClick={handleContinueTalking} variant="outline" className="flex-1 max-w-[200px] h-11 rounded-xl">
                Continue Talking
              </Button>
              <Button onClick={handleGenerateAssessment} className="flex-1 max-w-[200px] h-11 rounded-xl">
                Generate My Assessment
              </Button>
            </div>
          )}

          {/* Symptom chips — shown only before first selection */}
          {!showPendingConfirmation && !sufficientInfoConfirmation && !currentQuestion && !isThinking && !isComplete && showSymptomChips && (
            <div className="flex overflow-x-auto gap-2 pb-1 hide-scrollbar">
              {COMMON_SYMPTOMS.map(sym => (
                <button
                  key={sym}
                  onClick={() => handleCommonSymptomClick(sym)}
                  className="shrink-0 rounded-full border border-border bg-muted/50 px-4 py-2 text-[13px] font-medium text-muted-foreground transition-colors hover:border-primary/50 hover:bg-primary/5 hover:text-primary whitespace-nowrap"
                >
                  {sym}
                </button>
              ))}
            </div>
          )}

          {/* Free-text input (shown before question is active) */}
          {!showPendingConfirmation && !sufficientInfoConfirmation && !currentQuestion && !isThinking && !isComplete && (
            <form onSubmit={handleSymptomSubmit} className="relative flex items-center">
              <Input
                className="w-full rounded-2xl pl-4 pr-12 h-11 bg-muted/50 border-border/50 text-sm placeholder:text-muted-foreground/60 focus-visible:ring-1 focus-visible:ring-primary/40 focus-visible:border-primary/40"
                placeholder="Describe your symptoms..."
                value={symptomInput}
                onChange={(e) => setSymptomInput(e.target.value)}
                autoFocus
              />
              <button
                type="submit"
                disabled={!symptomInput.trim()}
                aria-label="Send symptom"
                className="absolute right-2 flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground shadow transition-opacity disabled:opacity-30 active:scale-95"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>
                </svg>
              </button>
            </form>
          )}

          {/* Question options (shown when there's an active question) */}
          {!showPendingConfirmation && !sufficientInfoConfirmation && currentQuestion && !isThinking && (
            <QuestionCard
              question={currentQuestion as any}
              onSubmit={handleAnswerSubmit}
            />
          )}

          {/* While thinking, show a subtle placeholder */}
          {isThinking && (
            <div className="h-11 rounded-2xl bg-muted/50 border border-border/50 animate-pulse" />
          )}
        </div>
      </div>
    </div>
  )
}
