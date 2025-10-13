'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useAuthStore } from '@/store/authStore'
import axios from 'axios'

interface LoginFormData {
  email: string
  password: string
}

interface LoginFormProps {
  onSwitchToRegister: () => void
}

export default function LoginForm({ onSwitchToRegister }: LoginFormProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuthStore()
  
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>()

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    setError('')
    
    try {
      const response = await axios.post('/api/auth/login', data)
      const { access_token } = response.data
      
      // Получаем информацию о пользователе
      const userResponse = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      })
      
      login(access_token, userResponse.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка входа в систему')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white mb-2">Вход в систему</h2>
        <p className="text-white/60">Войдите в свой аккаунт</p>
      </div>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-white/80 mb-2">
            Email
          </label>
          <input
            {...register('email', { required: 'Email обязателен' })}
            type="email"
            className="modern-input w-full"
            placeholder="your@email.com"
          />
          {errors.email && (
            <p className="text-red-400 text-sm mt-1">{errors.email.message}</p>
          )}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-white/80 mb-2">
            Пароль
          </label>
          <input
            {...register('password', { required: 'Пароль обязателен' })}
            type="password"
            className="modern-input w-full"
            placeholder="••••••••"
          />
          {errors.password && (
            <p className="text-red-400 text-sm mt-1">{errors.password.message}</p>
          )}
        </div>
        
        {error && (
          <div className="text-red-400 text-sm bg-red-500/10 p-3 rounded-lg border border-red-500/20">
            {error}
          </div>
        )}
        
        <button
          type="submit"
          disabled={isLoading}
          className="btn-primary w-full py-3 text-lg font-semibold disabled:opacity-50"
        >
          {isLoading ? 'Вход...' : 'Войти'}
        </button>
      </form>
      
      <div className="text-center">
        <span className="text-white/60">Нет аккаунта? </span>
        <button
          onClick={onSwitchToRegister}
          className="text-indigo-300 hover:text-indigo-200 font-medium transition-colors"
        >
          Зарегистрироваться
        </button>
      </div>
    </div>
  )
}