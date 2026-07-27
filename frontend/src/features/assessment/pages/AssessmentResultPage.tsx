import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { assessmentApi } from '@/services/api'
import { useAssessmentStore } from '@/stores/assessment-store'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { URGENCY_STYLES } from '@/types'
import { cn } from '@/lib/utils'

export default function AssessmentResultPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const resetSession = useAssessmentStore((s) => s.resetSession)

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['assessmentResult', sessionId],
    queryFn: () => assessmentApi.getResult(sessionId!),
    enabled: !!sessionId,
    retry: 2
  })

  // Sync result to store for dashboard history tracking if needed
  useEffect(() => {
    if (data?.data) {
      useAssessmentStore.getState().setResult(data.data)
    }
  }, [data])

  if (isLoading) return <PageLoader />

  if (isError || !data) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center md:h-[calc(100vh-6rem)]">
        <EmptyState
          icon="⚠️"
          title="Result Unavailable"
          description="We couldn't load your assessment result. Please check your connection or try again."
          action={{ label: 'Retry', onClick: () => refetch() }}
        />
      </div>
    )
  }

  const result = data.data
  const severity = result.severity ?? 'GREEN'
  const styles = URGENCY_STYLES[severity] ?? URGENCY_STYLES['GREEN']
  const isEmergency = result.is_emergency || severity === 'EMERGENCY' || severity === 'RED'

  const SEVERITY_LABELS: Record<string, string> = {
    RED: '🚨 Emergency — Seek Immediate Care',
    ORANGE: '⚠️ Urgent — See a Doctor Today',
    YELLOW: '🟡 Moderate — Schedule an Appointment',
    GREEN: '✅ Routine — Monitor & Rest',
    EMERGENCY: '🚨 Emergency — Seek Immediate Care',
    HIGH: '⚠️ Urgent — See a Doctor Today',
    MEDIUM: '🟡 Moderate — Schedule an Appointment',
    LOW: '✅ Routine — Monitor & Rest',
  }

  const handleStartNew = () => {
    resetSession()
    navigate('/assessment')
  }

  return (
    <div className="mx-auto max-w-2xl pt-4 sm:pt-8 pb-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      >
        <Card className={cn('overflow-hidden border-2', styles.border)} padding="none">
          {/* Header Banner */}
          <div className={cn('flex flex-col items-center justify-center p-8 text-center text-white', styles.bg)}>
            <div className="mb-4 rounded-full bg-white/20 p-4 shadow-inner">
              <span className="text-4xl">{isEmergency ? '🚨' : '🩺'}</span>
            </div>
            <h1 className="mb-2 text-2xl font-bold tracking-tight">Assessment Complete</h1>
            <p className="mt-2 text-base font-semibold opacity-90">{SEVERITY_LABELS[severity]}</p>
          </div>

          <div className="p-6 sm:p-8 space-y-8">


            {/* Recommendation & Explanation */}
            <div className="space-y-6">
              <div>
                <h3 className="mb-2 text-lg font-semibold text-foreground flex items-center gap-2">
                  <span>💡</span> Recommendation
                </h3>
                <div className="rounded-xl border border-border bg-card p-5 shadow-sm leading-relaxed text-foreground">
                  <ul className="list-disc list-inside space-y-1">
                    {result.recommendations?.map((rec, i) => (
                      <li key={i}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div>
                <h3 className="mb-2 text-lg font-semibold text-foreground flex items-center gap-2">
                  <span>📋</span> Clinical Explanation
                </h3>
                <div className="rounded-xl border border-border bg-accent p-5 text-sm leading-relaxed text-muted-foreground">
                  {result.explanation}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="pt-4 flex flex-col sm:flex-row gap-3">
              <Button 
                variant={isEmergency ? 'danger' : 'primary'} 
                size="lg" 
                className="flex-1"
                onClick={handleStartNew}
              >
                Start New Assessment
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                className="flex-1"
                onClick={() => navigate('/dashboard')}
              >
                Return Home
              </Button>
            </div>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}
