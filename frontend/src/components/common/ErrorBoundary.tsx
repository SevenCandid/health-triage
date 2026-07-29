import { AlertTriangle } from 'lucide-react'
import { Component, type ErrorInfo, type ReactNode } from 'react'
import { motion } from 'framer-motion'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="flex min-h-screen items-center justify-center bg-background p-4">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-md rounded-xl border border-border bg-card p-8 text-center shadow-lg"
          >
            <div className="mb-4 text-5xl"><AlertTriangle className="w-4 h-4" />️</div>
            <h1 className="mb-2 text-xl font-semibold text-foreground">Something went wrong</h1>
            <p className="mb-6 text-sm text-muted-foreground">
              {this.state.error?.message ?? 'An unexpected error occurred. Please try again.'}
            </p>
            <button
              id="error-boundary-reload-btn"
              onClick={() => window.location.reload()}
              className="rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground transition hover:opacity-90"
            >
              Reload Page
            </button>
          </motion.div>
        </div>
      )
    }

    return this.props.children
  }
}
