import { useState } from 'react'
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
  const [isCollapsed, setIsCollapsed] = useState(false)

  if (!isAuthenticated) return null

  const isGuest = userRole === 'GUEST'
  const activeItems = isGuest
    ? navItems.filter(item => item.to === '/dashboard' || item.to === '/emergency' || item.to === '/settings')
    : navItems

  return (
    <aside className={cn(
      "hidden md:flex flex-col border-r border-border bg-background/50 backdrop-blur-sm transition-all duration-300 ease-in-out shrink-0 relative",
      isCollapsed ? "w-[72px]" : "w-64"
    )}>
      <div className="flex-1 overflow-y-auto overflow-x-hidden py-6 px-3">
        <div className={cn(
          "mb-6 flex items-center transition-all duration-300 overflow-hidden whitespace-nowrap",
          isCollapsed ? "px-1 justify-center opacity-0 h-0" : "px-3 opacity-100 h-auto"
        )}>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Menu</h2>
        </div>
        
        <ul className="flex flex-col gap-2">
          {activeItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                title={isCollapsed ? item.label : undefined}
                className={({ isActive }) =>
                  cn(
                    'flex items-center rounded-xl py-3 text-sm font-medium transition-all duration-200 overflow-hidden',
                    isCollapsed ? 'justify-center px-0' : 'gap-3 px-3',
                    isActive
                      ? 'bg-primary/10 text-primary shadow-sm ring-1 ring-primary/20'
                      : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                  )
                }
              >
                <span className="text-lg flex-shrink-0 flex items-center justify-center w-6">{item.icon}</span>
                <span className={cn(
                  "whitespace-nowrap transition-all duration-300",
                  isCollapsed ? "opacity-0 w-0 hidden" : "opacity-100 w-auto"
                )}>
                  {item.label}
                </span>
              </NavLink>
            </li>
          ))}
        </ul>
      </div>

      {/* Collapse Toggle Button */}
      <div className="p-3 border-t border-border mt-auto">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={cn(
            "flex w-full items-center rounded-lg p-2 text-muted-foreground hover:bg-accent hover:text-foreground transition-all duration-200",
            isCollapsed ? "justify-center" : "gap-3 px-3"
          )}
          title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          <span className="text-lg flex-shrink-0 flex items-center justify-center w-6">{isCollapsed ? '▶️' : '◀️'}</span>
          <span className={cn(
            "text-sm font-medium whitespace-nowrap transition-all duration-300",
            isCollapsed ? "opacity-0 w-0 hidden" : "opacity-100 w-auto"
          )}>
            Collapse
          </span>
        </button>
      </div>
    </aside>
  )
}
