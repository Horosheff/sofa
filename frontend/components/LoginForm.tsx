'use client'

import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'

interface LoginFormProps {
  onSwitchToRegister: () => void
}

export default function LoginForm({ onSwitchToRegister }: LoginFormProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const login = useAuthStore((state) => state.login)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      await login(email, password)
    } catch (err) {
      setError('Неверный email или пароль')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white text-center">Вход</h2>
      
      {error && (
        <div className="glass-panel p-4 border-red-400/50 bg-red-500/20 text-red-200 rounded-lg">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-white/80 mb-2">
            Email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="modern-input w-full"
            placeholder="example@email.com"
          />
        </div>
        
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-white/80 mb-2">
            Пароль
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="modern-input w-full"
            placeholder="Введите пароль"
          />
        </div>
        
        <button
          type="submit"
          disabled={loading}
          className="modern-button w-full py-3 text-white font-semibold"
        >
          {loading ? 'Вход...' : 'Войти'}
        </button>
      </form>
      
      <p className="text-center text-sm text-white/70">
        Нет аккаунта?{' '}
        <button
          onClick={onSwitchToRegister}
          className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
        >
          Зарегистрироваться
        </button>
      </p>
    </div>
  )
}