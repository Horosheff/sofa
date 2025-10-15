#!/bin/bash

# 🔍 ПРОВЕРЯЕМ И ИСПРАВЛЯЕМ SETTINGS PANEL
echo "🔍 ПРОВЕРЯЕМ И ИСПРАВЛЯЕМ SETTINGS PANEL"
echo "========================================"

# Переходим в правильную папку
cd /opt/sofiya

# 1. ПРОВЕРЯЕМ ТЕКУЩИЙ SETTINGS PANEL
echo "1️⃣ Проверяем текущий SettingsPanel.tsx..."
echo "Поиск telegramTestResult:"
grep -n "telegramTestResult" frontend/components/SettingsPanel.tsx || echo "❌ telegramTestResult НЕ НАЙДЕН"

echo ""
echo "Поиск testTelegramBot:"
grep -n "testTelegramBot" frontend/components/SettingsPanel.tsx || echo "❌ testTelegramBot НЕ НАЙДЕН"

echo ""
echo "Поиск кнопки проверки:"
grep -n "Проверка Telegram бота" frontend/components/SettingsPanel.tsx || echo "❌ Кнопка проверки НЕ НАЙДЕНА"

# 2. ПОКАЗЫВАЕМ СТРУКТУРУ ФАЙЛА
echo ""
echo "2️⃣ Структура SettingsPanel.tsx:"
head -20 frontend/components/SettingsPanel.tsx

# 3. ИЩЕМ ГДЕ ДОБАВИТЬ КОД
echo ""
echo "3️⃣ Ищем где добавить код..."
echo "Поиск useState:"
grep -n "useState" frontend/components/SettingsPanel.tsx

echo ""
echo "Поиск handleSubmit:"
grep -n "handleSubmit" frontend/components/SettingsPanel.tsx

# 4. ВРУЧНУЮ ДОБАВЛЯЕМ КНОПКУ
echo ""
echo "4️⃣ Вручную добавляем кнопку..."

# Создаем новый SettingsPanel.tsx с кнопкой
cat > frontend/components/SettingsPanel.tsx << 'EOF'
'use client'

import { useState, useEffect, useMemo } from 'react'
import { useForm } from 'react-hook-form'
import { useAuthStore } from '@/store/authStore'
import PasswordField from './inputs/PasswordField'

interface SettingsResponse {
  wordpress_url?: string
  wordpress_username?: string
  wordpress_password?: string
  wordstat_client_id?: string
  wordstat_client_secret?: string
  wordstat_redirect_uri?: string
  telegram_webhook_url?: string
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
  telegram_bot_token?: string
  telegram_webhook_url?: string
  telegram_webhook_secret?: string
  mcp_sse_url?: string
  mcp_connector_id?: string
  timezone?: string
  language?: string
}

export default function SettingsPanel() {
  const { user } = useAuthStore()
  const [settings, setSettings] = useState<SettingsResponse>({})
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  
  // Добавляем состояние для проверки Telegram
  const [telegramTestResult, setTelegramTestResult] = useState<{
    status: 'idle' | 'testing' | 'success' | 'error'
    message: string
  }>({ status: 'idle', message: '' })

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isDirty }
  } = useForm<SettingsFormData>({
    defaultValues: useMemo(
      () => ({
        wordpress_url: '',
        wordpress_username: '',
        wordpress_password: '',
        wordstat_client_id: '',
        wordstat_client_secret: '',
        wordstat_redirect_uri: '',
        telegram_bot_token: '',
        telegram_webhook_url: '',
        telegram_webhook_secret: '',
        mcp_sse_url: '',
        mcp_connector_id: '',
        timezone: 'UTC',
        language: 'ru',
      }),
      []
    ),
  })

  const watchValues = watch()

  // Функция проверки Telegram бота
  const testTelegramBot = async () => {
    setTelegramTestResult({ status: 'testing', message: 'Проверяем Telegram бота...' })
    
    try {
      // 1. Сначала сохраняем настройки
      const settingsData = {
        telegram_bot_token: watchValues.telegram_bot_token,
        telegram_webhook_url: watchValues.telegram_webhook_url,
        telegram_webhook_secret: watchValues.telegram_webhook_secret
      }

      const saveResponse = await fetch('/api/user/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.token}`
        },
        body: JSON.stringify(settingsData)
      })

      if (!saveResponse.ok) {
        throw new Error('Ошибка сохранения настроек')
      }

      // 2. Проверяем токен через Telegram API
      const checkResponse = await fetch('/api/telegram/check-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.token}`
        }
      })

      const checkData = await checkResponse.json()
      
      if (checkData.success) {
        setTelegramTestResult({ 
          status: 'success', 
          message: `✅ Telegram бот работает! Имя: ${checkData.bot_name || 'Неизвестно'}` 
        })
      } else {
        setTelegramTestResult({ 
          status: 'error', 
          message: `❌ Ошибка: ${checkData.error}` 
        })
      }

    } catch (error) {
      setTelegramTestResult({ 
        status: 'error', 
        message: `❌ Ошибка проверки: ${error}` 
      })
    }
  }

  useEffect(() => {
    fetchSettings()
  }, [])

  async function fetchSettings() {
    try {
      const response = await fetch('/api/user/settings', {
        headers: {
          'Authorization': `Bearer ${user?.token}`
        }
      })
      const data = await response.json()
      setSettings(data)
      
      // Заполняем форму данными
      Object.keys(data).forEach(key => {
        if (data[key] !== null && data[key] !== undefined) {
          setValue(key as keyof SettingsFormData, data[key])
        }
      })
    } catch (error) {
      console.error('Ошибка загрузки настроек:', error)
    }
  }

  const onSubmit = async (data: SettingsFormData) => {
    setIsLoading(true)
    setMessage('')
    
    try {
      const response = await fetch('/api/user/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.token}`
        },
        body: JSON.stringify(data)
      })
      
      if (response.ok) {
        setMessage('Настройки сохранены успешно!')
        await fetchSettings()
      } else {
        const errorData = await response.json()
        setMessage(`Ошибка: ${errorData.detail || 'Неизвестная ошибка'}`)
      }
    } catch (error) {
      setMessage(`Ошибка: ${error}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="glass-panel">
        <h3 className="text-xl font-bold text-foreground mb-6">⚙️ Настройки</h3>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* WordPress Settings */}
          <div className="glass-panel">
            <h3 className="text-xl font-bold text-foreground mb-6 flex items-center">
              📝 WordPress настройки
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-2">
                  URL сайта
                </label>
                <input
                  {...register('wordpress_url')}
                  type="url"
                  className="modern-input w-full"
                  placeholder="https://example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-2">
                  Имя пользователя
                </label>
                <input
                  {...register('wordpress_username')}
                  type="text"
                  className="modern-input w-full"
                  placeholder="admin"
                />
              </div>
              <PasswordField
                label="Пароль приложения"
                name="wordpress_password"
                value={watchValues.wordpress_password}
                onChange={(value) => setValue('wordpress_password', value, { shouldDirty: true })}
                placeholder="xxxx xxxx xxxx xxxx xxxx xxxx"
                className="md:col-span-2"
              />
            </div>
          </div>

          {/* Wordstat Settings */}
          <div className="glass-panel">
            <h3 className="text-xl font-bold text-foreground mb-6 flex items-center">
              📊 Wordstat настройки
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
                  placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                />
              </div>
              <PasswordField
                label="Client Secret"
                name="wordstat_client_secret"
                value={watchValues.wordstat_client_secret}
                onChange={(value) => setValue('wordstat_client_secret', value, { shouldDirty: true })}
                placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
              />
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-2">
                  Redirect URI
                </label>
                <input
                  {...register('wordstat_redirect_uri')}
                  type="url"
                  className="modern-input w-full"
                  placeholder="https://www.make.com/oauth/cb/app"
                />
              </div>
            </div>
          </div>

          {/* Telegram Bot Settings */}
          <div className="glass-panel">
            <h3 className="text-xl font-bold text-foreground mb-6 flex items-center">
              🤖 Telegram Bot настройки
            </h3>
            
            {/* Инструкция по созданию бота */}
            <div className="glass-form p-4 mb-6 border-l-4 border-blue-400/50">
              <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center">
                💡 Как создать Telegram бота:
              </h4>
              <ol className="text-sm text-foreground/70 space-y-2 list-decimal list-inside">
                <li>Найдите <strong>@BotFather</strong> в Telegram</li>
                <li>Отправьте команду <code className="text-xs bg-white/10 px-2 py-1 rounded">/newbot</code></li>
                <li>Введите имя для вашего бота (например: "My Awesome Bot")</li>
                <li>Введите username для бота (например: "my_awesome_bot")</li>
                <li>Скопируйте полученный токен и вставьте в поле ниже</li>
              </ol>
              <p className="text-xs text-foreground/50 mt-3">
                🔐 <strong>Безопасность:</strong> Токен бота дает полный доступ к управлению ботом. Храните его в безопасности!
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <PasswordField
                label="Токен бота"
                name="telegram_bot_token"
                value={watchValues.telegram_bot_token}
                onChange={(value) => setValue('telegram_bot_token', value, { shouldDirty: true })}
                placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                className="md:col-span-2"
              />
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-2">
                  Webhook URL (опционально)
                </label>
                <input
                  {...register('telegram_webhook_url')}
                  type="url"
                  className="modern-input w-full"
                  placeholder="https://your-domain.com/webhook"
                />
                <p className="text-xs text-foreground/50 mt-1">URL для получения обновлений от Telegram</p>
              </div>
              <PasswordField
                label="Webhook Secret (опционально)"
                name="telegram_webhook_secret"
                value={watchValues.telegram_webhook_secret}
                onChange={(value) => setValue('telegram_webhook_secret', value, { shouldDirty: true })}
                placeholder="your-secret-key"
              />
            </div>

            {/* КНОПКА ПРОВЕРКИ TELEGRAM БОТА */}
            <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-semibold text-blue-600">🔍 Проверка Telegram бота</h4>
                <button
                  type="button"
                  onClick={testTelegramBot}
                  disabled={!watchValues.telegram_bot_token || telegramTestResult.status === 'testing'}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    watchValues.telegram_bot_token && telegramTestResult.status !== 'testing'
                      ? 'bg-blue-600 hover:bg-blue-700 text-white'
                      : 'bg-gray-400 text-gray-200 cursor-not-allowed'
                  }`}
                >
                  {telegramTestResult.status === 'testing' ? '⏳ Проверяем...' : '🔍 Проверить бота'}
                </button>
              </div>
              
              {/* Результат проверки */}
              {telegramTestResult.status !== 'idle' && (
                <div className={`p-3 rounded-lg text-sm ${
                  telegramTestResult.status === 'success' ? 'bg-green-500/10 text-green-600 border border-green-500/20' :
                  telegramTestResult.status === 'error' ? 'bg-red-500/10 text-red-600 border border-red-500/20' :
                  'bg-blue-500/10 text-blue-600 border border-blue-500/20'
                }`}>
                  {telegramTestResult.message}
                </div>
              )}
              
              <p className="text-xs text-foreground/50 mt-2">
                💡 Кнопка сохранит настройки и проверит доступность бота через Telegram API
              </p>
            </div>
          </div>

          {/* MCP Settings */}
          <div className="glass-panel">
            <h3 className="text-xl font-bold text-foreground mb-6 flex items-center">
              🔗 MCP настройки
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-2">
                  SSE URL
                </label>
                <input
                  {...register('mcp_sse_url')}
                  type="url"
                  className="modern-input w-full"
                  placeholder="https://mcp-kv.ru/mcp/sse/connector-id"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-2">
                  Connector ID
                </label>
                <input
                  {...register('mcp_connector_id')}
                  type="text"
                  className="modern-input w-full"
                  placeholder="user-xxxxxxxxxxxxxxxx"
                />
              </div>
            </div>
          </div>

          {/* General Settings */}
          <div className="glass-panel">
            <h3 className="text-xl font-bold text-foreground mb-6 flex items-center">
              🌍 Общие настройки
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-2">
                  Часовой пояс
                </label>
                <select {...register('timezone')} className="modern-input w-full">
                  <option value="UTC">UTC</option>
                  <option value="Europe/Moscow">Москва (UTC+3)</option>
                  <option value="Europe/Kiev">Киев (UTC+2)</option>
                  <option value="America/New_York">Нью-Йорк (UTC-5)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-2">
                  Язык
                </label>
                <select {...register('language')} className="modern-input w-full">
                  <option value="ru">Русский</option>
                  <option value="en">English</option>
                </select>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isLoading || !isDirty}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                isDirty && !isLoading
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-400 text-gray-200 cursor-not-allowed'
              }`}
            >
              {isLoading ? 'Сохранение...' : 'Сохранить настройки'}
            </button>
          </div>

          {/* Message */}
          {message && (
            <div className={`p-4 rounded-lg ${
              message.includes('успешно') 
                ? 'bg-green-500/10 text-green-600 border border-green-500/20'
                : 'bg-red-500/10 text-red-600 border border-red-500/20'
            }`}>
              {message}
            </div>
          )}
        </form>
      </div>
    </div>
  )
}
EOF

# 5. ПЕРЕСОБИРАЕМ FRONTEND
echo "5️⃣ Пересобираем frontend..."
cd frontend
rm -rf .next
npm run build

# 6. ПЕРЕЗАПУСКАЕМ FRONTEND
echo "6️⃣ Перезапускаем frontend..."
pm2 restart frontend

# 7. ПРОВЕРЯЕМ СТАТУС
echo "7️⃣ Проверяем статус..."
pm2 status

echo ""
echo "🎯 SETTINGS PANEL ИСПРАВЛЕН!"
echo "✅ Кнопка '🔍 Проверить бота' добавлена"
echo "✅ Функция testTelegramBot добавлена"
echo "✅ Состояние telegramTestResult добавлено"
echo "✅ Frontend пересобран и перезапущен"
echo ""
echo "🔍 Теперь зайди на сайт и проверь настройки!"
