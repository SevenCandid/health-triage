import React from 'react'
import { Mic, HelpCircle, Circle, X, AlertTriangle, Stethoscope, Hand } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { assessmentApi, profileApi, authApi } from '@/services/api'
import { useNetworkStore } from '@/stores/network-store'
import { useAuthStore } from '@/stores/auth-store'
import { Card } from '@/components/ui/Card'
import { PageLoader } from '@/components/common/LoadingSpinner'
import type { AssessmentSession } from '@/types'
import { ChevronRight, PhoneCall, History, User, BarChart2 } from 'lucide-react'

// ── Animation Helper ──────────────────────────────────────────────────────────

function FadeIn({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  )
}

// ── Quick Action Card Component ───────────────────────────────────────────────

function QuickAction({ icon: Icon, label, description, onClick }: {
  icon: React.ComponentType<any>
  label: string
  description: string
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="text-left w-full border border-border/80 bg-card hover:bg-accent/40 rounded-xl p-3.5 flex items-center justify-between shadow-sm transition-all hover:-translate-y-0.5 active:scale-[0.98]"
    >
      <div className="flex items-center gap-3 min-w-0">
        <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center text-primary flex-shrink-0">
          <Icon className="h-4.5 w-4.5" />
        </div>
        <div className="min-w-0">
          <h3 className="text-xs font-bold text-foreground leading-snug">{label}</h3>
          <p className="text-[10px] text-muted-foreground truncate leading-normal">{description}</p>
        </div>
      </div>
      <ChevronRight className="h-4 w-4 text-muted-foreground flex-shrink-0" />
    </button>
  )
}

// ── Main Dashboard ─────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const navigate = useNavigate()
  const { isOnline } = useNetworkStore()
  const { userRole, profileCompleted } = useAuthStore()

  // Fetch registered user credentials (for greeting)
  const { data: authData, isLoading: authLoading } = useQuery({
    queryKey: ['authProfile'],
    queryFn: () => authApi.getProfile(),
    staleTime: 30_000,
    enabled: userRole !== 'GUEST',
  })

  // Fetch health profile details
  const { data: profileData, isLoading: profileLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      try {
        return await profileApi.getProfile()
      } catch (err: any) {
        if (err?.response?.status === 404) return null
        throw err
      }
    },
    retry: false,
    staleTime: 30_000,
    enabled: userRole !== 'GUEST' && profileCompleted,
  })

  // Fetch assessment history (to find most recent assessment)
  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['assessmentHistory'],
    queryFn: async () => {
      try {
        return await assessmentApi.getHistory(1, 10)
      } catch {
        return null
      }
    },
    retry: false,
    staleTime: 15_000,
    enabled: userRole !== 'GUEST',
  })

  const sessions: AssessmentSession[] = useMemo(() => historyData?.data?.items ?? [], [historyData])
  const completedSessions = useMemo(() => sessions.filter(s => s.status === 'COMPLETED'), [sessions])
  
  // Find the single most recent completed assessment
  const lastSession = useMemo(() => {
    if (!completedSessions.length) return null
    return [...completedSessions].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0]
  }, [completedSessions])

  // Fetch detail for last session to get severity and recommendations
  const { data: lastSessionResultData, isLoading: lastSessionResultLoading } = useQuery({
    queryKey: ['lastSessionResult', lastSession?.id],
    queryFn: () => assessmentApi.getResult(lastSession!.id),
    enabled: !!lastSession?.id,
    retry: false,
  })

  const profile = profileData?.data
  const authUser = authData?.data

  const [bannerDismissed, setBannerDismissed] = useState(false)
  const showProfileBanner = userRole !== 'GUEST' && !profileCompleted && !bannerDismissed

  if (authLoading || profileLoading || historyLoading || lastSessionResultLoading) return <PageLoader />

  // Extract First Name
  const rawName = profile?.full_name || authUser?.full_name || ''
  const firstName = rawName ? rawName.trim().split(' ')[0] : 'Guest'

  const RISK_COLORS: Record<string, React.ReactNode | string> = {
    LOW: 'bg-green-500/10 text-green-600 border-green-500/20',
    GREEN: 'bg-green-500/10 text-green-600 border-green-500/20',
    MEDIUM: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20',
    YELLOW: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20',
    HIGH: 'bg-orange-500/10 text-orange-600 border-orange-500/20',
    ORANGE: 'bg-orange-500/10 text-orange-600 border-orange-500/20',
    EMERGENCY: 'bg-red-500/10 text-red-600 border-red-500/20 animate-pulse',
    RED: 'bg-red-500/10 text-red-600 border-red-500/20 animate-pulse',
  }

  const RISK_EMOJIS: Record<string, React.ReactNode | string> = {
    LOW: <Circle className="w-4 h-4" />,
    GREEN: <Circle className="w-4 h-4" />,
    MEDIUM: <Circle className="w-4 h-4" />,
    YELLOW: <Circle className="w-4 h-4" />,
    HIGH: '🟠',
    ORANGE: '🟠',
    EMERGENCY: <Circle className="w-4 h-4" />,
    RED: <Circle className="w-4 h-4" />,
  }

  return (
    <div className="mx-auto max-w-2xl px-3 pt-3 pb-24 space-y-4">

      {/* ── Profile Setup Alert ────────────────────────────────── */}
      {showProfileBanner && (
        <motion.div
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-700 dark:text-amber-400"
        >
          <div className="flex items-center gap-1.5">
            <span><AlertTriangle className="w-4 h-4" />️</span>
            <span>Profile incomplete — triage accuracy may be reduced.</span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button onClick={() => navigate('/profile')} className="font-semibold underline underline-offset-2 hover:opacity-80">
              Set up
            </button>
            <button onClick={() => setBannerDismissed(true)} className="opacity-50 hover:opacity-100 font-bold" aria-label="Dismiss"><X className="w-4 h-4" /></button>
          </div>
        </motion.div>
      )}

      {/* ── Welcome Greeting ───────────────────────────────────── */}
      <FadeIn>
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-xl font-extrabold text-foreground tracking-tight">
              Hello, {firstName}
            </h1>
            <p className="text-xs text-muted-foreground mt-0.5">How are you feeling today?</p>
          </div>
          <div className={`flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full ${isOnline ? 'bg-green-500/10 text-green-600' : 'bg-yellow-500/10 text-yellow-600'}`}>
            <div className={`h-1 w-1 rounded-full ${isOnline ? 'bg-green-500' : 'bg-yellow-500'}`} />
            {isOnline ? 'Online' : 'Offline'}
          </div>
        </div>
      </FadeIn>

      {/* ── Large Assess CTA Buttons ───────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <FadeIn delay={0.05}>
          <button
            onClick={() => navigate('/assessment')}
            className="text-left w-full h-full bg-gradient-to-br from-primary to-primary/80 hover:from-primary/95 hover:to-primary/75 text-primary-foreground rounded-xl p-4 shadow-md hover:shadow-lg transition-all flex flex-col justify-between min-h-[100px] group active:scale-[0.98]"
          >
            <span className="text-2xl bg-white/10 h-10 w-10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform mb-3"><Stethoscope className="w-4 h-4" /></span>
            <div>
              <h2 className="text-sm font-bold leading-tight">Start Health Assessment</h2>
              <p className="text-[11px] text-primary-foreground/80 mt-0.5 leading-snug">Interactive symptom triage assistant</p>
            </div>
          </button>
        </FadeIn>

        <FadeIn delay={0.08}>
          <button
            onClick={() => navigate('/voice')}
            className="text-left w-full h-full bg-gradient-to-br from-accent/90 to-accent/70 hover:from-accent hover:to-accent/60 text-accent-foreground rounded-xl p-4 shadow-md hover:shadow-lg transition-all flex flex-col justify-between min-h-[100px] group active:scale-[0.98]"
          >
            <span className="text-2xl bg-black/10 h-10 w-10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform mb-3"><Mic className="w-4 h-4" /></span>
            <div>
              <h2 className="text-sm font-bold leading-tight">Start Voice Assessment</h2>
              <p className="text-[11px] text-accent-foreground/80 mt-0.5 leading-snug">Hands-free voice triage session</p>
            </div>
          </button>
        </FadeIn>
      </div>

      {/* ── Quick Actions ──────────────────────────────────────── */}
      <FadeIn delay={0.12}>
        <div className="space-y-2">
          <h2 className="text-xs font-bold text-foreground/80 uppercase tracking-wider">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <QuickAction
              icon={PhoneCall}
              label="Emergency Centre"
              description="Get instant help & contact dispatch"
              onClick={() => navigate('/emergency')}
            />
            <QuickAction
              icon={History}
              label="Health Conversations"
              description="View your past triage sessions"
              onClick={() => navigate('/history')}
            />
            <QuickAction
              icon={User}
              label="My Profile"
              description="Manage health history & preferences"
              onClick={() => navigate('/profile')}
            />
            <QuickAction
              icon={BarChart2}
              label="Health Insights"
              description="View health charts & analytics"
              onClick={() => navigate('/insights')}
            />
          </div>
        </div>
      </FadeIn>

      {/* ── Recent Assessment ──────────────────────────────────── */}
      <FadeIn delay={0.18}>
        <div className="space-y-2">
          <h2 className="text-xs font-bold text-foreground/80 uppercase tracking-wider">Recent Assessment</h2>
          {lastSession ? (
            <Card
              hover
              onClick={() => navigate(`/assessment/${lastSession.id}/result`)}
              className="flex items-center justify-between gap-4 p-4 border border-border bg-card cursor-pointer shadow-sm"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-foreground">
                    {new Date(lastSession.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
                  </span>
                  {lastSessionResultData?.data && (
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${RISK_COLORS[lastSessionResultData.data.severity] || 'bg-muted'}`}>
                      {RISK_EMOJIS[lastSessionResultData.data.severity] || <HelpCircle className="w-4 h-4" />} {lastSessionResultData.data.severity}
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground mt-1 truncate">
                  Recommendation: {lastSessionResultData?.data?.recommendations?.[0] || 'Monitor symptoms'}
                </p>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground shrink-0" />
            </Card>
          ) : (
            <Card className="text-center p-8 border border-border/60 bg-gradient-to-b from-card to-muted/10 shadow-sm flex flex-col items-center justify-center">
              <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center mb-3">
                <p className="text-xl"><Hand className="w-4 h-4" /></p>
              </div>
              <p className="text-xs font-semibold text-foreground">No recent conversations</p>
              <p className="text-[11px] text-muted-foreground mt-1">When you complete an assessment, your recommendations will appear here.</p>
            </Card>
          )}
        </div>
      </FadeIn>

    </div>
  )
}
