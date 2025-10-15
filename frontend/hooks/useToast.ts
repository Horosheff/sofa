'use client'

import { useState, useCallback } from 'react'

interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'info' | 'warning'
  duration?: number
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([])

  const addToast = useCallback((
    message: string, 
    type: 'success' | 'error' | 'info' | 'warning' = 'info',
    duration?: number
  ) => {
    const id = Math.random().toString(36).substr(2, 9)
    const newToast: Toast = { id, message, type, duration }
    
    setToasts(prev => [...prev, newToast])
    
    // Auto remove after duration
    setTimeout(() => {
      removeToast(id)
    }, duration || 4000)
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const success = useCallback((message: string, duration?: number) => {
    addToast(message, 'success', duration)
  }, [addToast])

  const error = useCallback((message: string, duration?: number) => {
    addToast(message, 'error', duration)
  }, [addToast])

  const info = useCallback((message: string, duration?: number) => {
    addToast(message, 'info', duration)
  }, [addToast])

  const warning = useCallback((message: string, duration?: number) => {
    addToast(message, 'warning', duration)
  }, [addToast])

  return {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    info,
    warning
  }
}
