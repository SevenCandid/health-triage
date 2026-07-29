import { NavLink, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { useAuthStore } from '@/stores/auth-store'
import { useTheme } from '@/hooks/use-theme'
import { useNetworkStore } from '@/stores/network-store'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { usePWAInstall } from '@/hooks/use-pwa-install'
import { navItems } from '@/components/layout/Sidebar'

export function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false)
  const { isAuthenticated, clearAuth, userRole } = useAuthStore()
  const { resolvedTheme, setTheme } = useTheme()
  const isOnline = useNetworkStore((s) => s.isOnline)
  const navigate = useNavigate()
  const { isInstallable, promptInstall } = usePWAInstall()

  const toggleTheme = () => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  const isGuest = userRole === 'GUEST'
  const activeItems = isGuest
    ? navItems.filter(item => item.to === '/dashboard' || item.to === '/emergency' || item.to === '/settings')
    : navItems

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-sm">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-2 font-bold text-foreground">
          <span className="text-2xl">❤️‍🩹</span>
          <span>Triage Assistant</span>
        </NavLink>

        {/* Desktop Nav (Moved to Sidebar) */}

        {/* Right Controls */}
        <div className="flex items-center gap-2">
          {/* Install Button (Desktop) */}
          {isInstallable && (
            <Button
              variant="outline"
              size="sm"
              onClick={promptInstall}
              className="hidden sm:flex text-xs h-8 font-semibold gap-1.5 border-primary/20 text-primary bg-primary/5 hover:bg-primary/10"
            >
              <span>📱</span> Install App
            </Button>
          )}

          {/* Online Dot */}
          <span
            title={isOnline ? 'Online' : 'Offline'}
            className={cn(
              'h-2 w-2 rounded-full',
              isOnline ? 'bg-urgency-routine' : 'bg-urgency-emergency animate-pulse'
            )}
          />

          {/* Dark Mode Toggle */}
          <button
            id="navbar-theme-toggle"
            onClick={toggleTheme}
            aria-label="Toggle dark mode"
            className="rounded-lg p-2 text-muted-foreground transition hover:bg-accent hover:text-foreground mr-1"
          >
            {resolvedTheme === 'dark' ? '☀️' : '🌙'}
          </button>

          {/* Auth Controls */}
          {isAuthenticated && !isGuest ? (
            <button
              id="navbar-logout-btn"
              onClick={handleLogout}
              className="hidden rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition hover:bg-accent sm:block"
            >
              Logout
            </button>
          ) : (
            <div className="hidden sm:flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                className="text-xs h-8 font-semibold"
                onClick={() => { clearAuth(); navigate('/login') }}
              >
                Sign In
              </Button>
              <Button
                size="sm"
                className="text-xs h-8 font-bold"
                onClick={() => { clearAuth(); navigate('/register') }}
              >
                Sign Up
              </Button>
            </div>
          )}

          {/* Mobile Hamburger */}
          <button
            id="navbar-mobile-menu-btn"
            onClick={() => setMenuOpen((o) => !o)}
            aria-label="Toggle menu"
            aria-expanded={menuOpen}
            className="rounded-lg p-2 md:hidden text-muted-foreground hover:bg-accent"
          >
            {menuOpen ? '✕' : '☰'}
          </button>
        </div>
      </nav>

      {/* Mobile Drawer */}
      <AnimatePresence>
        {menuOpen && isAuthenticated && (
          <motion.div
            key="mobile-menu"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-t border-border bg-background md:hidden"
          >
            <ul className="flex flex-col gap-1 p-4">
              {isInstallable && (
                <li className="pt-1 border-b border-border/50 pb-2 mb-1">
                  <Button
                    variant="outline"
                    onClick={() => { promptInstall(); setMenuOpen(false); }}
                    className="w-full text-xs font-semibold py-2.5 flex items-center justify-center gap-2 border-primary/20 text-primary bg-primary/5"
                  >
                    <span>📱</span> Install Triage App
                  </Button>
                </li>
              )}
              {activeItems.map((item) => (
                <li key={item.to}>
                  <NavLink
                    to={item.to}
                    onClick={() => setMenuOpen(false)}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center gap-2 rounded-lg px-3 py-3 text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-accent text-accent-foreground'
                          : 'text-muted-foreground hover:bg-accent'
                      )
                    }
                  >
                    <span>{item.icon}</span>
                    {item.label}
                  </NavLink>
                </li>
              ))}
              {isGuest ? (
                <li className="grid grid-cols-2 gap-2 pt-2 border-t border-border mt-2">
                  <Button
                    variant="outline"
                    onClick={() => { clearAuth(); setMenuOpen(false); navigate('/login') }}
                    className="w-full text-xs font-semibold py-2.5"
                  >
                    Sign In
                  </Button>
                  <Button
                    onClick={() => { clearAuth(); setMenuOpen(false); navigate('/register') }}
                    className="w-full text-xs font-bold py-2.5"
                  >
                    Sign Up
                  </Button>
                </li>
              ) : (
                <li>
                  <button
                    onClick={() => { handleLogout(); setMenuOpen(false) }}
                    className="w-full text-left flex items-center gap-2 rounded-lg px-3 py-3 text-sm font-medium text-muted-foreground hover:bg-accent"
                  >
                    <span>🚪</span> Logout
                  </button>
                </li>
              )}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
