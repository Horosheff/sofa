'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import AdminDashboard from './AdminDashboard'
import AdminUsersPanel from './AdminUsersPanel'
import AdminLogsPanel from './AdminLogsPanel'

type AdminTab = 'dashboard' | 'users' | 'logs' | 'settings'

const AdminPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<AdminTab>('dashboard')

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-4xl font-bold text-gray-900 mb-2">Админ Панель</h2>
            <p className="text-gray-600 text-lg">Управление платформой и пользователями</p>
          </div>
          <div className="flex items-center gap-3 px-4 py-2 bg-red-50 rounded-lg border border-red-200">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
            <span className="text-sm font-medium text-red-700">Режим администратора</span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-2 flex gap-2">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`flex-1 px-6 py-3 rounded-xl font-semibold transition-all duration-200 ${
            activeTab === 'dashboard'
              ? 'bg-gray-900 text-white shadow-lg'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          }`}
        >
          📊 Дашборд
        </button>
        <button
          onClick={() => setActiveTab('users')}
          className={`flex-1 px-6 py-3 rounded-xl font-semibold transition-all duration-200 ${
            activeTab === 'users'
              ? 'bg-gray-900 text-white shadow-lg'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          }`}
        >
          👥 Пользователи
        </button>
        <button
          onClick={() => setActiveTab('logs')}
          className={`flex-1 px-6 py-3 rounded-xl font-semibold transition-all duration-200 ${
            activeTab === 'logs'
              ? 'bg-gray-900 text-white shadow-lg'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          }`}
        >
          📋 Логи
        </button>
        <button
          onClick={() => setActiveTab('settings')}
          className={`flex-1 px-6 py-3 rounded-xl font-semibold transition-all duration-200 ${
            activeTab === 'settings'
              ? 'bg-gray-900 text-white shadow-lg'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          }`}
        >
          ⚙️ Настройки
        </button>
      </div>

      {/* Content */}
      <div>
        {activeTab === 'dashboard' && <AdminDashboard />}
        {activeTab === 'users' && <AdminUsersPanel />}
        {activeTab === 'logs' && <AdminLogsPanel />}
        {activeTab === 'settings' && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-12 text-center">
            <p className="text-2xl font-semibold text-gray-900">⚙️ Настройки админ-панели</p>
            <p className="mt-3 text-gray-600">В разработке...</p>
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default AdminPanel

