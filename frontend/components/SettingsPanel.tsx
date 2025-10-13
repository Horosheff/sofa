'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useAuthStore } from '@/store/authStore'

interface UserSettings {
  wordpress_url?: string
  wordpress_username?: string
  wordpress_password?: string
  wordstat_client_id?: string
  wordstat_client_secret?: string
  wordstat_redirect_uri?: string
  mcp_sse_url?: string
  mcp_connector_id?: string
  timezone?: string
  language?: string
}

interface SettingsFormData {
  wordpress_url: string
  wordpress_username: string
  wordpress_password: string
  wordstat_client_id: string
  wordstat_client_secret: string
  wordstat_redirect_uri: string
  mcp_sse_url: string
  mcp_connector_id: string
  timezone: string
  language: string
}

export default function SettingsPanel() {
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [settings, setSettings] = useState<UserSettings>({})
  const { token, user } = useAuthStore()
  
  const { register, handleSubmit, formState: { errors }, setValue } = useForm<SettingsFormData>()

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      // Пока API недоступен, используем тестовые данные
      const testSettings = {
        wordpress_url: '',
        wordpress_username: '',
        wordpress_password: '',
        wordstat_client_id: '',
        wordstat_client_secret: '',
        wordstat_redirect_uri: '',
        mcp_sse_url: `https://mcp-kov4eg.com/sse/${user?.id || 'user-12345'}`,
        mcp_connector_id: `${user?.id || 'user-12345'}-connector`,
        timezone: 'UTC',
        language: 'ru'
      }
      
      setSettings(testSettings)
      
      // Заполняем форму
      setValue('wordpress_url', testSettings.wordpress_url || '')
      setValue('wordpress_username', testSettings.wordpress_username || '')
      setValue('wordstat_client_id', testSettings.wordstat_client_id || '')
      setValue('wordstat_redirect_uri', testSettings.wordstat_redirect_uri || '')
      setValue('mcp_sse_url', testSettings.mcp_sse_url || '')
      setValue('mcp_connector_id', testSettings.mcp_connector_id || '')
      setValue('timezone', testSettings.timezone || 'UTC')
      setValue('language', testSettings.language || 'ru')
    } catch (error) {
      console.error('Ошибка загрузки настроек:', error)
    }
  }

  const onSubmit = async (data: SettingsFormData) => {
    setIsLoading(true)
    setMessage('')
    
    try {
      // Пока API недоступен, просто сохраняем в localStorage
      localStorage.setItem('user-settings', JSON.stringify(data))
      setMessage('Настройки успешно сохранены!')
    } catch (error: any) {
      setMessage('Ошибка сохранения настроек: ' + (error.message || 'Неизвестная ошибка'))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold gradient-text mb-4">Настройки</h2>
        <p className="text-white/70">Настройте подключения к внешним сервисам</p>
      </div>

      {/* User Info */}
      <div className="modern-card p-6">
        <h3 className="text-xl font-bold text-white mb-6 flex items-center">
          👤 Информация о пользователе
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">
              Имя пользователя
            </label>
            <div className="modern-input w-full bg-slate-800/50 text-white/70">
              {user?.full_name || 'Не указано'}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">
              Email
            </label>
            <div className="modern-input w-full bg-slate-800/50 text-white/70">
              {user?.email || 'Не указано'}
            </div>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* WordPress Settings */}
        <div className="modern-card p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center">
            📝 WordPress настройки
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                URL сайта WordPress
              </label>
              <input
                {...register('wordpress_url')}
                type="url"
                className="modern-input w-full"
                placeholder="https://example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Имя пользователя
              </label>
              <input
                {...register('wordpress_username')}
                type="text"
                className="modern-input w-full"
                placeholder="username"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-white/80 mb-2">
                Пароль приложения
              </label>
              <input
                {...register('wordpress_password')}
                type="password"
                className="modern-input w-full"
                placeholder="••••••••"
              />
            </div>
          </div>
        </div>

        {/* Wordstat Settings */}
        <div className="modern-card p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center">
            📊 Wordstat API настройки
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Client ID
              </label>
              <input
                {...register('wordstat_client_id')}
                type="text"
                className="modern-input w-full"
                placeholder="your_client_id"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Client Secret
              </label>
              <input
                {...register('wordstat_client_secret')}
                type="password"
                className="modern-input w-full"
                placeholder="••••••••"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-white/80 mb-2">
                Redirect URI
              </label>
              <input
                {...register('wordstat_redirect_uri')}
                type="url"
                className="modern-input w-full"
                placeholder="https://example.com/callback"
              />
            </div>
          </div>
        </div>

        {/* MCP SSE Settings */}
        <div className="modern-card p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center">
            🔗 MCP SSE сервер
          </h3>
          <div className="grid grid-cols-1 gap-6">
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                URL MCP SSE сервера
              </label>
              <input
                {...register('mcp_sse_url')}
                type="url"
                className="modern-input w-full"
                placeholder="https://mcp-kov4eg.com/sse/your-connector-id"
              />
              <p className="text-xs text-white/60 mt-1">
                Уникальный URL для подключения к MCP серверу
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                ID коннектора
              </label>
              <input
                {...register('mcp_connector_id')}
                type="text"
                className="modern-input w-full"
                placeholder="user-12345-connector"
                readOnly
              />
              <p className="text-xs text-white/60 mt-1">
                Автоматически генерируется при регистрации
              </p>
            </div>
          </div>
          <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <h4 className="text-sm font-semibold text-blue-300 mb-2">📋 Как получить MCP SSE URL:</h4>
            <ol className="text-xs text-white/70 space-y-1 list-decimal list-inside">
              <li>После регистрации система автоматически создаст ваш уникальный коннектор</li>
              <li>Скопируйте URL из поля выше</li>
              <li>Используйте этот URL в ChatGPT или других AI клиентах</li>
              <li>Выберите аутентификацию "OAuth" или "Без аутентификации"</li>
            </ol>
          </div>
        </div>

        {/* General Settings */}
        <div className="modern-card p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center">
            ⚙️ Общие настройки
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Часовой пояс
              </label>
              <select
                {...register('timezone')}
                className="modern-input w-full"
              >
                <option value="UTC">UTC</option>
                <option value="Europe/Moscow">Москва</option>
                <option value="Europe/Kiev">Киев</option>
                <option value="America/New_York">Нью-Йорк</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Язык
              </label>
              <select
                {...register('language')}
                className="modern-input w-full"
              >
                <option value="ru">Русский</option>
                <option value="en">English</option>
                <option value="uk">Українська</option>
              </select>
            </div>
          </div>
        </div>

        {message && (
          <div className={`modern-card p-4 ${
            message.includes('Ошибка') 
              ? 'bg-red-500/10 border border-red-500/20' 
              : 'bg-green-500/10 border border-green-500/20'
          }`}>
            <div className={`text-sm ${
              message.includes('Ошибка') ? 'text-red-400' : 'text-green-400'
            }`}>
              {message}
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="btn-primary w-full py-4 text-lg font-semibold disabled:opacity-50"
        >
          {isLoading ? '⏳ Сохранение...' : '💾 Сохранить настройки'}
        </button>
      </form>
    </div>
  )
}