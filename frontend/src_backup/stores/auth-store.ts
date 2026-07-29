import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  userId: string | null
  userRole: string | null
  profileCompleted: boolean
  profileSkipped: boolean
  isAuthenticated: boolean
  setAuth: (token: string, refreshToken: string, userId: string, role: string, profileCompleted: boolean) => void
  setProfileCompleted: (completed: boolean) => void
  setProfileSkipped: (skipped: boolean) => void
  clearAuth: () => void
}

export const authStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      userId: null,
      userRole: null,
      profileCompleted: false,
      profileSkipped: false,
      isAuthenticated: false,

      setAuth: (token, refreshToken, userId, role, profileCompleted) =>
        set({ 
          accessToken: token, 
          refreshToken, 
          userId, 
          userRole: role, 
          profileCompleted, 
          isAuthenticated: true 
        }),

      setProfileCompleted: (completed) =>
        set({ profileCompleted: completed }),

      setProfileSkipped: (skipped) =>
        set({ profileSkipped: skipped }),

      clearAuth: () =>
        set({ 
          accessToken: null, 
          refreshToken: null, 
          userId: null, 
          userRole: null, 
          profileCompleted: false, 
          isAuthenticated: false 
        }),
    }),
    {
      name: 'health-triage-auth',
      storage: createJSONStorage(() => localStorage),
      // Only persist non-sensitive fields; token is stored for session continuity
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        userId: state.userId,
        userRole: state.userRole,
        profileCompleted: state.profileCompleted,
        profileSkipped: state.profileSkipped,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

// Named hook for component consumption
export const useAuthStore = authStore
