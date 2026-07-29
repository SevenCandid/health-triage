import { useEffect } from 'react'
import { useNetworkStore } from '@/stores/network-store'

/**
 * Listens to browser online/offline events and syncs state to the network store.
 * Register this hook once at the layout level.
 */
export function useOnlineStatus() {
  const { setOnline, isOnline } = useNetworkStore()

  useEffect(() => {
    const handleOnline = () => setOnline(true)
    const handleOffline = () => setOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [setOnline])

  return isOnline
}
