import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { assessmentApi } from '@/services/api'
import { useAssessmentStore } from '@/stores/assessment-store'
import { useSettingsStore } from '@/stores/settings-store'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/Button'
import { VoiceWave, type VoiceState } from '../components/VoiceWave'
import { parseVoiceCommand } from '@/lib/voice-commands'
import { getRandomPrompt } from '@/lib/conversations'

// Polyfill for vendor prefixes
const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

import { useAuthStore } from '@/stores/auth-store'
import { GuestBlock } from '@/components/common/GuestBlock'
import { AssessmentNotice } from '@/features/assessment/components/AssessmentNotice'

export default function VoicePage() {
  const navigate = useNavigate()
  const { addToast } = useToast()
  const { userRole } = useAuthStore()
  
  const {
    sessionId,
    startSession,
    setCurrentQuestion,
    completeSession,
    resetSession,
    resumeSession,
    isComplete
  } = useAssessmentStore()
  
  const { preferredVoiceURI } = useSettingsStore()

  if (userRole === 'GUEST') {
    return <GuestBlock featureName="Voice Consultation" icon="🎙️" />
  }

  const [voiceState, setVoiceState] = useState<VoiceState>('IDLE')
  const [transcriptText, setTranscriptText] = useState('')
  const [systemMessage, setSystemMessage] = useState('')
  const [hasReadNotice, setHasReadNotice] = useState(false)
  const [showAssessmentNotice, setShowAssessmentNotice] = useState(false)
  
  // Refs to manage native API instances
  const recognitionRef = useRef<any>(null)
  const isComponentMounted = useRef(true)
  const speechRate = useRef(1)

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
    utterance.rate = speechRate.current
    
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
      
      let intro = ""
      if (!hasReadNotice) {
        setShowAssessmentNotice(true)
        intro += "Health Guidance Notice. This assessment provides health guidance based on the information you share. It is not a medical diagnosis and does not replace care from a qualified healthcare professional. "
        setHasReadNotice(true)
      }

      if (res.data.pending_symptom) {
        intro += `Earlier today you mentioned ${res.data.pending_symptom}. Are you still experiencing it?`
      } else {
        intro += "Hi! I'm your Health Triage Assistant. What symptoms are you experiencing today?"
      }
      
      speakText(intro, () => {
        startListening()
      })
    },
    onError: () => {
      setVoiceState('IDLE')
      addToast({ message: 'Failed to start session. Please try again.', type: 'error' })
    }
  })

  // Start fresh session or resume on mount
  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search)
    const isResuming = queryParams.get('resume') === 'true'

    if (isResuming && sessionId && !isComplete) {
      resumeSession()
      setVoiceState('PROCESSING')
      // If we're resuming a session, get the transcript to figure out where we are.
      assessmentApi.getConversationTranscript(sessionId)
        .then(res => {
          const msgs = res.data.messages
          if (msgs.length > 0) {
            const lastMsg = msgs[msgs.length - 1]
            if (lastMsg.role === 'SYSTEM') {
              speakText(lastMsg.content, () => startListening())
            } else {
               speakText("I'm ready to continue.", () => startListening())
            }
          }
        })
        .catch(() => {
          resetSession()
          startMutation.mutate()
        })
    } else {
      resetSession()
      setVoiceState('PROCESSING')
      startMutation.mutate()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // 2. Submit Symptoms Mutation
  const symptomsMutation = useMutation({
    mutationFn: ({ sid, symptoms }: { sid: string; symptoms: string[] }) =>
      assessmentApi.submitSymptoms(sid, symptoms),
    onSuccess: (res) => {
      if (res.data.is_emergency) {
        speakText("I'm concerned about what you've shared. I'm going to ask a few important questions so I can provide the safest guidance.", () => {
           if (res.data.next_question) {
              setCurrentQuestion(res.data.next_question)
              askQuestion(res.data.next_question.question_text_en)
           }
        })
      } else if (res.data.is_completed) {
        handleCompletion()
      } else if (res.data.next_question) {
        setCurrentQuestion(res.data.next_question)
        askQuestion(res.data.next_question.question_text_en)
      } else {
         // No next question, meaning it's ready for assessment generation.
         speakText("I think I have enough information. Before I prepare your assessment, is there anything else you'd like to tell me?", () => startListening())
      }
    },
    onError: () => {
      speakText("I couldn't quite understand that symptom. Could you please rephrase it?", () => {
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
        speakText("I think I have enough information. Before I prepare your assessment, is there anything else you'd like to tell me?", () => startListening())
      } else if (res.data.next_question) {
        setCurrentQuestion(res.data.next_question)
        // Add a conversational transition before the next question
        const transition = getRandomPrompt('transitions')
        speakText(`${transition}. ${res.data.next_question.question_text_en}`, () => startListening())
      }
    },
    onError: () => {
      speakText("I didn't quite catch that. Could you repeat your answer?", () => {
        startListening()
      })
    }
  })
  
  // 4. Get Assessment Result Mutation
  const resultMutation = useMutation({
      mutationFn: (sid: string) => assessmentApi.getResult(sid),
      onSuccess: (res) => {
         const result = res.data
         let resultText = `Assessment Summary. ${result.explanation}. `
         if (result.recommendations && result.recommendations.length > 0) {
             resultText += `Recommended next steps: ${result.recommendations.join(', ')}. `
         }
         resultText += "Is there anything else you'd like to discuss today?"
         
         speakText(resultText, () => startListening())
      },
      onError: () => {
          speakText("I'm sorry, I encountered an error while generating your assessment. Please open the results page manually.", () => navigate(`/assessment/${sessionId}/result`))
      }
  })

  const handleCompletion = () => {
    completeSession()
    speakText("I'm generating your assessment now...", () => {
        if (sessionId) resultMutation.mutate(sessionId)
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

  const executeCommand = (command: string) => {
      switch (command) {
          case 'CONVERSATION_CONTINUE':
             if (useAssessmentStore.getState().currentQuestion) {
                 speakText("Please answer the last question.", () => startListening())
             } else {
                 handleCompletion()
             }
             break;
          case 'CONVERSATION_FINISH':
             handleCompletion()
             break;
          case 'CONVERSATION_START_OVER':
             resetSession()
             startMutation.mutate()
             break;
          case 'CONVERSATION_CANCEL':
             handleEndTriage()
             break;
          case 'SPEECH_STOP':
          case 'SPEECH_PAUSE':
             window.speechSynthesis.cancel()
             setVoiceState('IDLE')
             break;
          case 'SPEECH_RESUME':
             startListening()
             break;
          case 'SPEECH_REPEAT':
             speakText(systemMessage, () => startListening())
             break;
          case 'SPEECH_SLOWER':
             speechRate.current = Math.max(0.5, speechRate.current - 0.25)
             speakText("I will speak slower. " + systemMessage, () => startListening())
             break;
          case 'SPEECH_FASTER':
             speechRate.current = Math.min(2.0, speechRate.current + 0.25)
             speakText("I will speak faster. " + systemMessage, () => startListening())
             break;
          case 'NAV_BACK':
             navigate(-1)
             break;
          case 'NAV_NEXT':
          case 'NAV_RESULTS':
             if (sessionId) navigate(`/assessment/${sessionId}/result`)
             break;
          case 'NAV_HISTORY':
             navigate('/history')
             break;
          case 'NAV_EMERGENCY':
             navigate('/emergency')
             break;
          case 'NAV_PROFILE':
             navigate('/profile')
             break;
          case 'NAV_SETTINGS':
             navigate('/settings')
             break;
          case 'HELP':
             speakText("You can say commands like 'repeat that', 'stop speaking', 'go back', 'open results', or 'finish assessment'.", () => startListening())
             break;
      }
  }

  const handleUserUtterance = (text: string) => {
    stopListening()
    
    // Intercept Voice Commands
    const command = parseVoiceCommand(text)
    if (command) {
        executeCommand(command)
        return
    }

    setVoiceState('PROCESSING')
    const sid = useAssessmentStore.getState().sessionId
    const question = useAssessmentStore.getState().currentQuestion
    const completed = useAssessmentStore.getState().isComplete

    if (!sid) {
      speakText('Session not ready yet. Please wait a moment and try again.', () => startListening())
      return
    }
    
    const lowerText = text.toLowerCase().replace(/[^\w\s]/g, '').trim()
    
    if (completed) {
        if (lowerText === 'no' || lowerText === 'nope' || lowerText.includes('nothing')) {
            handleEndTriage()
        } else if (lowerText === 'yes' || lowerText.includes('yes') || lowerText.includes('more')) {
            // Start a new session seamlessly
            resetSession()
            startMutation.mutate()
        } else {
           speakText("I didn't quite catch that. Would you like to discuss anything else?", () => startListening())
        }
        return
    }
    
    // Check for confirmations to "I think I have enough information..."
    if (!question) {
        if (lowerText === 'yes' || lowerText === 'yeah' || lowerText === 'no' || lowerText === 'nope' || lowerText.includes('no more') || lowerText.includes('thats all')) {
             if (lowerText === 'yes' || lowerText === 'yeah') {
                 speakText("Okay, please tell me what else you're experiencing.", () => startListening())
             } else {
                 handleCompletion()
             }
             return
        }
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
    <div className="mx-auto flex h-full max-h-full max-w-2xl flex-col items-center justify-between p-4 sm:p-6 text-center relative overflow-hidden">
      
      {showAssessmentNotice && (
         <div className="w-full mt-2 sm:mt-4 z-10 flex-shrink-0">
             <AssessmentNotice />
         </div>
      )}

      {/* Dynamic System Message */}
      <div className="mt-4 sm:mt-8 min-h-[3rem] sm:min-h-[4rem] flex items-center justify-center flex-shrink-0 px-2">
        {voiceState === 'SPEAKING' && (
          <h2 className="text-xl sm:text-2xl font-semibold text-foreground animate-pulse">
            {systemMessage}
          </h2>
        )}
        {voiceState === 'LISTENING' && (
          <h2 className="text-xl sm:text-2xl font-semibold text-primary">
            I'm listening...
          </h2>
        )}
        {voiceState === 'PROCESSING' && (
          <h2 className="text-xl sm:text-2xl font-semibold text-muted-foreground">
            Thinking...
          </h2>
        )}
      </div>

      {/* Main Visualizer */}
      <div className="flex-1 flex items-center justify-center min-h-[160px]">
        <VoiceWave state={voiceState} />
      </div>

      {/* Transcript / Spoken Feedback */}
      <div className="mb-4 sm:mb-8 min-h-[2.5rem] sm:min-h-[3rem] w-full max-w-md rounded-xl bg-accent/50 p-3 sm:p-4 flex-shrink-0 flex items-center justify-center">
        {transcriptText ? (
          <p className="text-base sm:text-lg text-foreground line-clamp-2">"{transcriptText}"</p>
        ) : (
          <p className="text-base sm:text-lg text-muted-foreground italic">
            {voiceState === 'LISTENING' ? 'Speak clearly into your microphone' : 'Waiting...'}
          </p>
        )}
      </div>

      {/* Controls */}
      <div className="flex gap-3 sm:gap-4 flex-shrink-0 mb-4 sm:mb-8">
        {voiceState === 'IDLE' ? (
          <Button size="lg" className="rounded-full px-6 py-4 sm:px-8 sm:py-6 text-base sm:text-lg" onClick={startListening}>
            Tap to Speak
          </Button>
        ) : voiceState === 'LISTENING' ? (
           <Button size="lg" variant="outline" className="rounded-full px-6 py-4 sm:px-8 sm:py-6 text-base sm:text-lg" onClick={stopListening}>
             Pause
           </Button>
        ) : null}
        
        <Button size="lg" variant="danger" className="rounded-full px-6 py-4 sm:px-8 sm:py-6 text-base sm:text-lg" onClick={handleEndTriage}>
          End Triage
        </Button>
      </div>
      
    </div>
  )
}
