'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'
import { useAuthStore } from '@/store/authStore'

interface UserStats {
  total_actions: number
  actions_by_type: Record<string, number>
  recent_activities: Activity[]
  connections: {
    wordpress: boolean
    wordstat: boolean
    mcp: boolean
  }
  daily_activity: DailyActivity[]
  user_info: {
    email: string
    full_name: string
    created_at: string
    days_since_registration: number
  }
}

interface Activity {
  id: number
  action_type: string
  action_name: string
  status: string
  created_at: string
  details?: string
}

interface DailyActivity {
  date: string
  count: number
}

export default function StatsPanel() {
  const { token } = useAuthStore()
  const [stats, setStats] = useState<UserStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      fetchStats()
    }
  }, [token])

  async function fetchStats() {
    try {
      const response = await axios.get<UserStats>('/api/user/stats', {
        headers: { Authorization: `Bearer ${token}` },
      })
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="glass-panel p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="glass-panel p-8 text-center">
        <p className="text-foreground/70">Не удалось загрузить статистику</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Заголовок */}
      <div className="text-center">
        <h2 className="text-3xl font-bold gradient-text mb-2">📊 Статистика</h2>
        <p className="text-foreground/70">Ваша активность и использование платформы</p>
      </div>

      {/* Основные метрики */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-panel p-6 text-center hover:scale-105 transition-transform">
          <div className="text-4xl mb-2">🎯</div>
          <div className="text-3xl font-bold text-indigo-600 mb-1">
            {stats.total_actions}
          </div>
          <div className="text-sm text-foreground/70">Всего действий</div>
        </div>

        <div className="glass-panel p-6 text-center hover:scale-105 transition-transform">
          <div className="text-4xl mb-2">📅</div>
          <div className="text-3xl font-bold text-green-600 mb-1">
            {stats.user_info.days_since_registration}
          </div>
          <div className="text-sm text-foreground/70">Дней на платформе</div>
        </div>

        <div className="glass-panel p-6 text-center hover:scale-105 transition-transform">
          <div className="text-4xl mb-2">🔌</div>
          <div className="text-3xl font-bold text-blue-600 mb-1">
            {Object.values(stats.connections).filter(Boolean).length}/3
          </div>
          <div className="text-sm text-foreground/70">Активных подключений</div>
        </div>

        <div className="glass-panel p-6 text-center hover:scale-105 transition-transform">
          <div className="text-4xl mb-2">✅</div>
          <div className="text-3xl font-bold text-purple-600 mb-1">
            {stats.recent_activities.filter(a => a.status === 'success').length}
          </div>
          <div className="text-sm text-foreground/70">Успешных операций</div>
        </div>
      </div>

      {/* Статистика по сервисам */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-6">
          <h3 className="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
            📊 Использование по сервисам
          </h3>
          <div className="space-y-3">
            {Object.entries(stats.actions_by_type).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${
                    type === 'wordpress' ? 'bg-blue-500' :
                    type === 'wordstat' ? 'bg-green-500' :
                    type === 'settings' ? 'bg-purple-500' :
                    'bg-gray-500'
                  }`}></div>
                  <span className="text-foreground capitalize">{type}</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-32 bg-foreground/10 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        type === 'wordpress' ? 'bg-blue-500' :
                        type === 'wordstat' ? 'bg-green-500' :
                        type === 'settings' ? 'bg-purple-500' :
                        'bg-gray-500'
                      }`}
                      style={{ width: `${(count / stats.total_actions) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-foreground font-bold w-12 text-right">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel p-6">
          <h3 className="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
            🔌 Статус подключений
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 glass-form rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${stats.connections.wordpress ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-foreground">WordPress</span>
              </div>
              <span className={`text-sm ${stats.connections.wordpress ? 'text-green-600' : 'text-red-600'}`}>
                {stats.connections.wordpress ? 'Подключен' : 'Не настроен'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 glass-form rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${stats.connections.wordstat ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-foreground">Wordstat</span>
              </div>
              <span className={`text-sm ${stats.connections.wordstat ? 'text-green-600' : 'text-red-600'}`}>
                {stats.connections.wordstat ? 'Подключен' : 'Не настроен'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 glass-form rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-blue-500 animate-pulse"></div>
                <span className="text-foreground">MCP Server</span>
              </div>
              <span className="text-sm text-blue-600">Активен</span>
            </div>
          </div>
        </div>
      </div>

      {/* Последняя активность */}
      <div className="glass-panel p-6">
        <h3 className="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
          🕐 Последняя активность
        </h3>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {stats.recent_activities.map((activity) => (
            <div key={activity.id} className="glass-form p-4 rounded-lg flex items-center justify-between hover:bg-foreground/5 transition-colors">
              <div className="flex items-center gap-4">
                <div className={`w-2 h-2 rounded-full ${activity.status === 'success' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <div>
                  <div className="text-foreground font-medium">{activity.action_name}</div>
                  <div className="text-sm text-foreground/60 capitalize">{activity.action_type}</div>
                </div>
              </div>
              <div className="text-right">
                <div className={`text-sm font-medium ${activity.status === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                  {activity.status === 'success' ? 'Успешно' : 'Ошибка'}
                </div>
                <div className="text-xs text-foreground/60">
                  {new Date(activity.created_at).toLocaleString('ru-RU', {
                    day: '2-digit',
                    month: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Информация о пользователе */}
      <div className="glass-panel p-6">
        <h3 className="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
          👤 Информация об аккаунте
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-foreground/60 mb-1">Имя</div>
            <div className="text-foreground font-medium">{stats.user_info.full_name}</div>
          </div>
          <div>
            <div className="text-sm text-foreground/60 mb-1">Email</div>
            <div className="text-foreground font-medium">{stats.user_info.email}</div>
          </div>
          <div>
            <div className="text-sm text-foreground/60 mb-1">Дата регистрации</div>
            <div className="text-foreground font-medium">
              {new Date(stats.user_info.created_at).toLocaleDateString('ru-RU', {
                day: '2-digit',
                month: 'long',
                year: 'numeric'
              })}
            </div>
          </div>
          <div>
            <div className="text-sm text-foreground/60 mb-1">На платформе</div>
            <div className="text-foreground font-medium">{stats.user_info.days_since_registration} дней</div>
          </div>
        </div>
      </div>
    </div>
  )
}

