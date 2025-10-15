'use client'

import { useState, useEffect, useMemo } from 'react'
import { useForm } from 'react-hook-form'
import PasswordField from './PasswordField'
import { useAuthStore } from '@/store/authStore'
import { useToast } from '@/hooks/useToast'
import ToastContainer from './ToastContainer'

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
  const { toasts, success, error, removeToast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [isFetching, setIsFetching] = useState(false)
  const [message, setMessage] = useState('')
  const [authCode, setAuthCode] = useState('')
  const [showCodeInput, setShowCodeInput] = useState(false)
  const [authUrl, setAuthUrl] = useState('')
  const { token, user } = useAuthStore()

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    watch,
    getValues,
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
    wordstat_client_id: watch('wordstat_client_id'),
    wordstat_redirect_uri: watch('wordstat_redirect_uri'),
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

  // Генерируем OAuth URL и сохраняем настройки
  const generateOAuthUrl = async () => {
    if (!watchValues.wordstat_client_id) {
      setMessage('Заполните Client ID')
      return
    }

    setIsLoading(true)
    setMessage('')

    try {
      // Получаем текущие значения из формы
      const formData = getValues()
      
      // Сначала сохраняем настройки
      const response = await fetch('/api/user/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          wordstat_client_id: formData.wordstat_client_id,
          wordstat_client_secret: formData.wordstat_client_secret,
          wordstat_redirect_uri: formData.wordstat_redirect_uri,
          timezone: 'UTC',
          language: 'ru',
        }),
      })

      if (!response.ok) {
        const detail = await response.json().catch(() => ({}))
        throw new Error(detail?.detail || 'Неизвестная ошибка')
      }

      // После успешного сохранения генерируем OAuth URL
      const currentRedirectUri = formData.wordstat_redirect_uri;
      const redirectUri = (currentRedirectUri && currentRedirectUri.trim()) || 
        (window.location.hostname === 'localhost' 
          ? 'http://localhost:3000/dashboard'
          : 'https://mcp-kv.ru/dashboard');
      
      const params = new URLSearchParams({
        client_id: formData.wordstat_client_id || '',
        redirect_uri: redirectUri,
        response_type: 'code'
      });
      
      setAuthUrl(`https://oauth.yandex.ru/authorize?${params.toString()}`);
      setMessage('✅ Настройки сохранены! OAuth ссылка сгенерирована.')
      
    } catch (error: any) {
      setMessage('Ошибка сохранения настроек: ' + (error.message || 'Неизвестная ошибка'))
    } finally {
      setIsLoading(false)
    }
  }

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

      success('Настройки успешно сохранены!')
    } catch (error: any) {
      error('Ошибка сохранения настроек: ' + (error.message || 'Неизвестная ошибка'))
    } finally {
      setIsLoading(false)
    }
  }

  const copyAuthUrl = () => {
    navigator.clipboard.writeText(authUrl);
    success('Ссылка скопирована в буфер обмена!');
  };

  const handleCodeSubmit = async () => {
    if (!authCode.trim()) {
      error('Введите код авторизации');
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await fetch('/api/oauth/yandex/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ code: authCode }),
      });

      const data = await response.json();

      if (response.ok) {
        success('Токен успешно получен и сохранен!');
        setAuthCode('');
        setShowCodeInput(false);
      } else {
        error(data.error || 'Ошибка получения токена');
      }
    } catch (err) {
      error('Ошибка соединения с сервером');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold gradient-text mb-4">Настройки</h2>
        <p className="text-foreground/70">Настройте подключения к внешним сервисам</p>
      </div>

      {/* User Info */}
      <div className="glass-panel">
        <h3 className="text-xl font-bold text-foreground mb-6 flex items-center">
          👤 Информация о пользователе
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-2">
              Имя пользователя
            </label>
            <div className="modern-input w-full text-foreground/70">
              {user?.full_name || 'Не указано'}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground/80 mb-2">
              Email
            </label>
            <div className="modern-input w-full text-foreground/70">
              {user?.email || 'Не указано'}
            </div>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* WordPress Settings */}
        <div className="glass-panel">
          <h3 className="text-xl font-bold text-foreground mb-6 flex items-center">
            📝 WordPress настройки
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-foreground/80 mb-2">
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
        <div className="glass-panel">
          <h3 className="text-xl font-bold text-foreground mb-6 flex items-center">
            📊 Wordstat API настройки
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-foreground/80 mb-2">
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
              <label className="block text-sm font-medium text-foreground/80 mb-2">
                Redirect URI
              </label>
              <input
                {...register('wordstat_redirect_uri')}
                type="url"
                className="modern-input w-full"
                placeholder="https://example.com/callback"
              />
              <button
                type="button"
                onClick={generateOAuthUrl}
                className="modern-button mt-2 w-full md:w-auto"
                disabled={isLoading}
              >
                💾 Сохранить и получить ссылку
              </button>
            </div>
          </div>

          {/* OAuth Section */}
          {watchValues.wordstat_client_id && watchValues.wordstat_client_secret && authUrl && (
            <div className="mt-6 glass-form border-blue-500/30">
              <h4 className="text-lg font-semibold text-blue-600 mb-4">🔐 Авторизация Wordstat</h4>
              
              {/* Step 1: Copy Link */}
              <div className="mb-4">
                <h5 className="font-medium text-foreground mb-2">📋 Шаг 1: Получите код авторизации</h5>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={authUrl}
                    readOnly
                    className="flex-1 modern-input text-sm font-mono"
                  />
                  <button
                    onClick={copyAuthUrl}
                    className="modern-button px-3 py-2 text-sm font-medium"
                  >
                    📋 Скопировать
                  </button>
                </div>
                <p className="text-xs text-foreground/70 mt-2">
                  Скопируйте ссылку и откройте её в новой вкладке для авторизации в Yandex
                </p>
              </div>

              {/* Step 2: Enter Code */}
              <div>
                <h5 className="font-medium text-foreground mb-2">🔑 Шаг 2: Введите код авторизации</h5>
                {!showCodeInput ? (
                  <button
                    onClick={() => setShowCodeInput(true)}
                    className="modern-button bg-green-500/20 border-green-500/30 text-green-600 hover:bg-green-500/30 px-4 py-2 text-sm font-medium"
                  >
                    📝 Ввести код авторизации
                  </button>
                ) : (
                  <div className="space-y-3">
                    <div className="glass-form border-blue-500/30">
                      <p className="text-sm text-foreground mb-2">
                        После авторизации в Yandex вы будете перенаправлены на страницу с кодом в URL.
                        Скопируйте код из адресной строки (параметр <code>code=</code>) и вставьте его ниже:
                      </p>
                      <p className="text-xs text-blue-600">
                        Пример: <code>http://localhost:3000/dashboard?code=ABC123</code> → код: <code>ABC123</code>
                      </p>
                    </div>
                    <input
                      type="text"
                      value={authCode}
                      onChange={(e) => setAuthCode(e.target.value)}
                      placeholder="Вставьте код авторизации здесь..."
                      className="w-full modern-input text-sm"
                    />
                    <div className="flex space-x-2">
                      <button
                        onClick={handleCodeSubmit}
                        disabled={isLoading}
                        className="modern-button bg-green-500/20 border-green-500/30 text-green-600 hover:bg-green-500/30 disabled:opacity-50 px-4 py-2 text-sm font-medium"
                      >
                        {isLoading ? '⏳ Получение токена...' : '✅ Получить токен'}
                      </button>
                      <button
                        onClick={() => {
                          setShowCodeInput(false);
                          setAuthCode('');
                        }}
                        className="modern-button bg-gray-500/20 border-gray-500/30 text-gray-600 hover:bg-gray-500/30 px-4 py-2 text-sm font-medium"
                      >
                        ❌ Отмена
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-4 glass-form border-blue-500/30">
                <h6 className="text-sm font-semibold text-blue-600 mb-2">ℹ️ Инструкция:</h6>
                <ol className="text-xs text-foreground/70 space-y-1 list-decimal list-inside">
                  <li>Нажмите "Скопировать" и откройте ссылку в новой вкладке</li>
                  <li>Авторизуйтесь в Yandex и разрешите доступ приложению</li>
                  <li>Скопируйте код из адресной строки (параметр code=)</li>
                  <li>Вставьте код в форму выше и нажмите "Получить токен"</li>
                </ol>
              </div>
            </div>
          )}
        </div>

        {/* MCP SSE Settings */}
        <div className="glass-panel">
          <h3 className="text-xl font-bold text-foreground mb-6 flex items-center">
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
          <div className="mt-4 glass-form border-blue-500/30">
            <h4 className="text-sm font-semibold text-blue-600 mb-2">📋 Как получить MCP SSE URL:</h4>
            <ol className="text-xs text-foreground/70 space-y-1 list-decimal list-inside">
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
          <div className={`glass-form ${
            message.includes('Ошибка') 
              ? 'border-red-500/30' 
              : 'border-green-500/30'
          }`}>
            <div className={`text-sm ${
              message.includes('Ошибка') ? 'text-red-600' : 'text-green-600'
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
      
      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  )
}