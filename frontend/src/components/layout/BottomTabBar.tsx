import { ScrollText, Home, User, Siren } from 'lucide-react'
import { NavLink, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/auth-store'

const tabItems = [
  { to: '/dashboard', label: 'Assess', icon: <Home className="w-4 h-4" /> },
  { to: '/history', label: 'History', icon: <ScrollText className="w-4 h-4" /> },
  { to: '/emergency', label: 'Emergency', icon: <Siren className="w-4 h-4" /> },
  { to: '/profile', label: 'Profile', icon: <User className="w-4 h-4" /> },
]

/**
 * Bottom tab bar for mobile navigation (fixed at bottom, hidden on md+).
 * Uses a sliding indicator for the active tab.
 */
export function BottomTabBar() {
  const { pathname } = useLocation()
  const { userRole } = useAuthStore()

  const isGuest = userRole === 'GUEST'
  const activeTabs = isGuest
    ? tabItems.filter(item => item.to === '/dashboard' || item.to === '/emergency')
    : tabItems

  return (
    <nav
      className="fixed bottom-0 inset-x-0 z-40 border-t border-border bg-background/90 backdrop-blur-sm md:hidden"
      aria-label="Mobile navigation"
    >
      <ul className="flex items-center">
        {activeTabs.map((item) => {
          const isActive = pathname.startsWith(item.to)
          return (
            <li key={item.to} className="flex-1">
              <NavLink
                to={item.to}
                id={`tab-${item.label.toLowerCase()}`}
                className="relative flex flex-col items-center gap-0.5 py-1 text-[8px] font-medium"
              >
                {isActive && (
                  <motion.span
                    layoutId="tab-indicator"
                    className="absolute -top-px inset-x-3 h-0.5 rounded-full bg-primary"
                  />
                )}
                <span
                  className={cn(
                    'text-sm transition-transform',
                    isActive ? 'scale-110' : 'scale-100 opacity-60'
                  )}
                >
                  {item.icon}
                </span>
                <span
                  className={cn(
                    'transition-colors',
                    isActive ? 'text-primary' : 'text-muted-foreground'
                  )}
                >
                  {item.label}
                </span>
              </NavLink>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
