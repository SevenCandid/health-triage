import { Outlet } from 'react-router-dom'
import { Navbar } from '@/components/layout/Navbar'
import { BottomTabBar } from '@/components/layout/BottomTabBar'
import { OfflineBanner } from '@/components/common/OfflineBanner'
import { InstallNotice } from '@/components/common/InstallNotice'
import { useOnlineStatus } from '@/hooks/use-online-status'
import { useTheme } from '@/hooks/use-theme'

/**
 * RootLayout — the primary authenticated shell.
 *
 * Renders:
 *  - Sticky top Navbar
 *  - Offline status banner (slides in when network drops)
 *  - <Outlet> for child route content
 *  - Fixed bottom tab bar for mobile
 *
 * Hooks: registers online/offline listeners & theme initialisation.
 */
export function RootLayout() {
  // Register global hooks here — runs once at layout level
  useOnlineStatus()
  useTheme()

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <OfflineBanner />
      <Navbar />
      <InstallNotice />

      {/* Page content */}
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 pb-12 sm:px-6 lg:px-8">
        <Outlet />
      </main>

      <BottomTabBar />
    </div>
  )
}
