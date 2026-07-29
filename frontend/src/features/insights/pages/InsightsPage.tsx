import React from 'react'
import { CheckCircle2, BarChart2 } from 'lucide-react'
import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { assessmentApi } from '@/services/api'
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
  icon: React.ReactNode | string; label: string; value: string | number; color?: string
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
  const monthlyMap: Record<string, { month: string; total: number }> = {}
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const label = d.toLocaleDateString('en-US', { month: 'short' })
    monthlyMap[label] = { month: label, total: 0 }
  }

  completed.forEach(s => {
    const sDate = new Date(s.created_at)
    const label = sDate.toLocaleDateString('en-US', { month: 'short' })
    if (monthlyMap[label]) {
      monthlyMap[label].total += 1
    }
  })

  return {
    totalSessions: sessions.length,
    completedCount: completed.length,
    monthlyTrend: Object.values(monthlyMap),
  }
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function InsightsPage() {
  const navigate = useNavigate()
  const { userRole, profileCompleted } = useAuthStore()

  // Fetch assessment history
  const { data: historyData, isLoading } = useQuery({
    queryKey: ['assessmentHistory'],
    queryFn: () => assessmentApi.getHistory(1, 100),
    staleTime: 15_000,
    enabled: userRole !== 'GUEST' && profileCompleted,
  })

  const sessions = useMemo(() => historyData?.data?.items ?? [], [historyData])
  const stats = useMemo(() => deriveStats(sessions), [sessions])

  if (isLoading) return <PageLoader />

  return (
    <div className="mx-auto max-w-2xl px-3 pt-3 pb-20 space-y-4">
      {/* Header */}
      <FadeIn>
        <div className="flex items-center justify-between gap-2">
          <div>
            <h1 className="text-xl font-extrabold text-foreground">Health Insights</h1>
            <p className="text-xs text-muted-foreground">Historical analytics & risk distribution</p>
          </div>
          <Button variant="outline" size="sm" onClick={() => navigate('/dashboard')}>
            ← Back Home
          </Button>
        </div>
      </FadeIn>

      {/* Stat Cards */}
      <FadeIn delay={0.05}>
        <div className="grid grid-cols-2 gap-2">
          <StatCard icon=<BarChart2 className="w-4 h-4" /> label="Total Sessions" value={stats.totalSessions} color="bg-blue-500/10" />
          <StatCard icon=<CheckCircle2 className="w-4 h-4" /> label="Completed" value={stats.completedCount} color="bg-green-500/10" />
        </div>
      </FadeIn>

      {/* Charts */}
      {sessions.length > 0 ? (
        <div className="space-y-4">
          {/* Monthly Trend Chart */}
          <FadeIn delay={0.1}>
            <Card>
              <h2 className="text-xs font-bold text-foreground mb-3 uppercase tracking-wider">Triage Trend</h2>
              <div className="h-44 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={stats.monthlyTrend} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                    <defs>
                      <linearGradient id="totalColor" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.2} />
                        <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                    <XAxis dataKey="month" tickLine={false} axisLine={false} style={{ fontSize: 9, fill: 'var(--muted-foreground)' }} />
                    <YAxis tickLine={false} axisLine={false} style={{ fontSize: 9, fill: 'var(--muted-foreground)' }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="total" name="Total Sessions" stroke="var(--primary)" strokeWidth={1.5} fillOpacity={1} fill="url(#totalColor)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </FadeIn>

        </div>
      ) : (
        <Card className="text-center py-12">
          <p className="text-3xl mb-2"><BarChart2 className="w-4 h-4" /></p>
          <h3 className="font-semibold text-foreground">No insights available</h3>
          <p className="text-xs text-muted-foreground mt-1">Complete symptom assessments to generate health analytics.</p>
        </Card>
      )}
    </div>
  )
}
