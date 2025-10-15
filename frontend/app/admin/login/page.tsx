'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import axios from 'axios'

export default function AdminLoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Авторизация
      const loginResponse = await axios.post('/api/login', {
        email,
        password,
      })

      const { access_token, user } = loginResponse.data

      // Проверка прав администратора
      try {
        await axios.get('/api/admin/dashboard', {
          headers: { Authorization: `Bearer ${access_token}` },
        })

        // Сохраняем в Zustand store (который сохранит в localStorage через persist)
        useAuthStore.setState({
          token: access_token,
          user: user,
          isAuthenticated: true,
          hasHydrated: true
        })

        // Даем время на сохранение в localStorage
        await new Promise(resolve => setTimeout(resolve, 100))

        // Перенаправляем в админ-панель
        router.push('/admin')
      } catch (err) {
        setError('У вас нет прав администратора')
      }
    } catch (err: any) {
      console.error('Login error:', err)
      setError(err.response?.data?.detail || 'Неверный email или пароль')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      {/* Login Form */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-10 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gray-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-3xl">🔐</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Админ-панель</h1>
          <p className="text-gray-600">Вход только для администраторов</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-5">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Email администратора
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@example.com"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed text-gray-900 bg-white"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Пароль
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed text-gray-900 bg-white"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gray-900 hover:bg-gray-800 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            {loading ? 'Проверка прав...' : '🔓 Войти в админ-панель'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => router.push('/')}
            className="text-sm text-gray-600 hover:text-gray-900 transition-colors font-medium"
          >
            ← Вернуться на главную
          </button>
        </div>
      </div>
    </div>
  )
}

