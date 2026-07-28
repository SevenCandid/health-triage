import { lazy, Suspense } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { RootLayout } from '@/layouts/RootLayout'
import { AuthLayout } from '@/layouts/AuthLayout'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { ErrorBoundary } from '@/components/common/ErrorBoundary'
import { useAuthStore } from '@/stores/auth-store'

// ── Lazy Page Imports ─────────────────────────────────────────────────────────
// All pages are code-split via dynamic import. Only loaded when navigated to.

const LoginPage            = lazy(() => import('@/features/auth/pages/LoginPage'))
const RegisterPage         = lazy(() => import('@/features/auth/pages/RegisterPage'))
const DashboardPage        = lazy(() => import('@/features/dashboard/pages/DashboardPage'))
const AssessmentPage       = lazy(() => import('@/features/assessment/pages/AssessmentPage'))
const AssessmentResultPage = lazy(() => import('@/features/assessment/pages/AssessmentResultPage'))
const HistoryPage          = lazy(() => import('@/features/history/pages/HistoryPage'))
const EmergencyPage        = lazy(() => import('@/features/emergency/pages/EmergencyPage'))
const ProfilePage          = lazy(() => import('@/features/profile/pages/ProfilePage'))
const SettingsPage         = lazy(() => import('@/features/settings/pages/SettingsPage'))
const VoicePage            = lazy(() => import('@/features/voice/pages/VoicePage'))
const NotFoundPage         = lazy(() => import('@/features/error/pages/NotFoundPage'))
const LandingPage          = lazy(() => import('@/features/landing/pages/LandingPage'))
const InsightsPage         = lazy(() => import('@/features/insights/pages/InsightsPage'))

// ── Guards ────────────────────────────────────────────────────────────────────

function RequireAuth({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

function RedirectIfAuth({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (isAuthenticated) return <Navigate to="/dashboard" replace />
  return <>{children}</>
}

// ── Route Wrapper with Suspense + ErrorBoundary ───────────────────────────────

function Page({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary>
      <Suspense fallback={<PageLoader />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  )
}

// ── Router Definition ─────────────────────────────────────────────────────────

export const router = createBrowserRouter([
  // ── Public Landing Page ──────────────────────────────────────────────────
  {
    path: '/',
    element: (
      <RedirectIfAuth>
        <Page><LandingPage /></Page>
      </RedirectIfAuth>
    ),
  },

  // ── Auth Routes ──────────────────────────────────────────────────────────
  {
    element: <AuthLayout />,
    children: [
      {
        path: '/login',
        element: (
          <RedirectIfAuth>
            <Page><LoginPage /></Page>
          </RedirectIfAuth>
        ),
      },
      {
        path: '/register',
        element: (
          <RedirectIfAuth>
            <Page><RegisterPage /></Page>
          </RedirectIfAuth>
        ),
      },
    ],
  },

  // ── Authenticated App Routes ─────────────────────────────────────────────
  {
    element: (
      <RequireAuth>
        <RootLayout />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      {
        path: '/dashboard',
        element: <Page><DashboardPage /></Page>,
      },
      {
        path: '/insights',
        element: <Page><InsightsPage /></Page>,
      },
      {
        path: '/assessment',
        element: <Page><AssessmentPage /></Page>,
      },
      {
        path: '/assessment/:sessionId/result',
        element: <Page><AssessmentResultPage /></Page>,
      },
      {
        path: '/history',
        element: <Page><HistoryPage /></Page>,
      },
      {
        path: '/emergency',
        element: <Page><EmergencyPage /></Page>,
      },
      {
        path: '/profile',
        element: <Page><ProfilePage /></Page>,
      },
      {
        path: '/settings',
        element: <Page><SettingsPage /></Page>,
      },
      {
        path: '/voice',
        element: <Page><VoicePage /></Page>,
      },
    ],
  },

  // ── 404 ───────────────────────────────────────────────────────────────────
  {
    path: '*',
    element: <Page><NotFoundPage /></Page>,
  },
])
