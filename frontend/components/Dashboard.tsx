'use client'

import { useState } from 'react'
import ToolsPanel from '@/components/ToolsPanel'
import SettingsPanel from '@/components/SettingsPanel'
import WordstatOAuth from '@/components/WordstatOAuth'
import { useAuthStore } from '@/store/authStore'

export default function Dashboard() {
  const { user, logout } = useAuthStore()
  const [activeTab, setActiveTab] = useState<'tools' | 'settings' | 'oauth'>('tools')

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <header className="border-b border-white/10 bg-slate-950/60 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-start justify-between px-6 py-6">
          <div>
            <h1 className="text-2xl font-semibold">Панель управления</h1>
            <p className="text-sm text-white/60">
              MCP KOV4EG • Управление подключениями и инструментами
            </p>
          </div>

          <div className="text-right">
            <p className="font-medium text-lg">{user?.full_name || 'Пользователь'}</p>
            <p className="text-sm text-white/60">{user?.email || 'email@example.com'}</p>
            <button
              onClick={logout}
              className="mt-4 rounded-md bg-red-600 px-4 py-2 text-sm font-semibold hover:bg-red-500 transition"
            >
              Выйти
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">
        {/* Navigation Tabs */}
        <div className="mb-8">
          <div className="flex space-x-1 bg-slate-800/50 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('tools')}
              className={`px-6 py-3 rounded-md font-medium transition-all ${
                activeTab === 'tools'
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'text-white/70 hover:text-white hover:bg-white/10'
              }`}
            >
              🛠️ Инструменты
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`px-6 py-3 rounded-md font-medium transition-all ${
                activeTab === 'settings'
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'text-white/70 hover:text-white hover:bg-white/10'
              }`}
            >
              ⚙️ Настройки
            </button>
            <button
              onClick={() => setActiveTab('oauth')}
              className={`px-6 py-3 rounded-md font-medium transition-all ${
                activeTab === 'oauth'
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'text-white/70 hover:text-white hover:bg-white/10'
              }`}
            >
              🔐 Wordstat OAuth
            </button>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'tools' && <ToolsPanel />}
        {activeTab === 'settings' && <SettingsPanel />}
        {activeTab === 'oauth' && (
          <div className="max-w-4xl">
            <WordstatOAuth onTokenReceived={(token) => {
              console.log('Token received:', token);
              // Можно добавить уведомление или обновление состояния
            }} />
          </div>
        )}
      </main>
    </div>
  )
}