'use client'

import { useState, useEffect, useMemo } from 'react'
import { useForm } from 'react-hook-form'
import PasswordField from './PasswordField'
import { useAuthStore } from '@/store/authStore'

interface SettingsResponse {
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

export default function SettingsPanel() {
  const [isLoading, setIsLoading] = useState(false)
  const [isFetching, setIsFetching] = useState(false)
  const [message, setMessage] = useState('')
  const { token, user } = useAuthStore()

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    watch,
  } = useForm<SettingsFormData>({
    defaultValues: useMemo(
      () => ({
        wordpress_url: '',
        wordpress_username: '',
        wordpress_password: '',
        wordstat_client_id: '',
        wordstat_client_secret: '',
        wordstat_redirect_uri: '',
        mcp_sse_url: '',
        mcp_connector_id: '',
        timezone: 'UTC',
        language: 'ru',
      }),
      []
    ),
  })

  const watchValues = {
    wordpress_password: watch('wordpress_password'),
    wordstat_client_secret: watch('wordstat_client_secret'),
    mcp_sse_url: watch('mcp_sse_url'),
    mcp_connector_id: watch('mcp_connector_id'),
  }

  useEffect(() => {
    if (!token) {
      reset()
      return
    }
    const loadSettings = async () => {
      setIsFetching(true)
      setMessage('')
      try {
        const response = await fetch('/api/user/settings', {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        })

        if (!response.ok) {
          throw new Error(await response.text())
        }

        const data: SettingsResponse = await response.json()
        reset({
          wordpress_url: data.wordpress_url ?? '',
          wordpress_username: data.wordpress_username ?? '',
          wordpress_password: data.wordpress_password ?? '',
          wordstat_client_id: data.wordstat_client_id ?? '',
          wordstat_client_secret: data.wordstat_client_secret ?? '',
          wordstat_redirect_uri: data.wordstat_redirect_uri ?? '',
          mcp_sse_url: data.mcp_sse_url ?? '',
          mcp_connector_id: data.mcp_connector_id ?? '',
          timezone: data.timezone ?? 'UTC',
          language: data.language ?? 'ru',
        })
      } catch (error) {
        console.error('Ошибка загрузки настроек:', error)
        setMessage('Не удалось загрузить настройки пользователя')
      } finally {
        setIsFetching(false)
      }
    }

    loadSettings()
  }, [token, reset])

  const onSubmit = async (data: SettingsFormData) => {
    if (!token) {
      setMessage('Не удалось подтвердить авторизацию')
      return
    }

    setIsLoading(true)
    setMessage('')

    try {
      const response = await fetch('/api/user/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...data,
          timezone: data.timezone ?? 'UTC',
          language: data.language ?? 'ru',
        }),
      })

      if (!response.ok) {
        const detail = await response.json().catch(() => ({}))
        throw new Error(detail?.detail || 'Неизвестная ошибка')
      }

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
            <PasswordField
              label="Пароль приложения"
              name="wordpress_password"
              value={watchValues.wordpress_password}
              onChange={(value) => setValue('wordpress_password', value, { shouldDirty: true })}
              onBlur={() => setValue('wordpress_password', watchValues.wordpress_password, { shouldDirty: true })}
              placeholder="••••••••"
              className="md:col-span-2"
            />
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
            <PasswordField
              label="Client Secret"
              name="wordstat_client_secret"
              value={watchValues.wordstat_client_secret}
              onChange={(value) => setValue('wordstat_client_secret', value, { shouldDirty: true })}
              placeholder="••••••••"
            />
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <PasswordField
              label="URL MCP SSE сервера"
              name="mcp_sse_url"
              value={watchValues.mcp_sse_url}
              onChange={(value) => setValue('mcp_sse_url', value, { shouldDirty: true })}
              placeholder="https://mcp-kv.ru/sse/connector"
              readOnly
              className="md:col-span-2"
            />
            <PasswordField
              label="ID коннектора"
              name="mcp_connector_id"
              value={watchValues.mcp_connector_id}
              onChange={(value) => setValue('mcp_connector_id', value, { shouldDirty: true })}
              readOnly
            />
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
        {/* Removed general settings per requirements */}

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