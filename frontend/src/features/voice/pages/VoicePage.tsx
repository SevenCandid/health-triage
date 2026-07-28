import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { assessmentApi } from '@/services/api'
import { useAssessmentStore } from '@/stores/assessment-store'
import { useSettingsStore } from '@/stores/settings-store'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/Button'
import { VoiceWave, type VoiceState } from '../components/VoiceWave'

// Polyfill for vendor prefixes — cast to any since TypeScript's Window type may lag browser support
const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

import { useAuthStore } from '@/stores/auth-store'
import { GuestBlock } from '@/components/common/GuestBlock'

export default function VoicePage() {
  const navigate = useNavigate()
  const { addToast } = useToast()
  const { userRole } = useAuthStore()
  
  const {
    sessionId,
    startSession,
    setCurrentQuestion,
    completeSession,
    resetSession
  } = useAssessmentStore()
  
  const { preferredVoiceURI } = useSettingsStore()

  if (userRole === 'GUEST') {
    return <GuestBlock featureName="Voice Consultation" icon="🎙️" />
  }

  const [voiceState, setVoiceState] = useState<VoiceState>('IDLE')
  const [transcriptText, setTranscriptText] = useState('')
  const [systemMessage, setSystemMessage] = useState('')
  
  // Refs to manage native API instances
  const recognitionRef = useRef<any>(null)
  const isComponentMounted = useRef(true)

  // Initialize Speech Recognition
  useEffect(() => {
    isComponentMounted.current = true
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition()
      recognition.continuous = false
      recognition.lang = 'en-US'
      recognition.interimResults = true
      recognition.maxAlternatives = 1

      recognition.onresult = (event: any) => {
        let interimTranscript = ''
        let finalTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript
          } else {
            interimTranscript += event.results[i][0].transcript
          }
        }
        
        setTranscriptText(finalTranscript || interimTranscript)
        
        if (finalTranscript) {
          handleUserUtterance(finalTranscript)
        }
      }

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error', event.error)
        setVoiceState('IDLE')
        if (event.error !== 'no-speech') {
          addToast({ message: 'Could not hear you properly. Try speaking again.', type: 'error' })
        }
      }

      recognition.onend = () => {
        // If we were listening and it ended without final result, go idle
        setVoiceState(prev => prev === 'LISTENING' ? 'IDLE' : prev)
      }

      recognitionRef.current = recognition
    } else {
      addToast({ message: 'Voice recognition is not supported in this browser.', type: 'error' })
    }

    return () => {
      isComponentMounted.current = false
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      window.speechSynthesis.cancel()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const speakText = useCallback((text: string, onEnd?: () => void) => {
    if (!isComponentMounted.current) return

    window.speechSynthesis.cancel()
    setVoiceState('SPEAKING')
    setSystemMessage(text)

    const utterance = new SpeechSynthesisUtterance(text)
    
    // Apply preferred voice if exists
    if (preferredVoiceURI) {
      const voices = window.speechSynthesis.getVoices()
      const selected = voices.find(v => v.voiceURI === preferredVoiceURI)
      if (selected) utterance.voice = selected
    }

    utterance.onend = () => {
      if (!isComponentMounted.current) return
      setVoiceState('IDLE')
      if (onEnd) onEnd()
    }

    utterance.onerror = () => {
      if (!isComponentMounted.current) return
      setVoiceState('IDLE')
      if (onEnd) onEnd()
    }

    window.speechSynthesis.speak(utterance)
  }, [preferredVoiceURI])

  // 1. Start Session Mutation
  const startMutation = useMutation({
    mutationFn: () => assessmentApi.start('VOICE'),
    onSuccess: (res) => {
      startSession(res.data.session_id)
      const intro = "Hi! I'm your Health Triage Assistant. What symptoms are you experiencing today?"
      speakText(intro, () => {
        startListening()
      })
    },
    onError: () => {
      setVoiceState('IDLE')
      addToast({ message: 'Failed to start session. Please try again.', type: 'error' })
    }
  })

  // Start fresh session on mount
  useEffect(() => {
    resetSession()
    setVoiceState('PROCESSING')
    startMutation.mutate()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // 2. Submit Symptoms Mutation
  const symptomsMutation = useMutation({
    mutationFn: ({ sid, symptoms }: { sid: string; symptoms: string[] }) =>
      assessmentApi.submitSymptoms(sid, symptoms),
    onSuccess: (res) => {
      if (res.data.is_completed) {
        handleCompletion()
      } else if (res.data.next_question) {
        setCurrentQuestion(res.data.next_question)
        askQuestion(res.data.next_question.question_text_en)
      }
    },
    onError: () => {
      speakText("I couldn't find that symptom. Could you please rephrase it?", () => {
        startListening()
      })
    }
  })

  // 3. Submit Answer Mutation
  const answerMutation = useMutation({
    mutationFn: ({ sid, answerText, nodeId }: { sid: string; answerText: string; nodeId: string }) =>
      assessmentApi.submitAnswer(sid, nodeId, answerText),
    onSuccess: (res) => {
      if (res.data.is_completed) {
        handleCompletion()
      } else if (res.data.next_question) {
        setCurrentQuestion(res.data.next_question)
        askQuestion(res.data.next_question.question_text_en)
      }
    },
    onError: () => {
      speakText("I didn't quite catch that. Could you repeat your answer?", () => {
        startListening()
      })
    }
  })

  const handleCompletion = () => {
    completeSession()
    speakText("Assessment complete. I'm taking you to your results now.", () => {
      navigate(`/assessment/${sessionId}/result`)
    })
  }

  const askQuestion = (questionText: string) => {
    speakText(questionText, () => {
      startListening()
    })
  }

  const startListening = () => {
    if (recognitionRef.current && isComponentMounted.current) {
      setVoiceState('LISTENING')
      setTranscriptText('')
      try {
        recognitionRef.current.start()
      } catch (_e) {
        // Ignored if already started
      }
    }
  }

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      setVoiceState('IDLE')
    }
  }

  const handleUserUtterance = (text: string) => {
    stopListening()
    setVoiceState('PROCESSING')
    // Read sessionId FRESH from the store at call-time to avoid stale closure
    const sid = useAssessmentStore.getState().sessionId
    const question = useAssessmentStore.getState().currentQuestion

    if (!sid) {
      speakText('Session not ready yet. Please wait a moment and try again.', () => startListening())
      return
    }

    if (!question) {
      // Initial symptom phase
      symptomsMutation.mutate({ sid, symptoms: [text] })
    } else {
      // Answering a follow-up question
      const nodeId = question.node_id
      answerMutation.mutate({ sid, answerText: text, nodeId })
    }
  }

  const handleEndTriage = () => {
    stopListening()
    window.speechSynthesis.cancel()
    resetSession()
    navigate('/dashboard')
  }

  return (
    <div className="mx-auto flex h-full max-w-2xl flex-col items-center justify-center p-6 text-center">
      
      {/* Dynamic System Message */}
      <div className="mb-12 min-h-[4rem]">
        {voiceState === 'SPEAKING' && (
          <h2 className="text-2xl font-semibold text-foreground animate-pulse">
            {systemMessage}
          </h2>
        )}
        {voiceState === 'LISTENING' && (
          <h2 className="text-2xl font-semibold text-primary">
            I'm listening...
          </h2>
        )}
        {voiceState === 'PROCESSING' && (
          <h2 className="text-2xl font-semibold text-muted-foreground">
            Thinking...
          </h2>
        )}
      </div>

      {/* Main Visualizer */}
      <div className="mb-12">
        <VoiceWave state={voiceState} />
      </div>

      {/* Transcript / Spoken Feedback */}
      <div className="mb-12 min-h-[3rem] w-full max-w-md rounded-xl bg-accent/50 p-4">
        {transcriptText ? (
          <p className="text-lg text-foreground">"{transcriptText}"</p>
        ) : (
          <p className="text-lg text-muted-foreground italic">
            {voiceState === 'LISTENING' ? 'Speak clearly into your microphone' : 'Waiting...'}
          </p>
        )}
      </div>

      {/* Controls */}
      <div className="flex gap-4">
        {voiceState === 'IDLE' ? (
          <Button size="lg" className="rounded-full px-8 py-6 text-lg" onClick={startListening}>
            Tap to Speak
          </Button>
        ) : voiceState === 'LISTENING' ? (
           <Button size="lg" variant="outline" className="rounded-full px-8 py-6 text-lg" onClick={stopListening}>
             Pause
           </Button>
        ) : null}
        
        <Button size="lg" variant="danger" className="rounded-full px-8 py-6 text-lg" onClick={handleEndTriage}>
          End Triage
        </Button>
      </div>
      
    </div>
  )
}
