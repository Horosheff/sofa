'use client'

import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuthStore } from '@/store/authStore'
import { useToast } from '@/hooks/useToast'
import { motion } from 'framer-motion'

interface ActivityLog {
  id: number
  user_id: number
  action_type: string
  action_name: string
  status: string
  details: string | null
  error_message: string | null
  ip_address: string | null
  created_at: string
}

interface AdminLog {
  id: number
  admin_user_id: number
  action_type: string
  action_description: string
  target_user_id: number | null
  changes: any
  ip_address: string | null
  created_at: string
}

const AdminLogsPanel: React.FC = () => {
  const { token } = useAuthStore()
  const { error } = useToast()
  const [activeLogType, setActiveLogType] = useState<'activity' | 'admin'>('activity')
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([])
  const [adminLogs, setAdminLogs] = useState<AdminLog[]>([])
  const [loading, setLoading] = useState(true)
  const [filterType, setFilterType] = useState<string>('')
  const [filterStatus, setFilterStatus] = useState<string>('')

  useEffect(() => {
    if (activeLogType === 'activity') {
      fetchActivityLogs()
    } else {
      fetchAdminLogs()
    }
  }, [activeLogType, filterType, filterStatus])

  const fetchActivityLogs = async () => {
    setLoading(true)
    try {
      const params: any = { limit: 100 }
      if (filterType) params.action_type = filterType
      if (filterStatus) params.status = filterStatus

      const response = await axios.get('/api/admin/logs', {
        headers: { Authorization: `Bearer ${token}` },
        params,
      })
      setActivityLogs(response.data.logs)
    } catch (err: any) {
      console.error('Ошибка загрузки логов:', err)
      error(err.response?.data?.detail || 'Не удалось загрузить логи')
    } finally {
      setLoading(false)
    }
  }

  const fetchAdminLogs = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/admin/admin-logs', {
        headers: { Authorization: `Bearer ${token}` },
        params: { limit: 50 },
      })
      setAdminLogs(response.data.logs)
    } catch (err: any) {
      console.error('Ошибка загрузки админ логов:', err)
      error(err.response?.data?.detail || 'Не удалось загрузить админ логи')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-400 bg-green-500/20'
      case 'error':
        return 'text-red-400 bg-red-500/20'
      case 'pending':
        return 'text-yellow-400 bg-yellow-500/20'
      default:
        return 'text-foreground/70 bg-white/5'
    }
  }

  const getActionTypeIcon = (type: string) => {
    switch (type) {
      case 'wordpress':
        return '📝'
      case 'wordstat':
        return '📊'
      case 'settings':
        return '⚙️'
      case 'mcp':
        return '🔌'
      case 'user_block':
        return '🚫'
      case 'user_unblock':
        return '✅'
      case 'user_delete':
        return '🗑️'
      default:
        return '📋'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Переключатель типа логов */}
      <div className="glass-panel p-2 flex gap-2">
        <button
          onClick={() => setActiveLogType('activity')}
          className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${
            activeLogType === 'activity'
              ? 'bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-white shadow-lg'
              : 'text-foreground/70 hover:bg-white/5'
          }`}
        >
          📋 Логи активности
        </button>
        <button
          onClick={() => setActiveLogType('admin')}
          className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${
            activeLogType === 'admin'
              ? 'bg-gradient-to-r from-red-500/20 to-orange-500/20 text-white shadow-lg'
              : 'text-foreground/70 hover:bg-white/5'
          }`}
        >
          🔐 Логи администратора
        </button>
      </div>

      {/* Фильтры для логов активности */}
      {activeLogType === 'activity' && (
        <div className="glass-panel p-4 flex gap-4">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="modern-input flex-1"
          >
            <option value="">Все типы</option>
            <option value="wordpress">WordPress</option>
            <option value="wordstat">Wordstat</option>
            <option value="settings">Настройки</option>
            <option value="mcp">MCP</option>
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="modern-input flex-1"
          >
            <option value="">Все статусы</option>
            <option value="success">Успешно</option>
            <option value="error">Ошибка</option>
            <option value="pending">В процессе</option>
          </select>
        </div>
      )}

      {/* Логи */}
      {loading ? (
        <div className="glass-panel p-8 text-center text-foreground/70">Загрузка логов...</div>
      ) : (
        <div className="space-y-3">
          {activeLogType === 'activity' ? (
            activityLogs.length > 0 ? (
              activityLogs.map((log) => (
                <motion.div
                  key={log.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="glass-panel p-4"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4 flex-grow">
                      <span className="text-3xl">{getActionTypeIcon(log.action_type)}</span>
                      <div className="flex-grow">
                        <div className="flex items-center gap-3 mb-2">
                          <p className="font-bold text-foreground">{log.action_name}</p>
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                              log.status
                            )}`}
                          >
                            {log.status === 'success'
                              ? 'Успешно'
                              : log.status === 'error'
                              ? 'Ошибка'
                              : 'В процессе'}
                          </span>
                          <span className="px-3 py-1 bg-white/5 rounded-full text-xs text-foreground/70 capitalize">
                            {log.action_type}
                          </span>
                        </div>
                        <div className="text-sm text-foreground/70 space-y-1">
                          <p>User ID: {log.user_id}</p>
                          {log.ip_address && <p>IP: {log.ip_address}</p>}
                          {log.error_message && (
                            <p className="text-red-400 mt-2">⚠️ {log.error_message}</p>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="text-right text-sm text-foreground/70 whitespace-nowrap ml-4">
                      <p>{new Date(log.created_at).toLocaleDateString('ru-RU')}</p>
                      <p>{new Date(log.created_at).toLocaleTimeString('ru-RU')}</p>
                    </div>
                  </div>
                </motion.div>
              ))
            ) : (
              <div className="glass-panel p-8 text-center text-foreground/70">
                Логи активности не найдены
              </div>
            )
          ) : adminLogs.length > 0 ? (
            adminLogs.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="glass-panel p-4 border-l-4 border-red-500"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-grow">
                    <span className="text-3xl">{getActionTypeIcon(log.action_type)}</span>
                    <div className="flex-grow">
                      <div className="flex items-center gap-3 mb-2">
                        <p className="font-bold text-foreground">{log.action_description}</p>
                        <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-xs font-medium">
                          ADMIN
                        </span>
                      </div>
                      <div className="text-sm text-foreground/70 space-y-1">
                        <p>Admin User ID: {log.admin_user_id}</p>
                        {log.target_user_id && <p>Target User ID: {log.target_user_id}</p>}
                        {log.ip_address && <p>IP: {log.ip_address}</p>}
                        {log.changes && (
                          <details className="mt-2">
                            <summary className="cursor-pointer text-blue-400 hover:text-blue-300">
                              Показать изменения
                            </summary>
                            <pre className="mt-2 p-3 bg-black/30 rounded text-xs overflow-x-auto">
                              {JSON.stringify(log.changes, null, 2)}
                            </pre>
                          </details>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="text-right text-sm text-foreground/70 whitespace-nowrap ml-4">
                    <p>{new Date(log.created_at).toLocaleDateString('ru-RU')}</p>
                    <p>{new Date(log.created_at).toLocaleTimeString('ru-RU')}</p>
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="glass-panel p-8 text-center text-foreground/70">
              Логи администратора не найдены
            </div>
          )}
        </div>
      )}
    </motion.div>
  )
}

export default AdminLogsPanel

