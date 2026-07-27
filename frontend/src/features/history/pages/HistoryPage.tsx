import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { assessmentApi } from '@/services/api'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { PageLoader } from '@/components/common/LoadingSpinner'
import type { AssessmentSession } from '@/types'

const STATUS_STYLE: Record<string, string> = {
  COMPLETED: 'bg-green-500/10 text-green-600 border-green-500/20',
  IN_PROGRESS: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
  ABANDONED: 'bg-muted/60 text-muted-foreground border-border',
  SYNCED: 'bg-purple-500/10 text-purple-600 border-purple-500/20',
}

const STATUS_EMOJI: Record<string, string> = {
  COMPLETED: '✅',
  IN_PROGRESS: '🔄',
  ABANDONED: '❌',
  SYNCED: '☁️',
}

const PAGE_SIZE = 20

export default function HistoryPage() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [filter, setFilter] = useState<string>('ALL')

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['assessmentHistory', page],
    queryFn: async () => {
      try {
        return await assessmentApi.getHistory(page, PAGE_SIZE)
      } catch {
        return null
      }
    },
    retry: false,
    staleTime: 30_000,
  })

  const allItems: AssessmentSession[] = data?.data?.items ?? []
  const total: number = data?.data?.total ?? 0

  const filtered = filter === 'ALL'
    ? allItems
    : allItems.filter(s => s.status === filter)

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  if (isLoading) return <PageLoader />

  return (
    <div className="mx-auto max-w-md px-3 pt-3 pb-20 space-y-3">

      {/* Header */}
      <div className="flex items-center gap-2">
        <button onClick={() => navigate(-1)} className="text-muted-foreground hover:text-foreground transition-colors p-1 -ml-1">
          ←
        </button>
        <div className="min-w-0">
          <h1 className="text-base font-bold text-foreground leading-tight">Assessment History</h1>
          <p className="text-[11px] text-muted-foreground">{total} total session{total !== 1 ? 's' : ''}</p>
        </div>
        <Button
          size="sm"
          className="ml-auto text-xs h-7 px-2.5 shrink-0"
          onClick={() => navigate('/assessment')}
        >
          + New
        </Button>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-1.5 overflow-x-auto pb-0.5 -mx-1 px-1">
        {['ALL', 'COMPLETED', 'IN_PROGRESS', 'ABANDONED'].map(f => (
          <button
            key={f}
            onClick={() => { setFilter(f); setPage(1) }}
            className={`shrink-0 text-[11px] font-medium px-2.5 py-1 rounded-full border transition-all ${
              filter === f
                ? 'bg-primary text-primary-foreground border-primary'
                : 'bg-muted/50 text-muted-foreground border-border hover:bg-accent'
            }`}
          >
            {f === 'ALL' ? 'All' : f === 'IN_PROGRESS' ? 'In Progress' : f.charAt(0) + f.slice(1).toLowerCase()}
          </button>
        ))}
      </div>

      {/* Session List */}
      {filtered.length === 0 ? (
        <Card className="p-6 text-center">
          <p className="text-2xl mb-2">📋</p>
          <p className="text-sm font-medium text-foreground">No sessions found</p>
          <p className="text-xs text-muted-foreground mt-1">
            {filter === 'ALL' ? "You haven't done any triage yet." : `No ${filter.toLowerCase()} sessions.`}
          </p>
          {filter === 'ALL' && (
            <Button size="sm" className="mt-3 text-xs h-7 px-3" onClick={() => navigate('/assessment')}>
              Start Triage
            </Button>
          )}
        </Card>
      ) : (
        <Card className="p-0 overflow-hidden">
          <div className="divide-y divide-border">
            {filtered.map((session, i) => {
              const date = new Date(session.created_at)
              const statusStyle = STATUS_STYLE[session.status] ?? STATUS_STYLE.ABANDONED
              const emoji = STATUS_EMOJI[session.status] ?? '🩺'
              return (
                <motion.div
                  key={session.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: i * 0.03 }}
                  className="flex items-center justify-between gap-2 px-3 py-2.5 hover:bg-accent/30 transition-colors"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="h-8 w-8 rounded-full bg-muted/50 flex items-center justify-center text-sm flex-shrink-0">
                      {emoji}
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs font-medium text-foreground">
                        {date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
                      </p>
                      <p className="text-[10px] text-muted-foreground">
                        {date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}
                        {session.consultation_mode ? ` · ${session.consultation_mode.toLowerCase()}` : ''}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full border ${statusStyle}`}>
                      {session.status === 'IN_PROGRESS' ? 'Active' : session.status.charAt(0) + session.status.slice(1).toLowerCase()}
                    </span>
                    {session.status === 'COMPLETED' && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-[10px] h-6 px-1.5"
                        onClick={() => navigate(`/assessment/${session.id}/result`)}
                      >
                        View
                      </Button>
                    )}
                    {session.status === 'IN_PROGRESS' && (
                      <Button
                        size="sm"
                        className="text-[10px] h-6 px-1.5"
                        onClick={() => navigate(`/assessment`)}
                      >
                        Resume
                      </Button>
                    )}
                  </div>
                </motion.div>
              )
            })}
          </div>
        </Card>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between gap-2 pt-1">
          <Button
            variant="outline"
            size="sm"
            className="text-xs h-7 px-2.5"
            disabled={page <= 1 || isFetching}
            onClick={() => setPage(p => p - 1)}
          >
            ← Prev
          </Button>
          <span className="text-[11px] text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            className="text-xs h-7 px-2.5"
            disabled={page >= totalPages || isFetching}
            onClick={() => setPage(p => p + 1)}
          >
            Next →
          </Button>
        </div>
      )}
    </div>
  )
}
