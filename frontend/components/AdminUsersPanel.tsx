'use client'

import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuthStore } from '@/store/authStore'
import { useToast } from '@/hooks/useToast'
import { motion, AnimatePresence } from 'framer-motion'

interface User {
  id: number
  email: string
  full_name: string
  is_active: boolean
  is_admin: boolean
  created_at: string
  updated_at: string
}

interface UserDetails extends User {
  settings: {
    has_wordpress: boolean
    has_wordstat: boolean
    mcp_connector_id: string | null
  } | null
  activity: {
    total_actions: number
    recent_activities: Array<{
      id: number
      action_type: string
      action_name: string
      status: string
      created_at: string
    }>
  }
}

const AdminUsersPanel: React.FC = () => {
  const { token } = useAuthStore()
  const { success, error } = useToast()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterActive, setFilterActive] = useState<boolean | null>(null)
  const [selectedUser, setSelectedUser] = useState<UserDetails | null>(null)
  const [showDetails, setShowDetails] = useState(false)

  useEffect(() => {
    fetchUsers()
  }, [searchQuery, filterActive])

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const params: any = {}
      if (searchQuery) params.search = searchQuery
      if (filterActive !== null) params.is_active = filterActive

      const response = await axios.get('/api/admin/users', {
        headers: { Authorization: `Bearer ${token}` },
        params,
      })
      setUsers(response.data.users)
    } catch (err: any) {
      console.error('Ошибка загрузки пользователей:', err)
      error(err.response?.data?.detail || 'Не удалось загрузить пользователей')
    } finally {
      setLoading(false)
    }
  }

  const fetchUserDetails = async (userId: number) => {
    try {
      const response = await axios.get<UserDetails>(`/api/admin/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setSelectedUser(response.data.user as any)
      setShowDetails(true)
    } catch (err: any) {
      console.error('Ошибка загрузки деталей:', err)
      error(err.response?.data?.detail || 'Не удалось загрузить детали пользователя')
    }
  }

  const blockUser = async (userId: number) => {
    if (!confirm('Вы уверены, что хотите заблокировать этого пользователя?')) return

    try {
      await axios.put(
        `/api/admin/users/${userId}/block`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      )
      success('Пользователь заблокирован')
      fetchUsers()
      if (selectedUser?.id === userId) {
        setShowDetails(false)
      }
    } catch (err: any) {
      error(err.response?.data?.detail || 'Не удалось заблокировать пользователя')
    }
  }

  const unblockUser = async (userId: number) => {
    try {
      await axios.put(
        `/api/admin/users/${userId}/unblock`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      )
      success('Пользователь разблокирован')
      fetchUsers()
    } catch (err: any) {
      error(err.response?.data?.detail || 'Не удалось разблокировать пользователя')
    }
  }

  const deleteUser = async (userId: number) => {
    if (!confirm('ВНИМАНИЕ! Вы действительно хотите удалить этого пользователя? Это действие необратимо!')) return

    try {
      await axios.delete(`/api/admin/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      success('Пользователь удалён')
      fetchUsers()
      if (selectedUser?.id === userId) {
        setShowDetails(false)
      }
    } catch (err: any) {
      error(err.response?.data?.detail || 'Не удалось удалить пользователя')
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Фильтры и поиск */}
      <div className="glass-panel p-6">
        <div className="flex flex-col md:flex-row gap-4">
          <input
            type="text"
            placeholder="🔍 Поиск по email или имени..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="modern-input flex-grow"
          />
          <div className="flex gap-2">
            <button
              onClick={() => setFilterActive(null)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filterActive === null
                  ? 'bg-indigo-500/20 text-white'
                  : 'bg-white/5 text-foreground/70 hover:bg-white/10'
              }`}
            >
              Все
            </button>
            <button
              onClick={() => setFilterActive(true)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filterActive === true
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-white/5 text-foreground/70 hover:bg-white/10'
              }`}
            >
              Активные
            </button>
            <button
              onClick={() => setFilterActive(false)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filterActive === false
                  ? 'bg-red-500/20 text-red-400'
                  : 'bg-white/5 text-foreground/70 hover:bg-white/10'
              }`}
            >
              Заблок.
            </button>
          </div>
        </div>
      </div>

      {/* Список пользователей */}
      {loading ? (
        <div className="glass-panel p-8 text-center text-foreground/70">Загрузка пользователей...</div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {users.map((user) => (
            <motion.div
              key={user.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="glass-panel p-6 hover:shadow-lg transition-all cursor-pointer"
              onClick={() => fetchUserDetails(user.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center text-xl font-bold ${
                      user.is_admin
                        ? 'bg-gradient-to-r from-red-500 to-orange-500'
                        : 'bg-gradient-to-r from-indigo-500 to-purple-500'
                    }`}
                  >
                    {user.full_name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-bold text-foreground">{user.full_name}</p>
                      {user.is_admin && (
                        <span className="px-2 py-1 text-xs bg-red-500/20 text-red-400 rounded-full">
                          ADMIN
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-foreground/70">{user.email}</p>
                    <p className="text-xs text-foreground/50">
                      Регистрация: {new Date(user.created_at).toLocaleDateString('ru-RU')}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div
                    className={`px-4 py-2 rounded-lg font-medium ${
                      user.is_active
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-red-500/20 text-red-400'
                    }`}
                  >
                    {user.is_active ? '✅ Активен' : '🚫 Заблокирован'}
                  </div>
                  <div className="flex gap-2">
                    {!user.is_admin && (
                      <>
                        {user.is_active ? (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              blockUser(user.id)
                            }}
                            className="px-3 py-2 bg-orange-500/20 text-orange-400 hover:bg-orange-500/30 rounded-lg transition-all"
                          >
                            🚫 Блок
                          </button>
                        ) : (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              unblockUser(user.id)
                            }}
                            className="px-3 py-2 bg-green-500/20 text-green-400 hover:bg-green-500/30 rounded-lg transition-all"
                          >
                            ✅ Разблок
                          </button>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            deleteUser(user.id)
                          }}
                          className="px-3 py-2 bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded-lg transition-all"
                        >
                          🗑️ Удалить
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Модальное окно с деталями */}
      <AnimatePresence>
        {showDetails && selectedUser && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowDetails(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 50 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 50 }}
              className="glass-panel p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold gradient-text">Детали пользователя</h3>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-foreground/70 hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-6">
                {/* Основная информация */}
                <div className="glass-form p-6 rounded-lg space-y-3">
                  <h4 className="font-bold text-foreground mb-4">📋 Основная информация</h4>
                  <p>
                    <span className="text-foreground/70">Имя:</span>{' '}
                    <span className="font-medium">{selectedUser.full_name}</span>
                  </p>
                  <p>
                    <span className="text-foreground/70">Email:</span>{' '}
                    <span className="font-medium">{selectedUser.email}</span>
                  </p>
                  <p>
                    <span className="text-foreground/70">Статус:</span>{' '}
                    <span
                      className={selectedUser.is_active ? 'text-green-400' : 'text-red-400'}
                    >
                      {selectedUser.is_active ? 'Активен' : 'Заблокирован'}
                    </span>
                  </p>
                  <p>
                    <span className="text-foreground/70">Роль:</span>{' '}
                    <span className={selectedUser.is_admin ? 'text-red-400' : 'text-blue-400'}>
                      {selectedUser.is_admin ? 'Администратор' : 'Пользователь'}
                    </span>
                  </p>
                </div>

                {/* Подключения (из activity вместо settings) */}
                <div className="glass-form p-6 rounded-lg">
                  <h4 className="font-bold text-foreground mb-4">🔌 Статистика активности</h4>
                  <p className="text-foreground/70">
                    Всего действий: <span className="font-bold gradient-text text-xl">{(selectedUser as any).activity?.total_actions || 0}</span>
                  </p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default AdminUsersPanel

