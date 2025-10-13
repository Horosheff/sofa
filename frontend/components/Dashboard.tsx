'use client'

import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import SettingsPanel from './SettingsPanel'
import ToolsPanel from './ToolsPanel'

export default function Dashboard() {
  const { logout, user } = useAuthStore()
  const [activeTab, setActiveTab] = useState<'tools' | 'settings'>('tools')

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <div className="animated-bg"></div>
      
      {/* Header */}
      <header className="glass-dark border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold gradient-text">MCP KOV4EG</h1>
              <p className="text-white/70 mt-1">Добро пожаловать, {user?.full_name || user?.email}!</p>
            </div>
            <button
              onClick={logout}
              className="btn-primary bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600"
            >
              Выйти
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="glass-dark border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('tools')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-all duration-300 ${
                activeTab === 'tools'
                  ? 'border-indigo-400 text-indigo-300'
                  : 'border-transparent text-white/60 hover:text-white/80 hover:border-white/30'
              }`}
            >
              🛠️ Инструменты
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-all duration-300 ${
                activeTab === 'settings'
                  ? 'border-indigo-400 text-indigo-300'
                  : 'border-transparent text-white/60 hover:text-white/80 hover:border-white/30'
              }`}
            >
              ⚙️ Настройки
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'tools' && <ToolsPanel />}
        {activeTab === 'settings' && <SettingsPanel />}
      </main>
    </div>
  )
}