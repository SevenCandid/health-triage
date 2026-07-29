import { HeartPulse, Heart } from 'lucide-react'
import { Outlet } from 'react-router-dom'
import { useTheme } from '@/hooks/use-theme'

/**
 * AuthLayout — minimal shell for login/register pages.
 * No navbar, no tab bar — just a centered card container.
 */
export function AuthLayout() {
  useTheme()

  return (
    <div className="flex min-h-[100dvh] w-full flex-col items-center bg-background p-4">
      <div className="w-full flex flex-col items-center my-auto py-2 sm:py-6">
        <div className="mb-4 flex flex-col items-center gap-1">
          <span className="text-3xl"><HeartPulse className="w-4 h-4" /></span>
          <h1 className="text-xl font-bold tracking-tight text-foreground">Health Triage</h1>
          <p className="text-xs text-muted-foreground text-center">Offline-first clinical triage assistant</p>
        </div>
        <div className="w-full max-w-md">
          <Outlet />
        </div>
      </div>
      
      <footer className="w-full text-center py-4 text-xs text-muted-foreground mt-auto shrink-0">
        Made with <Heart className="w-4 h-4" />️ by SEVEN
      </footer>
    </div>
  )
}
