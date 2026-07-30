import { Mic, Volume2 } from 'lucide-react'
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
import { LanguageSwitcher } from '@/components/common/LanguageSwitcher'

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
  
  const { preferredVoiceURI, voiceRate, voicePitch, voiceVolume, autoReadResponses, handsFreeMode, appLanguage } = useSettingsStore()

  if (userRole === 'GUEST') {
    return <GuestBlock featureName="Voice Consultation" icon=<Mic className="w-4 h-4" /> />
  }

  const [voiceState, setVoiceState] = useState<VoiceState>('IDLE')
  const [transcriptText, setTranscriptText] = useState('')
  const [systemMessage, setSystemMessage] = useState('')
  const [hasReadNotice, setHasReadNotice] = useState(false)
  const [showAssessmentNotice, setShowAssessmentNotice] = useState(false)
  const [isConfirmingCompletion, setIsConfirmingCompletion] = useState(false)
  
  // Refs to manage native API instances
  const recognitionRef = useRef<any>(null)
  const isComponentMounted = useRef(true)
  const handleUserUtteranceRef = useRef<(text: string) => void>(() => {})
  const activeUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null)

  // Initialize Speech Recognition
  useEffect(() => {
    isComponentMounted.current = true
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition()
      recognition.continuous = false
      const localeMap: Record<string, string> = {
        'en': 'en-US',
        'tw': 'tw-GH',
        'fr': 'fr-FR',
        'ar': 'ar-SA',
        'pt': 'pt-PT'
      }
      recognition.lang = localeMap[appLanguage] || 'en-US'
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
          handleUserUtteranceRef.current(finalTranscript)
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

  useEffect(() => {
    if (recognitionRef.current) {
      const localeMap: Record<string, string> = {
        'en': 'en-US',
        'tw': 'tw-GH',
        'fr': 'fr-FR',
        'ar': 'ar-SA',
        'pt': 'pt-PT'
      }
      recognitionRef.current.lang = localeMap[appLanguage] || 'en-US'
      
      // Stop current speech
      window.speechSynthesis.cancel()
      
      if (voiceState === 'LISTENING') {
        recognitionRef.current.stop()
        setTimeout(() => {
          if (isComponentMounted.current) {
            try { recognitionRef.current.start() } catch (e) {}
          }
        }, 100)
      }
    }
  }, [appLanguage])

  const speakText = useCallback((text: string, onEnd?: () => void, displayText?: string) => {
    if (!isComponentMounted.current) return

    window.speechSynthesis.cancel()
    setSystemMessage(displayText !== undefined ? displayText : text)

    const handleEnd = () => {
      if (!isComponentMounted.current) return
      setVoiceState('IDLE')
      if (onEnd) {
         if (onEnd.toString().includes('startListening') && !handsFreeMode) {
             // Do not automatically start listening if hands-free is off
         } else {
             onEnd()
         }
      }
    }

    if (!autoReadResponses) {
      setVoiceState('IDLE')
      // Brief delay to allow UI to render before we potentially start listening
      setTimeout(handleEnd, 100)
      return
    }

    setVoiceState('SPEAKING')
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = voiceRate
    utterance.pitch = voicePitch
    utterance.volume = voiceVolume
    
    const voices = window.speechSynthesis.getVoices()
    let selectedVoice = preferredVoiceURI ? voices.find(v => v.voiceURI === preferredVoiceURI) : null
    
    if (appLanguage === 'tw') {
      const twiVoice = voices.find(v => v.lang.toLowerCase().startsWith('tw') || v.lang.toLowerCase().startsWith('ak'))
      if (twiVoice) {
        selectedVoice = twiVoice
      }
    }

    if (selectedVoice) utterance.voice = selectedVoice

    utterance.onend = () => {
      activeUtteranceRef.current = null
      handleEnd()
    }
    utterance.onerror = () => {
      activeUtteranceRef.current = null
      handleEnd()
    }

    activeUtteranceRef.current = utterance
    window.speechSynthesis.speak(utterance)
  }, [preferredVoiceURI, voiceRate, voicePitch, voiceVolume, autoReadResponses, handsFreeMode])

  const manualSpeak = () => {
     window.speechSynthesis.cancel()
     setVoiceState('SPEAKING')
     const utterance = new SpeechSynthesisUtterance(systemMessage)
     utterance.rate = voiceRate
     utterance.pitch = voicePitch
     utterance.volume = voiceVolume
     
     const voices = window.speechSynthesis.getVoices()
     let selectedVoice = preferredVoiceURI ? voices.find(v => v.voiceURI === preferredVoiceURI) : null
     
     if (appLanguage === 'tw') {
       const twiVoice = voices.find(v => v.lang.toLowerCase().startsWith('tw') || v.lang.toLowerCase().startsWith('ak'))
       if (twiVoice) {
         selectedVoice = twiVoice
       }
     }
 
     if (selectedVoice) utterance.voice = selectedVoice

     utterance.onend = () => { 
       activeUtteranceRef.current = null
       setVoiceState('IDLE') 
     }
     utterance.onerror = () => { 
       activeUtteranceRef.current = null
       setVoiceState('IDLE') 
     }
     activeUtteranceRef.current = utterance
     window.speechSynthesis.speak(utterance)
  }

  // 1. Start Session Mutation
  const startMutation = useMutation({
    mutationFn: () => assessmentApi.start('VOICE'),
    onSuccess: (res) => {
      startSession(res.data.session_id)
      
      let textToSpeak = ""
      let textToDisplay = ""
      if (!hasReadNotice) {
        setShowAssessmentNotice(true)
        textToSpeak += "Health Guidance Notice. This assessment provides health guidance based on the information you share. It is not a medical diagnosis and does not replace care from a qualified healthcare professional. "
        setHasReadNotice(true)
      }

      if (res.data.pending_symptom) {
        const t = appLanguage === 'tw' 
          ? `Nnɛ woka kyerɛɛ me sɛ wote ${res.data.pending_symptom}. Woda so ara te nka anaa?`
          : `Earlier today you mentioned ${res.data.pending_symptom}. Are you still experiencing it?`
        textToSpeak += t
        textToDisplay = t
      } else {
        const t = appLanguage === 'tw'
          ? "Akwaaba! Mɛyɛ dɛn atumi aboa wo nnɛ? Ɔhaw bɛn na wote nka?"
          : "Hi! I'm FirstAid+. What symptoms are you experiencing today?"
        textToSpeak += t
        textToDisplay = t
      }
      
      speakText(textToSpeak, () => {
        startListening()
      }, textToDisplay)
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
        const emergencyMsg = appLanguage === 'tw'
          ? "Asɛm a woaka no yɛ aniberesɛm. Mebisa wo nsɛm kakra na matumi aboa wo yiye."
          : "I'm concerned about what you've shared. I'm going to ask a few important questions so I can provide the safest guidance."
        speakText(emergencyMsg, () => {
           if (res.data.next_question) {
              setCurrentQuestion(res.data.next_question)
              askQuestion(appLanguage === 'tw' ? res.data.next_question.question_text_tw || res.data.next_question.question_text_en : res.data.next_question.question_text_en)
           }
        })
      } else if (res.data.is_completed) {
         setIsConfirmingCompletion(true)
         speakText(getRandomPrompt('sufficientInfo', appLanguage as 'en' | 'tw'), () => startListening())
      } else if (res.data.next_question) {
        setCurrentQuestion(res.data.next_question)
        askQuestion(appLanguage === 'tw' ? res.data.next_question.question_text_tw || res.data.next_question.question_text_en : res.data.next_question.question_text_en)
      } else {
         // No next question, meaning it's ready for assessment generation.
         setIsConfirmingCompletion(true)
         speakText(getRandomPrompt('sufficientInfo', appLanguage as 'en' | 'tw'), () => startListening())
      }
    },
    onError: (error: any) => {
      let msg = getRandomPrompt('errors', appLanguage as 'en' | 'tw')
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          msg = error.response.data.detail[0]?.msg || msg
        } else if (typeof error.response.data.detail === 'string') {
          msg = error.response.data.detail
        }
      }
      speakText(msg, () => {
        startListening()
      })
    }
  })

  // 3. Submit Answer Mutation
  const answerMutation = useMutation({
    mutationFn: ({ sid, answerValue, answerRawText, nodeId }: { sid: string; answerValue: string; answerRawText: string; nodeId: string }) =>
      assessmentApi.submitAnswer(sid, nodeId, answerValue, answerRawText),
    onSuccess: (res) => {
      if (res.data.is_completed) {
        setIsConfirmingCompletion(true)
        speakText(getRandomPrompt('sufficientInfo', appLanguage as 'en' | 'tw'), () => startListening())
      } else if (res.data.next_question) {
        setCurrentQuestion(res.data.next_question)
        // Add a conversational transition before the next question
        const transition = getRandomPrompt('transitions', appLanguage as 'en' | 'tw')
        const qText = appLanguage === 'tw' ? res.data.next_question.question_text_tw || res.data.next_question.question_text_en : res.data.next_question.question_text_en
        speakText(`${transition}. ${qText}`, () => startListening())
      }
    },
    onError: (error: any) => {
      let msg = getRandomPrompt('errors', appLanguage as 'en' | 'tw')
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          msg = error.response.data.detail[0]?.msg || msg
        } else if (typeof error.response.data.detail === 'string') {
          msg = error.response.data.detail
        }
      }
      speakText(msg, () => {
        startListening()
      })
    }
  })
  
  // 4. Get Assessment Result Mutation
  const resultMutation = useMutation({
      mutationFn: (sid: string) => assessmentApi.getResult(sid),
      onSuccess: (res) => {
         const result = res.data
         let resultText = appLanguage === 'tw' 
            ? `Nhwehwɛmu no aba. ${result.explanation}. `
            : `Assessment Summary. ${result.explanation}. `
         if (result.recommendations && result.recommendations.length > 0) {
             const recs = result.recommendations.join(', ')
             resultText += appLanguage === 'tw'
                 ? `Akwankyerɛ: ${recs}. `
                 : `Recommended next steps: ${recs}. `
         }
         resultText += appLanguage === 'tw'
            ? "Biribi foforo wɔ hɔ a wopɛ sɛ yɛka ho asɛm nnɛ?"
            : "Is there anything else you'd like to discuss today?"
         
         speakText(resultText, () => startListening())
      },
      onError: () => {
          speakText(
            appLanguage === 'tw'
              ? "Kafra, mfomso bi aba. Bubu kɔ nsunsuanso kratafa no so."
              : "I'm sorry, I encountered an error while generating your assessment. Please open the results page manually.", 
            () => navigate(`/assessment/${sessionId}/result`)
          )
      }
  })

  const handleCompletion = () => {
    completeSession()
    const msg = appLanguage === 'tw' ? "Meresiesie wo nhwehwɛmu no mprempren..." : "I'm generating your assessment now..."
    speakText(msg, () => {
        if (sessionId) navigate(`/assessment/${sessionId}/result`)
    })
  }

  const askQuestion = (questionText: string) => {
    speakText(questionText, () => {
      startListening()
    })
  }

  const startListening = () => {
    if (recognitionRef.current && isComponentMounted.current) {
      window.speechSynthesis.cancel() // Barge-in support
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
             useSettingsStore.getState().setVoiceRate(Math.max(0.5, useSettingsStore.getState().voiceRate - 0.25))
             speakText("I will speak slower. " + systemMessage, () => startListening())
             break;
          case 'SPEECH_FASTER':
             useSettingsStore.getState().setVoiceRate(Math.min(2.0, useSettingsStore.getState().voiceRate + 0.25))
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
    const completed = useAssessmentStore.getState().isComplete

    if (!sid) {
      speakText('Session not ready yet. Please wait a moment and try again.', () => startListening())
      return
    }
    
    const lowerText = text.toLowerCase().replace(/[^\w\s]/g, '').trim()
    
    if (completed) {
        const cleanResponse = lowerText.replace(/[']/g, '')
        const noRegex = /\b(no|nope|nothing|nah|none|thats all|no more)\b/i
        const yesRegex = /\b(yes|yeah|yep|yup|sure|more)\b/i
        
        if (noRegex.test(cleanResponse) || cleanResponse.includes('no thank') || cleanResponse.includes('im good')) {
            handleEndTriage()
        } else if (yesRegex.test(cleanResponse)) {
            // Start a new session seamlessly
            resetSession()
            startMutation.mutate()
        } else {
           speakText("I didn't quite catch that. Would you like to discuss anything else?", () => startListening())
        }
        return
    }
    
    // Check for confirmations to "I think I have enough information..."
    if (isConfirmingCompletion) {
        setIsConfirmingCompletion(false)
        const cleanResponse = lowerText.replace(/[']/g, '')
        
        const noConfirmRegex = /\b(no|nope|nah|none|nothing|thats all|no more|its okay|thats okay|thats fine|im good|im fine|thats enough|i dont think so)\b/i
        const yesConfirmRegex = /\b(yes|yeah|yep|yup|sure|i do)\b/i
        
        if (noConfirmRegex.test(cleanResponse) || cleanResponse.includes('i said no')) {
            handleCompletion()
            return
        }
        
        if (yesConfirmRegex.test(cleanResponse)) {
            setCurrentQuestion(null)
            speakText("Okay, please tell me what else you're experiencing.", () => startListening())
            return
        }

        // If it's not a clear yes/no, maybe they just spoke the symptom directly (e.g. "my head hurts")
        // If it looks like a negative but wasn't caught, let's play it safe and end
        if (cleanResponse.length < 15 && cleanResponse.includes('no')) {
            handleCompletion()
            return
        }

        // Fall through to symptomsMutation
        setCurrentQuestion(null)
    }

    const currentQ = useAssessmentStore.getState().currentQuestion
    if (!currentQ) {
      // Initial symptom phase
      symptomsMutation.mutate({ sid, symptoms: [text] })
    } else {
      // Answering a follow-up question
      const nodeId = currentQ.node_id
      const options = currentQ.options || []
      let answerValue = options.length > 0 ? options[0].option_value : ''
      const lowerText = text.toLowerCase()
      if (lowerText.includes('yes') || lowerText.includes('yep') || lowerText.includes('yeah') || lowerText.includes('ane') || lowerText.includes('aane') || lowerText.includes('yoo')) {
         answerValue = options.find(o => o.option_value === 'yes')?.option_value || (options.length > 0 ? options[0].option_value : '')
      } else if (lowerText.includes('no') || lowerText.includes('nope') || lowerText.includes('nah') || lowerText.includes('daabi')) {
         answerValue = options.find(o => o.option_value === 'no')?.option_value || (options.length > 1 ? options[1].option_value : (options.length > 0 ? options[0].option_value : ''))
      }
      answerMutation.mutate({ sid, answerValue, answerRawText: text, nodeId })
    }
  }

  const handleEndTriage = () => {
    stopListening()
    window.speechSynthesis.cancel()
    resetSession()
    navigate('/dashboard')
  }

  handleUserUtteranceRef.current = handleUserUtterance

  return (
    <div className="fixed inset-0 flex flex-col bg-background overflow-hidden" style={{ top: '3.5rem', bottom: '0' }}>
      <div className="mx-auto flex h-full w-full max-w-2xl flex-col items-center justify-between px-3 py-4 sm:p-6 text-center">
      
      <div className="absolute top-4 right-4 z-50">
        <LanguageSwitcher />
      </div>

      {showAssessmentNotice && (
         <div className="w-full mt-2 sm:mt-4 z-10 flex-shrink-0">
             <AssessmentNotice />
         </div>
      )}

      {/* Dynamic System Message */}
      <div className="mt-2 sm:mt-6 min-h-[4rem] sm:min-h-[5rem] flex flex-col items-center justify-center flex-shrink-0 px-2 w-full gap-2">
        {voiceState === 'SPEAKING' && (
          <h2 className="text-lg sm:text-2xl font-semibold text-foreground animate-pulse">
            {systemMessage}
          </h2>
        )}
        {voiceState === 'LISTENING' && (
          <h2 className="text-lg sm:text-2xl font-semibold text-primary">
            I'm listening...
          </h2>
        )}
        {voiceState === 'PROCESSING' && (
          <h2 className="text-lg sm:text-2xl font-semibold text-muted-foreground">
            Thinking...
          </h2>
        )}
        {voiceState === 'IDLE' && systemMessage && (
          <>
            <h2 className="text-lg sm:text-2xl font-semibold text-foreground">
              {systemMessage}
            </h2>
            {!autoReadResponses && (
              <Button variant="ghost" size="sm" onClick={manualSpeak} className="rounded-full text-muted-foreground">
                 <Volume2 className="w-4 h-4 mr-2" /> Read Aloud
              </Button>
            )}
          </>
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
      <div className="flex gap-2 sm:gap-4 flex-shrink-0 mt-auto w-full justify-center pb-20 sm:pb-24">
        {voiceState === 'IDLE' ? (
          <Button className="rounded-full h-9 sm:h-12 px-4 sm:px-6 text-xs sm:text-base whitespace-nowrap shadow-sm" onClick={startListening}>
            Tap to Speak
          </Button>
        ) : voiceState === 'LISTENING' ? (
           <Button variant="outline" className="rounded-full h-9 sm:h-12 px-4 sm:px-6 text-xs sm:text-base whitespace-nowrap shadow-sm border-primary/50 text-primary" onClick={stopListening}>
             Pause
           </Button>
        ) : null}
        
        <Button variant="danger" className="rounded-full h-9 sm:h-12 px-4 sm:px-6 text-xs sm:text-base whitespace-nowrap shadow-sm" onClick={handleEndTriage}>
          End Triage
        </Button>
      </div>
      
      </div>
    </div>
  )
}
