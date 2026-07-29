import { create } from 'zustand'

interface NetworkState {
  isOnline: boolean
  hasPendingSync: boolean
  lastSyncAt: Date | null
  setOnline: (online: boolean) => void
  setPendingSync: (pending: boolean) => void
  setLastSyncAt: (date: Date) => void
}

export const useNetworkStore = create<NetworkState>((set) => ({
  isOnline: navigator.onLine,
  hasPendingSync: false,
  lastSyncAt: null,

  setOnline: (online) => set({ isOnline: online }),
  setPendingSync: (pending) => set({ hasPendingSync: pending }),
  setLastSyncAt: (date) => set({ lastSyncAt: date }),
}))
