import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { assessmentApi } from '@/services/api'
import { useAssessmentStore } from '@/stores/assessment-store'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { Button } from '@/components/ui/Button'
import { useAuthStore } from '@/stores/auth-store'
import { Card } from '@/components/ui/Card'

// ── Risk level config ────────────────────────────────────────────────────────

interface RiskConfig {
  emoji: string
  label: string
  sublabel: string
  gradient: string          // hero gradient classes
  ring: string              // card border
  badgeBg: string           // inline badge
  badgeText: string
  iconBg: string
  pulseColor: string
  accentBar: string         // coloured top bar
}

const RISK: Record<string, RiskConfig> = {
  GREEN: {
    emoji: '🟢',
    label: 'Low Risk',
    sublabel: 'Monitor at home — no immediate care needed',
    gradient: 'from-emerald-500 to-teal-600',
    ring: 'border-emerald-400/40',
    badgeBg: 'bg-emerald-500/15',
    badgeText: 'text-emerald-600 dark:text-emerald-400',
    iconBg: 'bg-emerald-500/20',
    pulseColor: 'bg-emerald-400',
    accentBar: 'bg-gradient-to-r from-emerald-500 to-teal-500',
  },
  LOW: {
    emoji: '🟢',
    label: 'Low Risk',
    sublabel: 'Monitor at home — no immediate care needed',
    gradient: 'from-emerald-500 to-teal-600',
    ring: 'border-emerald-400/40',
    badgeBg: 'bg-emerald-500/15',
    badgeText: 'text-emerald-600 dark:text-emerald-400',
    iconBg: 'bg-emerald-500/20',
    pulseColor: 'bg-emerald-400',
    accentBar: 'bg-gradient-to-r from-emerald-500 to-teal-500',
  },
  YELLOW: {
    emoji: '🟡',
    label: 'Moderate Risk',
    sublabel: 'Schedule a clinic visit within 24–48 hours',
    gradient: 'from-amber-400 to-orange-500',
    ring: 'border-amber-400/40',
    badgeBg: 'bg-amber-500/15',
    badgeText: 'text-amber-700 dark:text-amber-400',
    iconBg: 'bg-amber-400/20',
    pulseColor: 'bg-amber-400',
    accentBar: 'bg-gradient-to-r from-amber-400 to-orange-400',
  },
  MEDIUM: {
    emoji: '🟡',
    label: 'Moderate Risk',
    sublabel: 'Schedule a clinic visit within 24–48 hours',
    gradient: 'from-amber-400 to-orange-500',
    ring: 'border-amber-400/40',
    badgeBg: 'bg-amber-500/15',
    badgeText: 'text-amber-700 dark:text-amber-400',
    iconBg: 'bg-amber-400/20',
    pulseColor: 'bg-amber-400',
    accentBar: 'bg-gradient-to-r from-amber-400 to-orange-400',
  },
  ORANGE: {
    emoji: '🟠',
    label: 'High Risk',
    sublabel: 'See a doctor today — do not delay',
    gradient: 'from-orange-500 to-red-500',
    ring: 'border-orange-400/40',
    badgeBg: 'bg-orange-500/15',
    badgeText: 'text-orange-600 dark:text-orange-400',
    iconBg: 'bg-orange-400/20',
    pulseColor: 'bg-orange-400',
    accentBar: 'bg-gradient-to-r from-orange-500 to-red-400',
  },
  HIGH: {
    emoji: '🟠',
    label: 'High Risk',
    sublabel: 'See a doctor today — do not delay',
    gradient: 'from-orange-500 to-red-500',
    ring: 'border-orange-400/40',
    badgeBg: 'bg-orange-500/15',
    badgeText: 'text-orange-600 dark:text-orange-400',
    iconBg: 'bg-orange-400/20',
    pulseColor: 'bg-orange-400',
    accentBar: 'bg-gradient-to-r from-orange-500 to-red-400',
  },
  RED: {
    emoji: '🔴',
    label: 'Emergency',
    sublabel: 'Call emergency services immediately',
    gradient: 'from-red-600 to-rose-700',
    ring: 'border-red-500/60',
    badgeBg: 'bg-red-500/15',
    badgeText: 'text-red-600 dark:text-red-400',
    iconBg: 'bg-red-500/20',
    pulseColor: 'bg-red-500',
    accentBar: 'bg-gradient-to-r from-red-600 to-rose-600',
  },
  EMERGENCY: {
    emoji: '🔴',
    label: 'Emergency',
    sublabel: 'Call emergency services immediately',
    gradient: 'from-red-600 to-rose-700',
    ring: 'border-red-500/60',
    badgeBg: 'bg-red-500/15',
    badgeText: 'text-red-600 dark:text-red-400',
    iconBg: 'bg-red-500/20',
    pulseColor: 'bg-red-500',
    accentBar: 'bg-gradient-to-r from-red-600 to-rose-600',
  },
}

// ── Fade-in staggered wrapper ─────────────────────────────────────────────────

function Section({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  )
}

// ── Divider ───────────────────────────────────────────────────────────────────

function Divider() {
  return <div className="h-px bg-border/60 my-1" />
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function AssessmentResultPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const resetSession = useAssessmentStore((s) => s.resetSession)
  const { userRole, clearAuth } = useAuthStore()

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['assessmentResult', sessionId],
    queryFn: () => assessmentApi.getResult(sessionId!),
    enabled: !!sessionId,
    retry: 2,
  })

  useEffect(() => {
    if (data?.data) useAssessmentStore.getState().setResult(data.data)
  }, [data])

  if (isLoading) return <PageLoader />

  if (isError || !data) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-4 text-center">
        <p className="text-4xl">⚠️</p>
        <p className="text-base font-semibold text-foreground">Result Unavailable</p>
        <p className="text-sm text-muted-foreground">We couldn't load your assessment result.</p>
        <div className="flex gap-2 mt-2">
          <Button size="sm" onClick={() => refetch()}>Retry</Button>
          <Button size="sm" variant="outline" onClick={() => navigate('/dashboard')}>Dashboard</Button>
        </div>
      </div>
    )
  }

  const result = data.data
  const severity = result.severity ?? 'GREEN'
  const cfg = RISK[severity] ?? RISK['GREEN']
  const isEmergency = result.is_emergency || severity === 'RED' || severity === 'EMERGENCY'

  const currentSymptoms = useAssessmentStore((s) => s.currentSymptoms)
  const symptomName = currentSymptoms[0] || 'General Health Concern'
  const symptomSlug = symptomName.toLowerCase().replace(/\s+/g, '-')

  const SYMPTOM_INFO: Record<string, string> = {
    'headache': 'Headaches can range from mild tension to severe migraines. Common triggers include stress, dehydration, fatigue, or eye strain.',
    'fever': 'A fever is a temporary increase in body temperature, often due to an illness or infection. It is a sign that your body is fighting off something.',
    'cough': 'Coughing is a natural reflex to protect your airways from irritants, infections, or fluids.',
    'chest-pain': 'Chest pain can have various causes, ranging from muscle strain or acid reflux to serious heart conditions.',
    'shortness-of-breath': 'Difficulty breathing can be related to physical exertion, anxiety, asthma, or respiratory infections.',
  }
  const generalInfo = SYMPTOM_INFO[symptomSlug] || 'If you are experiencing new or changing symptoms, it is helpful to monitor their severity and consult a professional if they persist.'

  // Parse explanation into bullet-point reasons
  const reasons = result.explanation
    ? result.explanation
        .split(/[.•\n]/)
        .map((s: string) => s.trim())
        .filter((s: string) => s.length > 8)
        .slice(0, 5)
    : []

  const handleStartNew = () => {
    resetSession()
    navigate('/assessment')
  }

  return (
    <div className="mx-auto max-w-md px-3 pt-3 pb-24 space-y-4">

      {/* 🩺 Reusable Health Guidance Disclaimer */}
      <Section delay={0}>
        <Card className="border-blue-500/20 bg-blue-500/5 p-4 flex gap-3 items-start text-left rounded-2xl">
          <span className="text-xl">🩺</span>
          <div>
            <p className="text-xs font-bold text-foreground mb-1">Health Guidance Disclaimer</p>
            <p className="text-xs text-muted-foreground leading-relaxed">
              This assessment provides health guidance based on the information you share. It is not a medical diagnosis and does not replace care from a qualified healthcare professional.
            </p>
          </div>
        </Card>
      </Section>

      {/* ── Hero Risk Card ─────────────────────────────────────── */}
      <Section delay={0.05}>
        <div className={`relative rounded-2xl overflow-hidden border-2 ${cfg.ring} shadow-lg`}>
          {/* Top gradient banner */}
          <div className={`bg-gradient-to-br ${cfg.gradient} px-5 py-6 flex flex-col items-center text-center text-white`}>
            {/* Pulsing ring + emoji */}
            <div className="relative mb-3">
              <div className={`absolute inset-0 rounded-full ${cfg.pulseColor} opacity-30 animate-ping`} style={{ animationDuration: '2s' }} />
              <div className={`relative h-16 w-16 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-4xl shadow-inner`}>
                {cfg.emoji}
              </div>
            </div>

            <p className="text-xs font-semibold uppercase tracking-widest opacity-80 mb-1">
              Assessment Summary
            </p>
            <h1 className="text-2xl font-extrabold tracking-tight">{cfg.label}</h1>
            <p className="text-sm opacity-85 mt-1 font-medium">{cfg.sublabel}</p>

            {/* Date */}
            {result.conducted_at && (
              <p className="text-[11px] opacity-60 mt-3">
                {new Date(result.conducted_at).toLocaleDateString('en-GB', {
                  weekday: 'short', day: 'numeric', month: 'long', year: 'numeric',
                })} · {new Date(result.conducted_at).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}
              </p>
            )}
          </div>

          {/* Risk meter bar */}
          <div className="h-1.5 w-full bg-muted">
            <motion.div
              className={`h-full ${cfg.accentBar}`}
              initial={{ width: 0 }}
              animate={{
                width: severity === 'GREEN' || severity === 'LOW' ? '25%'
                     : severity === 'YELLOW' || severity === 'MEDIUM' ? '50%'
                     : severity === 'ORANGE' || severity === 'HIGH' ? '75%'
                     : '100%'
              }}
              transition={{ duration: 0.8, delay: 0.3, ease: 'easeOut' }}
            />
          </div>
        </div>
      </Section>

      {/* ── 1. What We Understood ───────────────────────────────── */}
      <Section delay={0.1}>
        <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden p-4 space-y-1">
          <h2 className="text-xs font-bold text-foreground flex items-center gap-1.5 uppercase tracking-wider">
            💬 1. What We Understood
          </h2>
          <p className="text-sm text-muted-foreground">
            Reported Symptom: <span className="font-semibold text-foreground">{symptomName}</span>
          </p>
        </div>
      </Section>

      {/* ── 2. General Information ──────────────────────────────── */}
      <Section delay={0.15}>
        <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden p-4 space-y-1">
          <h2 className="text-xs font-bold text-foreground flex items-center gap-1.5 uppercase tracking-wider">
            📖 2. General Information
          </h2>
          <p className="text-xs text-muted-foreground leading-relaxed">{generalInfo}</p>
        </div>
      </Section>

      {/* ── 3. Why this recommendation was chosen ───────────────── */}
      {reasons.length > 0 && (
        <Section delay={0.2}>
          <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-muted/30">
              <span className="text-sm">🔬</span>
              <h2 className="text-xs font-bold text-foreground uppercase tracking-wider">3. Why this recommendation was chosen</h2>
            </div>
            <div className="px-4 py-3 space-y-2">
              {reasons.map((reason: string, i: number) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.25 + i * 0.06 }}
                  className="flex items-start gap-2"
                >
                  <span className={`mt-1.5 h-1.5 w-1.5 rounded-full flex-shrink-0 ${cfg.pulseColor}`} />
                  <p className="text-xs text-muted-foreground leading-relaxed">{reason}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </Section>
      )}

      {reasons.length === 0 && result.explanation && (
        <Section delay={0.2}>
          <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-muted/30">
              <span className="text-sm">🔬</span>
              <h2 className="text-xs font-bold text-foreground uppercase tracking-wider">3. Why this recommendation was chosen</h2>
            </div>
            <p className="px-4 py-3 text-xs text-muted-foreground leading-relaxed">{result.explanation}</p>
          </div>
        </Section>
      )}

      {/* ── 4. General self-care suggestions ───────────────────── */}
      {result.recommendations?.length > 0 && (
        <Section delay={0.25}>
          <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-muted/30">
              <span className="text-sm">🩹</span>
              <h2 className="text-xs font-bold text-foreground uppercase tracking-wider">4. General Self-Care Suggestions</h2>
            </div>
            <div className="divide-y divide-border/60">
              {result.recommendations.map((rec: string, i: number) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.15 + i * 0.07 }}
                  className="flex items-start gap-3 px-4 py-3"
                >
                  <span className="mt-0.5 text-sm flex-shrink-0">
                    {i === 0 ? '✅' : i === 1 ? '💧' : i === 2 ? '🛏️' : i === 3 ? '📅' : '🩺'}
                  </span>
                  <p className="text-xs text-foreground leading-snug">{rec}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </Section>
      )}

      {/* ── 5. Warning signs to watch for ──────────────────────── */}
      <Section delay={0.3}>
        <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden p-4 space-y-1.5">
          <h2 className="text-xs font-bold text-foreground flex items-center gap-1.5 uppercase tracking-wider">
            ⚠️ 5. Warning Signs to Watch For
          </h2>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Please seek immediate medical attention if you experience difficulty breathing, sudden severe pain, chest tightness, high fever resistant to medication, sudden confusion, or loss of consciousness.
          </p>
        </div>
      </Section>

      {/* Guest Signup Promotion */}
      {userRole === 'GUEST' && (
        <Section delay={0.32}>
          <Card className="border-primary/30 bg-primary/5 text-center p-5 space-y-3 rounded-2xl">
            <p className="text-2xl">✨</p>
            <p className="text-xs font-bold text-foreground leading-relaxed">
              Create a free account to save this assessment and track your health over time.
            </p>
            <div className="flex gap-2 justify-center pt-1">
              <Button size="sm" onClick={() => { clearAuth(); navigate('/register') }} className="text-xs font-bold px-3 py-1.5 h-8">
                Create Account
              </Button>
              <Button variant="outline" size="sm" onClick={() => { clearAuth(); navigate('/login') }} className="text-xs font-semibold px-3 py-1.5 h-8">
                Sign In
              </Button>
            </div>
          </Card>
        </Section>
      )}

      {/* ── 6. Recommended next steps ──────────────────────────── */}
      <Section delay={0.35}>
        <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-muted/30">
            <span className="text-sm">🗺️</span>
            <h2 className="text-xs font-bold text-foreground uppercase tracking-wider">6. Recommended Next Steps</h2>
          </div>
          <div className="p-3 space-y-2">

            {/* Emergency CTA — only when high risk */}
            {isEmergency && (
              <motion.button
                initial={{ scale: 0.97, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.35 }}
                onClick={() => navigate('/emergency')}
                className="w-full flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 active:scale-[0.98] text-white font-bold text-xs rounded-xl py-3 transition-all shadow-md shadow-red-500/30"
              >
                <span>🚨</span> Call Emergency Services
              </motion.button>
            )}

            {/* Find Hospital */}
            <button
              onClick={() => window.open('https://www.google.com/maps/search/hospital+near+me', '_blank')}
              className="w-full flex items-center justify-center gap-2 border border-border bg-background hover:bg-accent text-foreground font-semibold text-xs rounded-xl py-2.5 transition-all"
            >
              <span>🏥</span> Find Nearby Hospital
            </button>

            {/* Call Doctor (non-emergency) */}
            {!isEmergency && (
              <button
                onClick={() => navigate('/emergency')}
                className="w-full flex items-center justify-center gap-2 border border-border bg-background hover:bg-accent text-foreground font-semibold text-xs rounded-xl py-2.5 transition-all"
              >
                <span>📞</span> Call My Doctor / Contact
              </button>
            )}

            <Divider />

            {/* Start New */}
            <button
              onClick={handleStartNew}
              className={`w-full flex items-center justify-center gap-2 font-semibold text-xs rounded-xl py-2.5 transition-all bg-primary hover:bg-primary/90 text-primary-foreground`}
            >
              <span>🔄</span> Start New Conversation
            </button>
          </div>
        </div>
      </Section>

      {/* ── 7. Continue Conversation ───────────────────────────── */}
      <Section delay={0.4}>
        <Card className="border-border bg-muted/20 p-5 text-center space-y-3 rounded-2xl">
          <p className="text-xs font-semibold text-foreground">Would you like to continue discussing your health?</p>
          <div className="flex gap-2 justify-center">
            <Button onClick={() => navigate(`/assessment?resume=true`)} className="text-xs font-bold px-4 py-2 h-9 rounded-xl">
              Continue Conversation
            </Button>
            <Button variant="outline" onClick={() => navigate('/dashboard')} className="text-xs font-semibold px-4 py-2 h-9 rounded-xl">
              Finish For Now
            </Button>
          </div>
        </Card>
      </Section>

      {/* ── Session ID footer ─────────────────────────────────── */}
      <Section delay={0.45}>
        <p className="text-center text-[9px] text-muted-foreground/45 select-all">
          Conversation ID: {result.session_id}
        </p>
      </Section>

    </div>
  )
}
