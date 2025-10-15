'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import AdminPanel from '@/components/AdminPanel'
import axios from 'axios'

export default function AdminPage() {
  const router = useRouter()
  const { token, user } = useAuthStore()
  const [isAdmin, setIsAdmin] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkAdminAccess = async () => {
      if (!token) {
        router.push('/admin/login')
        return
      }

      try {
        // Проверяем доступ к админ-панели
        await axios.get('/api/admin/dashboard', {
          headers: { Authorization: `Bearer ${token}` },
        })
        setIsAdmin(true)
        setLoading(false)
      } catch (err) {
        console.error('Access denied:', err)
        // Перенаправляем на страницу логина админа
        router.push('/admin/login')
      }
    }

    checkAdminAccess()
  }, [token, router])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center">
          <p className="text-xl font-semibold text-gray-900">🔐 Проверка прав доступа...</p>
        </div>
      </div>
    )
  }

  if (!isAdmin) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Логотип */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gray-900 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Admin Panel</h1>
                <p className="text-sm text-gray-500">Управление платформой</p>
              </div>
            </div>

            {/* Пользователь */}
            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-red-50 rounded-lg border border-red-200">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-xs font-medium text-red-700">Admin Mode</span>
              </div>

              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gray-900 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold">
                    {user?.full_name?.charAt(0).toUpperCase() || 'A'}
                  </span>
                </div>
                <div className="hidden md:block text-right">
                  <p className="text-sm font-semibold text-gray-900">{user?.full_name}</p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
              </div>

              <button
                onClick={() => router.push('/dashboard')}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-xl transition-all text-sm font-medium text-gray-900"
              >
                ← Дашборд
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="container mx-auto px-6 py-8 max-w-7xl">
        <AdminPanel />
      </main>
    </div>
  )
}

