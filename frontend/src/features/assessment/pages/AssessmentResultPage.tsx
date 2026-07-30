import React from 'react'
import { Bed, Microscope, Zap, Circle, Droplets, Hospital, Smartphone, BarChart2, Utensils, AlertTriangle, MessageSquare, Siren, Sparkles, Phone } from 'lucide-react'
import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { assessmentApi, authApi } from '@/services/api'
import { useAssessmentStore } from '@/stores/assessment-store'
import { useNetworkStore } from '@/stores/network-store'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { Button } from '@/components/ui/Button'
import { useAuthStore } from '@/stores/auth-store'
import { Card } from '@/components/ui/Card'
import { AssessmentNotice } from '../components/AssessmentNotice'

// ── Risk level config ────────────────────────────────────────────────────────

interface RiskConfig {
  emoji: React.ReactNode | string
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
    emoji: <Circle className="w-4 h-4" />,
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
    emoji: <Circle className="w-4 h-4" />,
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
    emoji: <Circle className="w-4 h-4" />,
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
    emoji: <Circle className="w-4 h-4" />,
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
    emoji: <Circle className="w-4 h-4" />,
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
    emoji: <Circle className="w-4 h-4" />,
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

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function AssessmentResultPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const { userRole, clearAuth } = useAuthStore()
  const currentSymptoms = useAssessmentStore((s) => s.currentSymptoms)
  const isOnline = useNetworkStore(s => s.isOnline)

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['assessmentResult', sessionId],
    queryFn: () => assessmentApi.getResult(sessionId!),
    enabled: !!sessionId,
    retry: 2,
  })

  useEffect(() => {
    if (data?.data) useAssessmentStore.getState().setResult(data.data)
  }, [data])

  const { data: contactsData } = useQuery({
    queryKey: ['emergencyContacts'],
    queryFn: () => authApi.getEmergencyContacts(),
    enabled: userRole !== 'GUEST',
  })

  if (isLoading) return <PageLoader />

  if (isError || !data) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-4 text-center">
        <p className="text-4xl"><AlertTriangle className="w-4 h-4" />️</p>
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

  const contacts = contactsData?.data || []
  const doctorContact = contacts.find((c: any) => c.relationship_type === 'HEALTHCARE_PROVIDER')
  const emergencyContact = contacts.find((c: any) => c.is_primary && c.relationship_type !== 'HEALTHCARE_PROVIDER') || contacts.find((c: any) => c.relationship_type !== 'HEALTHCARE_PROVIDER')

  const symptomName = currentSymptoms[0] || 'General Health Concern'
  const symptomSlug = (result.symptom_name || symptomName).toLowerCase().replace(/\s+/g, '-')

  const SYMPTOM_INFO: Record<string, React.ReactNode | string> = {
    'headache': 'Headaches are common and may occur for many reasons including dehydration, stress, poor sleep, eye strain, or minor illnesses.',
    'fever': 'Fevers can indicate that the body is responding to an infection. They often resolve with rest, but can sometimes be a sign of conditions requiring attention.',
    'cough': 'Coughs are common respiratory responses that can occur due to viruses, allergies, or environmental irritants.',
    'chest-pain': 'Chest discomfort can happen for a variety of reasons, including acid reflux, muscle strain, stress, or cardiovascular factors.',
    'shortness-of-breath': 'Difficulty breathing may happen with physical exertion, anxiety, asthma, or respiratory conditions.',
  }
  
  // Combine information for all reported symptoms in the current session
  const matchedInfo = currentSymptoms
    .map(sym => SYMPTOM_INFO[sym.toLowerCase().replace(/\s+/g, '-')])
    .filter(Boolean);

  const generalInfo = matchedInfo.length > 0 
    ? matchedInfo.join(' ') 
    : SYMPTOM_INFO[symptomSlug] || 'Symptoms can be triggered by multiple factors, ranging from mild temporary changes to conditions that may need clinical evaluation.'

  // Parse explanation into bullet-point reasons
  const reasons = result.explanation
    ? result.explanation
        .split(/[.•\n]/)
        .map((s: string) => s.trim())
        .filter((s: string) => s.length > 8)
        .slice(0, 5)
    : []


  return (
    <div className="mx-auto max-w-md px-3 pt-3 pb-24 space-y-4">

      {/* <Stethoscope className="w-4 h-4" /> Reusable Assessment Notice Disclaimer */}
      <Section delay={0}>
        <AssessmentNotice />
      </Section>

      {!isOnline && (
        <Section delay={0.02}>
          <div className="rounded-xl bg-amber-500/10 border border-amber-500/20 p-4">
            <p className="text-sm text-amber-700 dark:text-amber-400 font-medium flex items-center gap-2">
              <span className="text-lg"><Zap className="w-4 h-4" /></span>
              Offline Mode Active: Your assessment was processed locally. AI insights will be generated when you reconnect.
            </p>
          </div>
        </Section>
      )}

      {/* ── Hero Completion Status ─────────────────────────────── */}
      <Section delay={0.05}>
        <div className={`relative rounded-2xl overflow-hidden border-2 ${cfg.ring} shadow-lg`}>
          <div className={`bg-gradient-to-br ${cfg.gradient} px-5 py-6 flex flex-col items-center text-center text-white`}>
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

            {isEmergency && doctorContact && (
              <a href={`tel:${doctorContact.phone_number}`} className="mt-4 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur text-white text-xs font-bold transition-colors">
                <Phone className="w-3.5 h-3.5" /> Call my doctor
              </a>
            )}

            {result.conducted_at && (
              <p className="text-[11px] opacity-60 mt-3">
                {new Date(result.conducted_at).toLocaleDateString('en-GB', {
                  weekday: 'short', day: 'numeric', month: 'long', year: 'numeric',
                })} · {new Date(result.conducted_at).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}
              </p>
            )}
          </div>

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

      {/* ── SECTION 1: What We Understood ─────────────────────── */}
      <Section delay={0.1}>
        <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden p-4 space-y-2">
          <h2 className="text-xs font-bold text-foreground flex items-center gap-1.5 uppercase tracking-wider">
            <MessageSquare className="w-4 h-4" /> What We Understood
          </h2>
          <div className="text-xs text-muted-foreground space-y-1">
            <p>Reported Symptom: <span className="font-semibold text-foreground">{result.symptom_name || symptomName}</span></p>
            {result.raw_answers && Object.keys(result.raw_answers).length > 0 && (
              <ul className="space-y-1 pt-1 border-t border-border/40 mt-1">
                {Object.entries(result.raw_answers).map(([key, val]) => (
                  <li key={key} className="list-disc ml-4">
                    <span className="font-medium text-foreground">{key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}:</span> {val}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </Section>

      {/* ── SECTION 2: General Information ────────────────────── */}
      <Section delay={0.15}>
        <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden p-4 space-y-1.5">
          <h2 className="text-xs font-bold text-foreground flex items-center gap-1.5 uppercase tracking-wider">
            📖 General Information
          </h2>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {generalInfo}
          </p>
        </div>
      </Section>

      {/* ── SECTION 3: Why This Recommendation ─────────────────── */}
      <Section delay={0.2}>
        <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-muted/30">
            <span className="text-sm"><Microscope className="w-4 h-4" /></span>
            <h2 className="text-xs font-bold text-foreground uppercase tracking-wider">Why This Recommendation</h2>
          </div>
          <div className="px-4 py-3 space-y-2">
            {reasons.length > 0 ? (
              reasons.map((reason: string, i: number) => (
                <div key={i} className="flex items-start gap-2">
                  <span className={`mt-1.5 h-1.5 w-1.5 rounded-full flex-shrink-0 ${cfg.pulseColor}`} />
                  <p className="text-xs text-muted-foreground leading-relaxed">{reason}</p>
                </div>
              ))
            ) : (
              <p className="text-xs text-muted-foreground leading-relaxed">
                {result.explanation || "Your responses indicate signs that warrant the chosen recommendation to ensure proper health management."}
              </p>
            )}
          </div>
        </div>
      </Section>

      {/* ── SECTION 4: Self-care Suggestions ───────────────────── */}
      <Section delay={0.25}>
        <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-muted/30">
            <span className="text-sm">🩹</span>
            <h2 className="text-xs font-bold text-foreground uppercase tracking-wider">Self-care Suggestions</h2>
          </div>
          <ul className="divide-y divide-border/60">
            <li className="flex items-start gap-3 px-4 py-2 text-xs text-muted-foreground">
              <span className="mt-0.5 text-sm"><Bed className="w-4 h-4" />️</span>
              <p className="leading-snug">Ensure adequate rest to allow the body to recover.</p>
            </li>
            <li className="flex items-start gap-3 px-4 py-2 text-xs text-muted-foreground">
              <span className="mt-0.5 text-sm"><Droplets className="w-4 h-4" /></span>
              <p className="leading-snug">Maintain hydration by drinking clear fluids regularly.</p>
            </li>
            <li className="flex items-start gap-3 px-4 py-2 text-xs text-muted-foreground">
              <span className="mt-0.5 text-sm"><Utensils className="w-4 h-4" /></span>
              <p className="leading-snug">Eat balanced, healthy meals to support immune function.</p>
            </li>
            <li className="flex items-start gap-3 px-4 py-2 text-xs text-muted-foreground">
              <span className="mt-0.5 text-sm"><Smartphone className="w-4 h-4" /></span>
              <p className="leading-snug">Avoid excessive screen time to reduce eye strain and fatigue.</p>
            </li>
            <li className="flex items-start gap-3 px-4 py-2 text-xs text-muted-foreground">
              <span className="mt-0.5 text-sm"><BarChart2 className="w-4 h-4" /></span>
              <p className="leading-snug">Monitor your symptoms closely and note any changes or worsening trends.</p>
            </li>
          </ul>
        </div>
      </Section>

      {/* ── SECTION 5: Warning Signs ────────────────────────────── */}
      <Section delay={0.3}>
        <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden p-4 space-y-1.5">
          <h2 className="text-xs font-bold text-foreground flex items-center gap-1.5 uppercase tracking-wider">
            <AlertTriangle className="w-4 h-4" />️ Warning Signs
          </h2>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Please seek immediate medical attention if you experience key warning signs such as:
          </p>
          <ul className="text-xs text-muted-foreground space-y-1 list-disc pl-4 pt-1">
            <li>Difficulty breathing or severe shortness of breath</li>
            <li>Loss of consciousness or sudden fainting</li>
            <li>Sudden weakness, numbness, or difficulty speaking</li>
            <li>Severe chest pain or tightness</li>
          </ul>
        </div>
      </Section>

      {/* Guest Signup Promotion */}
      {userRole === 'GUEST' && (
        <Section delay={0.32}>
          <Card className="border-primary/30 bg-primary/5 text-center p-5 space-y-3 rounded-2xl">
            <p className="text-2xl"><Sparkles className="w-4 h-4" /></p>
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

      {/* ── SECTION 6: Recommendation ───────────────────────────── */}
      <Section delay={0.35}>
        <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-muted/30">
            <span className="text-sm">📋</span>
            <h2 className="text-xs font-bold text-foreground uppercase tracking-wider">Recommendation</h2>
          </div>
          <div className="p-4 space-y-3">
            <div className={`p-3 rounded-xl bg-gradient-to-br ${cfg.gradient} text-white`}>
              <p className="text-xs font-semibold uppercase tracking-wider opacity-75">Triage Severity</p>
              <h3 className="text-lg font-bold">{cfg.label}</h3>
              <p className="text-xs opacity-90 mt-1">{cfg.sublabel}</p>
            </div>
            
            {result.recommendations?.length > 0 && (
              <div className="space-y-1.5">
                <p className="text-xs font-bold text-foreground">Actions Recommended:</p>
                {result.recommendations.map((rec: string, i: number) => (
                  <p key={i} className="text-xs text-muted-foreground flex gap-2">
                    <span>•</span> <span>{rec}</span>
                  </p>
                ))}
              </div>
            )}

            {isEmergency && (
              <motion.button
                initial={{ scale: 0.97, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                onClick={() => navigate('/emergency')}
                className="w-full flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 active:scale-[0.98] text-white font-bold text-xs rounded-xl py-3 mt-2 transition-all shadow-md shadow-red-500/30"
              >
                <span><Siren className="w-4 h-4" /></span> Call Emergency Services
              </motion.button>
            )}

            {doctorContact && (
              <a
                href={`tel:${doctorContact.phone_number}`}
                className={`w-full flex items-center justify-center gap-2 font-bold text-xs rounded-xl py-2.5 mt-2 transition-all shadow-sm ${
                  isEmergency
                    ? 'bg-red-500 hover:bg-red-600 text-white shadow-red-500/20'
                    : 'bg-primary hover:bg-primary/90 text-white'
                }`}
              >
                <span><Phone className="w-4 h-4" /></span> Call My Doctor ({doctorContact.contact_name})
              </a>
            )}

            {emergencyContact && (
              <a
                href={`tel:${emergencyContact.phone_number}`}
                className={`w-full flex items-center justify-center gap-2 font-bold text-xs rounded-xl py-2.5 mt-2 transition-all shadow-sm border ${
                  isEmergency
                    ? 'border-red-500 text-red-600 hover:bg-red-50'
                    : 'border-border bg-background hover:bg-accent text-foreground'
                }`}
              >
                <span><Phone className="w-4 h-4" /></span> Call Emergency Contact ({emergencyContact.contact_name})
              </a>
            )}

            <button
              onClick={() => navigate('/hospitals')}
              className="w-full flex items-center justify-center gap-2 border border-border bg-background hover:bg-accent text-foreground font-semibold text-xs rounded-xl py-2.5 transition-all mt-2"
            >
              <span><Hospital className="w-4 h-4" /></span> Find Nearby Hospital
            </button>
          </div>
        </div>
      </Section>

      {/* ── SECTION 7: Continue Conversation ───────────────────── */}
      <Section delay={0.4}>
        <Card className="border-border bg-muted/20 p-5 text-center space-y-4 rounded-2xl">
          <p className="text-xs font-semibold text-foreground">Is there anything else you'd like to talk about today?</p>
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
