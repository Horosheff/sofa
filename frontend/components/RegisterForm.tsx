'use client'

import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'

interface RegisterFormProps {
  onSwitchToLogin: () => void
}

export default function RegisterForm({ onSwitchToLogin }: RegisterFormProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  
  const register = useAuthStore((state) => state.register)

  const validatePassword = (password: string) => {
    const minLength = password.length >= 8
    const hasUpperCase = /[A-Z]/.test(password)
    const hasLowerCase = /[a-z]/.test(password)
    const hasNumbers = /\d/.test(password)
    
    return {
      isValid: minLength && hasUpperCase && hasLowerCase && hasNumbers,
      errors: {
        minLength: !minLength,
        hasUpperCase: !hasUpperCase,
        hasLowerCase: !hasLowerCase,
        hasNumbers: !hasNumbers
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    // Валидация пароля
    const passwordValidation = validatePassword(password)
    if (!passwordValidation.isValid) {
      setError('Пароль должен содержать минимум 8 символов, включая заглавные и строчные буквы, а также цифры')
      setLoading(false)
      return
    }
    
    // Проверка совпадения паролей
    if (password !== confirmPassword) {
      setError('Пароли не совпадают')
      setLoading(false)
      return
    }
    
    // Проверка email
    if (!email.includes('@')) {
      setError('Введите корректный email')
      setLoading(false)
      return
    }
    
    // Проверка имени
    if (fullName.length < 2) {
      setError('Имя должно содержать минимум 2 символа')
      setLoading(false)
      return
    }
    
    try {
      await register(email, password, fullName)
    } catch (err) {
      setError('Ошибка регистрации. Попробуйте еще раз.')
    } finally {
      setLoading(false)
    }
  }

  const passwordValidation = validatePassword(password)

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white text-center">Регистрация</h2>
      
      {error && (
        <div className="glass-panel p-4 border-red-400/50 bg-red-500/20 text-red-200 rounded-lg">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="fullName" className="block text-sm font-medium text-white/80 mb-2">
            Полное имя
          </label>
          <input
            type="text"
            id="fullName"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
            className="modern-input w-full"
            placeholder="Введите ваше полное имя"
          />
        </div>
        
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
          <div className="relative">
            <input
              type={showPassword ? "text" : "password"}
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="modern-input w-full pr-10"
              placeholder="Введите пароль"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-white/60 hover:text-white transition-colors"
            >
              {showPassword ? '👁️' : '👁️‍🗨️'}
            </button>
          </div>
          
          {/* Индикатор силы пароля */}
          <div className="mt-3 glass-panel p-3 rounded-lg">
            <div className="text-xs text-white/70 mb-2">Требования к паролю:</div>
            <div className="space-y-1">
              <div className={`text-xs flex items-center gap-2 ${passwordValidation.errors.minLength ? 'text-red-400' : 'text-green-400'}`}>
                <span>{passwordValidation.errors.minLength ? '✗' : '✓'}</span>
                Минимум 8 символов
              </div>
              <div className={`text-xs flex items-center gap-2 ${passwordValidation.errors.hasUpperCase ? 'text-red-400' : 'text-green-400'}`}>
                <span>{passwordValidation.errors.hasUpperCase ? '✗' : '✓'}</span>
                Заглавные буквы (A-Z)
              </div>
              <div className={`text-xs flex items-center gap-2 ${passwordValidation.errors.hasLowerCase ? 'text-red-400' : 'text-green-400'}`}>
                <span>{passwordValidation.errors.hasLowerCase ? '✗' : '✓'}</span>
                Строчные буквы (a-z)
              </div>
              <div className={`text-xs flex items-center gap-2 ${passwordValidation.errors.hasNumbers ? 'text-red-400' : 'text-green-400'}`}>
                <span>{passwordValidation.errors.hasNumbers ? '✗' : '✓'}</span>
                Цифры (0-9)
              </div>
            </div>
          </div>
        </div>
        
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-white/80 mb-2">
            Подтвердите пароль
          </label>
          <div className="relative">
            <input
              type={showConfirmPassword ? "text" : "password"}
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="modern-input w-full pr-10"
              placeholder="Подтвердите пароль"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-white/60 hover:text-white transition-colors"
            >
              {showConfirmPassword ? '👁️' : '👁️‍🗨️'}
            </button>
          </div>
          
          {confirmPassword && password !== confirmPassword && (
            <div className="text-xs text-red-400 mt-2 flex items-center gap-1">
              <span>✗</span>
              Пароли не совпадают
            </div>
          )}
        </div>
        
        <button
          type="submit"
          disabled={loading || !passwordValidation.isValid || password !== confirmPassword}
          className="modern-button w-full py-3 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Регистрация...' : 'Зарегистрироваться'}
        </button>
      </form>
      
      <p className="text-center text-sm text-white/70">
        Уже есть аккаунт?{' '}
        <button
          onClick={onSwitchToLogin}
          className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
        >
          Войти
        </button>
      </p>
    </div>
  )
}