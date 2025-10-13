'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import Dashboard from '@/components/Dashboard'

export default function DashboardPage() {
  const router = useRouter()
  const { isAuthenticated, hasHydrated, setHydrated } = useAuthStore()

  useEffect(() => {
    setHydrated()
  }, [setHydrated])

  useEffect(() => {
    if (hasHydrated && !isAuthenticated) {
      router.replace('/')
    }
  }, [hasHydrated, isAuthenticated, router])

  if (!hasHydrated) {
    return null
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-950 to-indigo-900">
        <span className="text-white/70 text-lg animate-pulse">
          Проверяем доступ...
        </span>
      </div>
    )
  }

  return <Dashboard />
}
