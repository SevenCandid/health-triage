import { useState, useCallback } from 'react'
import { ToastContainer } from '@/components/ui/Toast'

interface ToastItem {
  id: string
  type?: 'success' | 'error' | 'warning' | 'info'
  message: string
}

let _addToast: ((toast: Omit<ToastItem, 'id'>) => void) | null = null

/** Imperative helper — call outside React tree (e.g. Axios interceptors) */
export function toast(message: string, type: ToastItem['type'] = 'info') {
  _addToast?.({ message, type })
}

export function useToast() {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  const addToast = useCallback((item: Omit<ToastItem, 'id'>) => {
    const id = crypto.randomUUID()
    setToasts((prev) => [...prev, { id, ...item }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 5000)
  }, [])

  // Expose imperative handle
  _addToast = addToast

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  return { toasts, addToast, dismiss, ToastContainer }
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const { toasts, dismiss } = useToast()
  return (
    <>
      {children}
      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </>
  )
}
