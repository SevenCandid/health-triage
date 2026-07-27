import { useEffect } from 'react'
import { useThemeStore } from '@/stores/theme-store'

/**
 * Initialises the theme on app load.
 * - Reads persisted theme preference from the store.
 * - Applies or removes the 'dark' class on <html>.
 * - Listens for OS-level prefers-color-scheme changes when theme is 'system'.
 */
export function useTheme() {
  const { theme, resolvedTheme, setTheme } = useThemeStore()

  useEffect(() => {
    // Apply resolved theme class on mount
    if (resolvedTheme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [resolvedTheme])

  useEffect(() => {
    if (theme !== 'system') return

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = () => setTheme('system') // re-evaluate system preference

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme, setTheme])

  return { theme, resolvedTheme, setTheme }
}
