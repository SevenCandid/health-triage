import { NavLink } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth-store'
import { cn } from '@/lib/utils'

export const navItems = [
  { to: '/dashboard', label: 'Assess', icon: '🏠' },
  { to: '/insights', label: 'Insights', icon: '📊' },
  { to: '/history', label: 'History', icon: '📜' },
  { to: '/emergency', label: 'Emergency', icon: '🚨' },
  { to: '/profile', label: 'Profile', icon: '👤' },
  { to: '/settings', label: 'Settings', icon: '⚙️' },
]

export function Sidebar() {
  const { isAuthenticated, userRole } = useAuthStore()

  if (!isAuthenticated) return null

  const isGuest = userRole === 'GUEST'
  const activeItems = isGuest
    ? navItems.filter(item => item.to === '/dashboard' || item.to === '/emergency' || item.to === '/settings')
    : navItems

  return (
    <aside className="hidden md:flex w-64 flex-col border-r border-border bg-background/50 backdrop-blur-sm overflow-y-auto py-6 px-4 shrink-0">
      <div className="mb-6 px-2">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Menu</h2>
      </div>
      <ul className="flex flex-col gap-2">
        {activeItems.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200',
                  isActive
                    ? 'bg-primary/10 text-primary shadow-sm ring-1 ring-primary/20'
                    : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                )
              }
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </aside>
  )
}
