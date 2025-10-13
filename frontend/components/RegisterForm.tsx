'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useAuthStore } from '@/store/authStore'
import axios from 'axios'

interface RegisterFormData {
  full_name: string
  email: string
  password: string
  confirmPassword: string
}

interface RegisterFormProps {
  onSwitchToLogin: () => void
}

export default function RegisterForm({ onSwitchToLogin }: RegisterFormProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuthStore()
  
  const { register, handleSubmit, watch, formState: { errors } } = useForm<RegisterFormData>()
  const password = watch('password')

  const onSubmit = async (data: RegisterFormData) => {
    if (data.password !== data.confirmPassword) {
      setError('Пароли не совпадают')
      return
    }
    
    setIsLoading(true)
    setError('')
    
    try {
      const response = await axios.post('/api/auth/register', {
        full_name: data.full_name,
        email: data.email,
        password: data.password
      })
      const { access_token } = response.data
      
      // Получаем информацию о пользователе
      const userResponse = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      })
      
      login(access_token, userResponse.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка регистрации')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white mb-2">Регистрация</h2>
        <p className="text-white/60">Создайте новый аккаунт</p>
      </div>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-white/80 mb-2">
            Полное имя
          </label>
          <input
            {...register('full_name', { required: 'Имя обязательно' })}
            type="text"
            className="modern-input w-full"
            placeholder="Иван Иванов"
          />
          {errors.full_name && (
            <p className="text-red-400 text-sm mt-1">{errors.full_name.message}</p>
          )}
        </div>
        
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
            {...register('password', { required: 'Пароль обязателен', minLength: { value: 6, message: 'Пароль должен содержать минимум 6 символов' } })}
            type="password"
            className="modern-input w-full"
            placeholder="••••••••"
          />
          {errors.password && (
            <p className="text-red-400 text-sm mt-1">{errors.password.message}</p>
          )}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-white/80 mb-2">
            Подтвердите пароль
          </label>
          <input
            {...register('confirmPassword', { 
              required: 'Подтверждение пароля обязательно',
              validate: value => value === password || 'Пароли не совпадают'
            })}
            type="password"
            className="modern-input w-full"
            placeholder="••••••••"
          />
          {errors.confirmPassword && (
            <p className="text-red-400 text-sm mt-1">{errors.confirmPassword.message}</p>
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
          {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
        </button>
      </form>
      
      <div className="text-center">
        <span className="text-white/60">Уже есть аккаунт? </span>
        <button
          onClick={onSwitchToLogin}
          className="text-indigo-300 hover:text-indigo-200 font-medium transition-colors"
        >
          Войти
        </button>
      </div>
    </div>
  )
}