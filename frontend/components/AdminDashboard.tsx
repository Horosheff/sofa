'use client'

import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuthStore } from '@/store/authStore'
import { useToast } from '@/hooks/useToast'
import { motion } from 'framer-motion'

interface DashboardData {
  users: {
    total: number
    active: number
    new_week: number
  }
  activity: {
    total: number
    today: number
    errors: number
  }
  top_users: Array<{
    id: number
    email: string
    full_name: string
    action_count: number
  }>
  actions_by_type: Record<string, number>
  daily_activity: Array<{ date: string; count: number }>
}

const AdminDashboard: React.FC = () => {
  const { token } = useAuthStore()
  const { error } = useToast()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboard()
  }, [])

  const fetchDashboard = async () => {
    setLoading(true)
    try {
      const response = await axios.get<DashboardData>('/api/admin/dashboard', {
        headers: { Authorization: `Bearer ${token}` },
      })
      setData(response.data)
    } catch (err: any) {
      console.error('Ошибка загрузки дашборда:', err)
      error(err.response?.data?.detail || 'Не удалось загрузить дашборд')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center">
        <p className="text-gray-600">Загрузка дашборда...</p>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center">
        <p className="text-red-600">Не удалось загрузить дашборд</p>
      </div>
    )
  }

  const maxActions = Math.max(...Object.values(data.actions_by_type), 1)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Основные метрики */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <motion.div
          className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <div className="flex items-center justify-between mb-4">
            <span className="text-4xl">👥</span>
            <div className="text-right">
              <p className="text-3xl font-bold text-gray-900">{data.users.total}</p>
              <p className="text-sm text-gray-600">Всего пользователей</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
              <p className="text-green-600 font-bold text-lg">{data.users.active}</p>
              <p className="text-gray-600 mt-1">Активных</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
              <p className="text-blue-600 font-bold text-lg">{data.users.new_week}</p>
              <p className="text-gray-600 mt-1">За неделю</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="flex items-center justify-between mb-4">
            <span className="text-4xl">⚡</span>
            <div className="text-right">
              <p className="text-3xl font-bold text-gray-900">{data.activity.total}</p>
              <p className="text-sm text-gray-600">Всего действий</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
              <p className="text-blue-600 font-bold text-lg">{data.activity.today}</p>
              <p className="text-gray-600 mt-1">Сегодня</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
              <p className="text-red-600 font-bold text-lg">{data.activity.errors}</p>
              <p className="text-gray-600 mt-1">Ошибок</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="flex items-center justify-between mb-4">
            <span className="text-4xl">📈</span>
            <div className="text-right">
              <p className="text-3xl font-bold text-gray-900">
                {data.activity.errors > 0
                  ? Math.round(((data.activity.total - data.activity.errors) / data.activity.total) * 100)
                  : 100}%
              </p>
              <p className="text-sm text-gray-600">Успешность</p>
            </div>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
            <p className="text-gray-600">
              {data.activity.total - data.activity.errors} успешных из {data.activity.total}
            </p>
          </div>
        </motion.div>
      </div>

      {/* Активность по типам */}
      <motion.div
        className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <h3 className="text-xl font-semibold text-gray-900 mb-6">📊 Активность по сервисам</h3>
        <div className="space-y-4">
          {Object.entries(data.actions_by_type).map(([type, count]) => (
            <div key={type} className="flex items-center space-x-4">
              <span className="w-28 text-gray-700 capitalize font-medium">{type}</span>
              <div className="flex-grow bg-gray-200 rounded-full h-3">
                <motion.div
                  className="h-full rounded-full bg-gray-900"
                  initial={{ width: 0 }}
                  animate={{ width: `${(count / maxActions) * 100}%` }}
                  transition={{ duration: 1, delay: 0.5 }}
                ></motion.div>
              </div>
              <span className="text-gray-900 font-bold w-12 text-right">{count}</span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Топ активных пользователей */}
      <motion.div
        className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h3 className="text-xl font-semibold text-gray-900 mb-6">🏆 Топ активных пользователей</h3>
        <div className="space-y-3">
          {data.top_users.slice(0, 5).map((user, index) => (
            <div key={user.id} className="bg-gray-50 p-4 rounded-xl border border-gray-200 flex items-center justify-between hover:bg-gray-100 transition-colors">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 rounded-full bg-gray-900 flex items-center justify-center font-bold text-white text-lg">
                  {index + 1}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{user.full_name}</p>
                  <p className="text-sm text-gray-600">{user.email}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-gray-900">{user.action_count}</p>
                <p className="text-xs text-gray-600">действий</p>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  )
}

export default AdminDashboard

