import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { assessmentApi, profileApi } from '@/services/api'
import { useNetworkStore } from '@/stores/network-store'
import { useAuthStore } from '@/stores/auth-store'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { PageLoader } from '@/components/common/LoadingSpinner'
import type { AssessmentSession } from '@/types'

// ── Animation wrapper ──────────────────────────────────────────────────────────

function FadeIn({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  )
}

// ── Stat Card ──────────────────────────────────────────────────────────────────

function StatCard({ icon, label, value, color }: {
  icon: string; label: string; value: string | number; color?: string
}) {
  return (
    <Card className="flex items-center gap-2.5 p-3">
      <div className={`h-8 w-8 rounded-lg flex items-center justify-center text-base flex-shrink-0 ${color ?? 'bg-primary/10'}`}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-[11px] text-muted-foreground font-medium leading-none truncate">{label}</p>
        <p className="text-xl font-bold text-foreground mt-0.5 leading-none">{value}</p>
      </div>
    </Card>
  )
}

// ── Custom Tooltip ─────────────────────────────────────────────────────────────

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-md border border-border bg-card px-2.5 py-1.5 shadow-lg text-xs">
      <p className="font-semibold text-foreground mb-0.5">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }}>{p.name}: <strong>{p.value}</strong></p>
      ))}
    </div>
  )
}

// ── Derived analytics ──────────────────────────────────────────────────────────

function deriveStats(sessions: AssessmentSession[]) {
  const completed = sessions.filter(s => s.status === 'COMPLETED')

  const now = new Date()
  const monthlyMap: Record<string, { month: string; total: number; safe: number }> = {}
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const key = d.toLocaleDateString('en-GB', { month: 'short', year: '2-digit' })
    monthlyMap[key] = { month: key, total: 0, safe: 0 }
  }
  completed.forEach(s => {
    const key = new Date(s.created_at).toLocaleDateString('en-GB', { month: 'short', year: '2-digit' })
    if (monthlyMap[key]) { monthlyMap[key].total++; monthlyMap[key].safe++ }
  })
  const monthlyTrend = Object.values(monthlyMap)

  const recent = [...completed]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)

  return {
    monthlyTrend,
    recent,
    totalSessions: sessions.length,
    completedCount: completed.length,
    lastSession: recent[0],
  }
}

// ── Main Dashboard ─────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const navigate = useNavigate()
  const { isOnline } = useNetworkStore()
  const profileCompleted = useAuthStore((s) => s.profileCompleted)

  const { data: historyData, isLoading } = useQuery({
    queryKey: ['assessmentHistory'],
    queryFn: async () => {
      try { return await assessmentApi.getHistory(1, 100) } catch { return null }
    },
    retry: false,
    staleTime: 30_000,
  })

  const { data: profileData } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      try { return await profileApi.getProfile() } catch (err: any) {
        if (err?.response?.status === 404) return null
        throw err
      }
    },
    retry: false,
    staleTime: 30_000,
    enabled: profileCompleted,
  })

  const sessions = useMemo(() => historyData?.data?.items ?? [], [historyData])
  const stats = useMemo(() => deriveStats(sessions), [sessions])
  const profile = profileData?.data

  const [bannerDismissed, setBannerDismissed] = useState(false)
  const showProfileBanner = !profileCompleted && !bannerDismissed

  if (isLoading) return <PageLoader />

  return (
    <div className="mx-auto max-w-2xl px-3 pt-3 pb-20 space-y-3">

      {/* ── Profile Reminder Banner ─────────────────────────── */}
      {showProfileBanner && (
        <motion.div
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-700 dark:text-amber-400"
        >
          <div className="flex items-center gap-1.5">
            <span>⚠️</span>
            <span>Profile incomplete — triage accuracy may be reduced.</span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button onClick={() => navigate('/profile')} className="font-semibold underline underline-offset-2 hover:opacity-80">
              Set up
            </button>
            <button onClick={() => setBannerDismissed(true)} className="opacity-50 hover:opacity-100 font-bold" aria-label="Dismiss">×</button>
          </div>
        </motion.div>
      )}

      {/* ── Header ─────────────────────────────────────────── */}
      <FadeIn>
        <div className="flex items-center justify-between gap-2">
          <div>
            <h1 className="text-lg font-bold text-foreground leading-tight">
              {profile?.full_name ? `Hi, ${profile.full_name.split(' ')[0]} 👋` : 'Dashboard'}
            </h1>
            <p className="text-xs text-muted-foreground">Your health overview</p>
          </div>
          <div className="flex items-center gap-1.5">
            <div className={`flex items-center gap-1 text-[10px] font-medium px-2 py-1 rounded-full ${isOnline ? 'bg-green-500/10 text-green-600' : 'bg-yellow-500/10 text-yellow-600'}`}>
              <div className={`h-1.5 w-1.5 rounded-full ${isOnline ? 'bg-green-500' : 'bg-yellow-500'}`} />
              {isOnline ? 'Online' : 'Offline'}
            </div>
            <Button onClick={() => navigate('/assessment')} size="sm" className="text-xs h-7 px-2.5">💬 Triage</Button>
          </div>
        </div>
      </FadeIn>

      {/* ── Stat Cards ──────────────────────────────────────── */}
      <FadeIn delay={0.05}>
        <div className="grid grid-cols-2 gap-2">
          <StatCard icon="📊" label="Total Sessions" value={stats.totalSessions} color="bg-blue-500/10" />
          <StatCard icon="✅" label="Completed" value={stats.completedCount} color="bg-green-500/10" />
        </div>
      </FadeIn>

      {/* ── Quick Actions ─────────────────────────────────── */}
      <FadeIn delay={0.08}>
        <div className="grid grid-cols-3 gap-2">
          <QuickAction icon="🎙️" label="Voice" onClick={() => navigate('/voice')} />
          <QuickAction icon="🚨" label="Emergency" onClick={() => navigate('/emergency')} color="border-red-500/20 hover:border-red-400" />
          <QuickAction icon="👤" label="Profile" onClick={() => navigate('/profile')} />
        </div>
      </FadeIn>

      {/* ── Assessment Trend Chart ───────────────────────────── */}
      <FadeIn delay={0.1}>
        <Card className="p-3">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-sm font-semibold text-foreground">Assessment Trend</h2>
              <p className="text-[11px] text-muted-foreground">Last 6 months</p>
            </div>
          </div>
          {stats.monthlyTrend.some(m => m.total > 0) ? (
            <ResponsiveContainer width="100%" height={160}>
              <AreaChart data={stats.monthlyTrend} margin={{ top: 4, right: 4, left: -28, bottom: 0 }}>
                <defs>
                  <linearGradient id="gradSafe" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                <XAxis dataKey="month" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} allowDecimals={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="safe" name="Completed" stroke="#22c55e" strokeWidth={1.5} fill="url(#gradSafe)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart message="Complete your first assessment to see trends" />
          )}
        </Card>
      </FadeIn>

      {/* ── Monthly Volume Bar Chart ─────────────────────────── */}
      <FadeIn delay={0.13}>
        <Card className="p-3">
          <h2 className="text-sm font-semibold text-foreground mb-0.5">Monthly Volume</h2>
          <p className="text-[11px] text-muted-foreground mb-3">Sessions per month</p>
          {stats.monthlyTrend.some(m => m.total > 0) ? (
            <ResponsiveContainer width="100%" height={140}>
              <BarChart data={stats.monthlyTrend} margin={{ top: 4, right: 4, left: -28, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                <XAxis dataKey="month" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} allowDecimals={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="total" name="Sessions" radius={[3, 3, 0, 0]} fill="#6366f1" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart message="No assessment data yet" />
          )}
        </Card>
      </FadeIn>

      {/* ── Recent Assessments ───────────────────────────────── */}
      <FadeIn delay={0.16}>
        <Card className="overflow-hidden p-0">
          <div className="flex items-center justify-between px-3 py-2.5 border-b border-border">
            <h2 className="text-sm font-semibold text-foreground">Recent Assessments</h2>
            <Button variant="outline" size="sm" className="text-xs h-6 px-2" onClick={() => navigate('/history')}>All</Button>
          </div>

          {stats.recent.length === 0 ? (
            <div className="py-8 text-center">
              <p className="text-2xl mb-2">📋</p>
              <p className="text-xs text-muted-foreground">No completed assessments yet.</p>
              <div className="flex justify-center gap-2 mt-3">
                <Button size="sm" className="text-xs h-7 px-2.5" onClick={() => navigate('/assessment')}>Start Triage</Button>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-border">
              {stats.recent.map((session) => {
                const date = new Date(session.created_at)
                return (
                  <div key={session.id} className="flex items-center justify-between gap-2 px-3 py-2.5 hover:bg-accent/30 transition-colors">
                    <div className="flex items-center gap-2 min-w-0">
                      <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center text-sm flex-shrink-0">🩺</div>
                      <div className="min-w-0">
                        <p className="text-xs font-medium text-foreground truncate">
                          {date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
                        </p>
                        <p className="text-[10px] text-muted-foreground capitalize">{session.status.toLowerCase()}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-muted/50 text-muted-foreground border border-border capitalize">
                        {session.consultation_mode?.toLowerCase() ?? 'text'}
                      </span>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-[10px] h-6 px-2"
                        onClick={() => navigate(`/assessment/${session.id}/result`)}
                      >
                        View
                      </Button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </Card>
      </FadeIn>

    </div>
  )
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function EmptyChart({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-24 text-center">
      <p className="text-xl mb-1">📊</p>
      <p className="text-xs text-muted-foreground">{message}</p>
    </div>
  )
}

function QuickAction({ icon, label, onClick, color }: {
  icon: string; label: string; onClick: () => void; color?: string
}) {
  return (
    <button
      onClick={onClick}
      className={`flex flex-col items-center justify-center gap-1 rounded-xl border border-border bg-card p-3 hover:bg-accent transition-all ${color ?? ''}`}
    >
      <span className="text-xl leading-none">{icon}</span>
      <span className="text-[11px] font-medium text-foreground">{label}</span>
    </button>
  )
}
