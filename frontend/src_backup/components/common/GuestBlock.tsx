import { useNavigate } from 'react-router-dom'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useAuthStore } from '@/stores/auth-store'

interface GuestBlockProps {
  featureName: string
  icon?: string
}

export function GuestBlock({ featureName, icon = '🔒' }: GuestBlockProps) {
  const navigate = useNavigate()
  const { clearAuth } = useAuthStore()

  const handleAction = (to: '/login' | '/register') => {
    clearAuth() // Clear guest state
    navigate(to)
  }

  return (
    <div className="mx-auto max-w-sm px-4 py-8 flex flex-col items-center justify-center min-h-[50vh]">
      <Card className="text-center p-6 space-y-4 border border-border shadow-xl">
        <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-2xl mx-auto">
          {icon}
        </div>
        <div className="space-y-1">
          <h2 className="text-base font-bold text-foreground">Sign Up to Access {featureName}</h2>
          <p className="text-xs text-muted-foreground leading-relaxed">
            You are currently in Preview Mode. Please create an account or sign in to access personalized features.
          </p>
        </div>
        <div className="flex flex-col gap-2 pt-2">
          <Button onClick={() => handleAction('/register')} className="w-full text-xs py-2.5 font-bold">
            Create Account
          </Button>
          <Button onClick={() => handleAction('/login')} variant="outline" className="w-full text-xs py-2.5 font-semibold">
            Sign In
          </Button>
        </div>
      </Card>
    </div>
  )
}
