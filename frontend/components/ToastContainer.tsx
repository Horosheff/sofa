'use client'

import ToastNotification from './ToastNotification'

interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'info' | 'warning'
  duration?: number
}

interface ToastContainerProps {
  toasts: Toast[]
  onRemove: (id: string) => void
}

export default function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => (
        <ToastNotification
          key={toast.id}
          message={toast.message}
          type={toast.type}
          isVisible={true}
          onClose={() => onRemove(toast.id)}
          duration={toast.duration}
        />
      ))}
    </div>
  )
}
