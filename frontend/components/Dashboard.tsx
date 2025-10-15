'use client'

import { useState } from 'react'
import ToolsPanel from '@/components/ToolsPanel'
import SettingsPanel from '@/components/SettingsPanel'
import { useAuthStore } from '@/store/authStore'

export default function Dashboard() {
  const { user, logout } = useAuthStore()
  const [activeTab, setActiveTab] = useState<'tools' | 'settings'>('tools')

  return (
    <div className="min-h-screen text-foreground">
      <header className="glass-nav mx-auto max-w-6xl mt-4 mb-4">
        <div className="flex items-center justify-between px-4 py-3">
          {/* Логотип и название */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-md flex items-center justify-center">
              <span className="text-white font-bold text-sm">M</span>
            </div>
            <div>
              <h1 className="text-lg font-bold gradient-text">MCP Platform</h1>
              <p className="text-xs text-foreground/50">
                Управление подключениями и инструментами
              </p>
            </div>
          </div>

          {/* Пользователь и действия */}
          <div className="flex items-center gap-3">
            {/* Статус подключений */}
            <div className="hidden md:flex items-center gap-2">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-foreground/60">MCP</span>
              </div>
            </div>

            {/* Telegram логотип */}
            <a 
              href="https://t.me/maya_pro" 
              target="_blank" 
              rel="noopener noreferrer"
              className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center hover:scale-110 transition-transform duration-200 shadow-lg"
            >
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
              </svg>
            </a>

            {/* Профиль пользователя */}
            <div className="flex items-center gap-2">
              <div className="text-right">
                <p className="font-medium text-sm text-foreground">{user?.full_name || 'Пользователь'}</p>
                <p className="text-xs text-foreground/50">{user?.email || 'email@example.com'}</p>
              </div>
              <div className="w-7 h-7 bg-gradient-to-br from-gray-400 to-gray-600 rounded-full flex items-center justify-center text-white font-medium text-xs">
                {user?.full_name?.charAt(0) || 'П'}
              </div>
              <button
                onClick={logout}
                className="modern-button bg-red-500/10 border-red-500/20 text-red-600 hover:bg-red-500/20 px-2 py-1 text-xs"
              >
                Выйти
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">
        {/* Navigation Tabs */}
        <div className="mb-10">
          <div className="glass-panel p-1">
            <div className="flex space-x-1">
              <button
                onClick={() => setActiveTab('tools')}
                className={`glass-tab px-8 py-4 font-semibold transition-all duration-300 ${
                  activeTab === 'tools' 
                    ? 'bg-gradient-to-r from-indigo-500/20 to-purple-500/20 border-indigo-400/50 shadow-lg' 
                    : 'hover:bg-white/5'
                }`}
              >
                <span className="flex items-center gap-3">
                  <span className="text-lg">🛠️</span>
                  <span>Инструменты</span>
                </span>
              </button>
              <button
                onClick={() => setActiveTab('settings')}
                className={`glass-tab px-8 py-4 font-semibold transition-all duration-300 ${
                  activeTab === 'settings' 
                    ? 'bg-gradient-to-r from-indigo-500/20 to-purple-500/20 border-indigo-400/50 shadow-lg' 
                    : 'hover:bg-white/5'
                }`}
              >
                <span className="flex items-center gap-3">
                  <span className="text-lg">⚙️</span>
                  <span>Настройки</span>
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'tools' && <ToolsPanel />}
        {activeTab === 'settings' && <SettingsPanel />}
      </main>
    </div>
  )
}