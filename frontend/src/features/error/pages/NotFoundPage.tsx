import { Hospital } from 'lucide-react'
import { Link } from 'react-router-dom'
import { EmptyState } from '@/components/common/EmptyState'

export default function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center">
      <EmptyState
        icon=<Hospital className="w-4 h-4" />
        title="Page not found"
        description="The page you are looking for does not exist or has been moved."
      />
      <Link
        to="/dashboard"
        className="mt-4 rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground transition hover:opacity-90"
      >
        Return Home
      </Link>
    </div>
  )
}
