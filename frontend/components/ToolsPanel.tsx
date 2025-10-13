'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import { useAuthStore } from '@/store/authStore'

interface Tool {
  name: string
  description: string
  category: string
  params: Record<string, any>
}

interface UserSettings {
  has_wordpress_credentials: boolean
  has_wordstat_credentials: boolean
}

export default function ToolsPanel() {
  const [tools, setTools] = useState<Record<string, string[]>>({})
  const [selectedTool, setSelectedTool] = useState<string>('')
  const [params, setParams] = useState<Record<string, any>>({})
  const [result, setResult] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [settings, setSettings] = useState<UserSettings>({})
  const { token } = useAuthStore()

  useEffect(() => {
    loadTools()
    loadSettings()
  }, [])

  const loadTools = async () => {
    try {
      const response = await axios.get('/api/mcp/tools')
      setTools(response.data)
    } catch (error) {
      console.error('Ошибка загрузки инструментов:', error)
    }
  }

  const loadSettings = async () => {
    try {
      const response = await axios.get('/api/user/settings', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setSettings(response.data)
    } catch (error) {
      console.error('Ошибка загрузки настроек:', error)
    }
  }

  const executeTool = async () => {
    if (!selectedTool) return
    
    setIsLoading(true)
    setResult(null)
    
    try {
      const response = await axios.post('/api/mcp/execute', {
        tool: selectedTool,
        params: params
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setResult(response.data)
    } catch (error: any) {
      setResult({
        success: false,
        message: error.response?.data?.detail || 'Ошибка выполнения команды'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const getToolDescription = (tool: string): string => {
    const descriptions: Record<string, string> = {
      // WordPress tools
      'create_post': 'Создать новый пост в WordPress',
      'update_post': 'Обновить существующий пост',
      'get_posts': 'Получить список постов',
      'delete_post': 'Удалить пост',
      'search_posts': 'Поиск постов',
      'bulk_update_posts': 'Массовое обновление постов',
      'create_category': 'Создать категорию',
      'get_categories': 'Получить список категорий',
      'update_category': 'Обновить категорию',
      'delete_category': 'Удалить категорию',
      'upload_media': 'Загрузить медиафайл',
      'upload_image_from_url': 'Загрузить изображение по URL',
      'get_media': 'Получить список медиафайлов',
      'delete_media': 'Удалить медиафайл',
      'create_comment': 'Создать комментарий',
      'get_comments': 'Получить комментарии',
      'update_comment': 'Обновить комментарий',
      'delete_comment': 'Удалить комментарий',
      
      // Wordstat tools
      'set_wordstat_token': 'Установить токен Wordstat',
      'get_wordstat_regions_tree': 'Получить дерево регионов',
      'get_wordstat_top_requests': 'Получить топ запросов',
      'get_wordstat_dynamics': 'Получить динамику запросов',
      'get_wordstat_regions': 'Получить регионы',
      'get_wordstat_user_info': 'Получить информацию о пользователе',
      'auto_setup_wordstat': 'Автоматическая настройка Wordstat',
      
      // Google tools
      'google_trends': 'Получить тренды Google',
      'google_search_volume': 'Объем поиска в Google',
      'google_keywords': 'Анализ ключевых слов Google',
      'google_analytics': 'Данные Google Analytics',
      'google_ads': 'Управление Google Ads',
      'youtube_analytics': 'Аналитика YouTube',
      'google_maps': 'Данные Google Maps'
    }
    return descriptions[tool] || 'Описание недоступно'
  }

  const getDefaultParams = (tool: string): Record<string, any> => {
    const defaults: Record<string, Record<string, any>> = {
      'create_post': { title: '', content: '', status: 'draft' },
      'update_post': { post_id: '', title: '', content: '' },
      'get_posts': { per_page: 10, page: 1 },
      'delete_post': { post_id: '' },
      'search_posts': { search: '', per_page: 10 },
      'bulk_update_posts': { post_ids: [], updates: {} },
      'create_category': { name: '', description: '' },
      'get_categories': { per_page: 10 },
      'update_category': { category_id: '', name: '', description: '' },
      'delete_category': { category_id: '' },
      'upload_media': { file_path: '', alt_text: '' },
      'upload_image_from_url': { image_url: '', alt_text: '' },
      'get_media': { per_page: 10 },
      'delete_media': { media_id: '' },
      'create_comment': { post_id: '', content: '', author: '' },
      'get_comments': { post_id: '', per_page: 10 },
      'update_comment': { comment_id: '', content: '' },
      'delete_comment': { comment_id: '' },
      'set_wordstat_token': { token: '' },
      'get_wordstat_regions_tree': {},
      'get_wordstat_top_requests': { phrase: '', regions: [] },
      'get_wordstat_dynamics': { phrase: '', regions: [] },
      'get_wordstat_regions': {},
      'get_wordstat_user_info': {},
      'auto_setup_wordstat': {}
    }
    return defaults[tool] || {}
  }

  const canUseTool = (tool: string): boolean => {
    if (tool.startsWith('wordpress_')) {
      return settings.has_wordpress_credentials
    }
    if (tool.startsWith('wordstat_')) {
      return settings.has_wordstat_credentials
    }
    return true
  }

  const getCategoryColor = (category: string): string => {
    const colors: Record<string, string> = {
      'wordpress': 'bg-blue-100 text-blue-800',
      'wordstat': 'bg-green-100 text-green-800'
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold gradient-text mb-4">MCP Инструменты</h2>
        <p className="text-white/70">Управляйте WordPress, Wordstat и Google сервисами</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Tools List */}
        <div className="modern-card p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center">
            🛠️ Доступные инструменты
          </h3>
          
          <div className="space-y-6">
            {/* WordPress Tools */}
            <div>
              <h4 className="text-lg font-semibold text-indigo-300 mb-4 flex items-center">
                📝 WordPress
              </h4>
              <div className="grid grid-cols-1 gap-3">
                {[
                  'create_post', 'update_post', 'get_posts', 'delete_post', 
                  'search_posts', 'create_category', 'get_categories', 'upload_media'
                ].map((tool) => (
                  <button
                    key={tool}
                    onClick={() => {
                      setSelectedTool(tool)
                      setParams(getDefaultParams(tool))
                    }}
                    className={`modern-card p-4 text-left transition-all duration-300 ${
                      selectedTool === tool
                        ? 'neon-glow border-indigo-400'
                        : 'hover:border-white/30'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-white">{tool}</span>
                      <span className="px-2 py-1 rounded-full text-xs bg-indigo-500/20 text-indigo-300">
                        WordPress
                      </span>
                    </div>
                    <p className="text-sm text-white/70">
                      {getToolDescription(tool)}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Wordstat Tools */}
            <div>
              <h4 className="text-lg font-semibold text-green-300 mb-4 flex items-center">
                📊 Wordstat
              </h4>
              <div className="grid grid-cols-1 gap-3">
                {[
                  'set_wordstat_token', 'get_wordstat_regions_tree', 
                  'get_wordstat_top_requests', 'get_wordstat_dynamics'
                ].map((tool) => (
                  <button
                    key={tool}
                    onClick={() => {
                      setSelectedTool(tool)
                      setParams(getDefaultParams(tool))
                    }}
                    className={`modern-card p-4 text-left transition-all duration-300 ${
                      selectedTool === tool
                        ? 'neon-glow border-green-400'
                        : 'hover:border-white/30'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-white">{tool}</span>
                      <span className="px-2 py-1 rounded-full text-xs bg-green-500/20 text-green-300">
                        Wordstat
                      </span>
                    </div>
                    <p className="text-sm text-white/70">
                      {getToolDescription(tool)}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Google Tools */}
            <div>
              <h4 className="text-lg font-semibold text-red-300 mb-4 flex items-center">
                🔍 Google (MCP)
              </h4>
              <div className="grid grid-cols-1 gap-3">
                {[
                  'google_trends', 'google_search_volume', 'google_keywords',
                  'google_analytics', 'google_ads', 'youtube_analytics'
                ].map((tool) => (
                  <button
                    key={tool}
                    onClick={() => {
                      setSelectedTool(tool)
                      setParams(getDefaultParams(tool))
                    }}
                    className={`modern-card p-4 text-left transition-all duration-300 ${
                      selectedTool === tool
                        ? 'neon-glow border-red-400'
                        : 'hover:border-white/30'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-white">{tool}</span>
                      <span className="px-2 py-1 rounded-full text-xs bg-red-500/20 text-red-300">
                        MCP
                      </span>
                    </div>
                    <p className="text-sm text-white/70">
                      {getToolDescription(tool)}
                    </p>
                    <p className="text-xs text-green-400 mt-1">
                      ✅ Не требует настройки - работает через MCP сервер
                    </p>
                  </button>
                ))}
              </div>
            </div>

          </div>
        </div>

        {/* Tool Execution */}
        <div className="modern-card p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center">
            ⚡ Выполнение команды
          </h3>
          
          {selectedTool ? (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-white/80 mb-3">
                  Параметры для <span className="text-indigo-300">{selectedTool}</span>
                </label>
                <div className="space-y-4">
                  {Object.entries(params).map(([key, value]) => (
                    <div key={key}>
                      <label className="block text-sm font-medium text-white/70 mb-2">
                        {key}
                      </label>
                      <input
                        type={key.includes('password') || key.includes('secret') ? 'password' : 'text'}
                        value={value}
                        onChange={(e) => setParams({...params, [key]: e.target.value})}
                        className="modern-input w-full"
                        placeholder={`Введите ${key}`}
                      />
                    </div>
                  ))}
                </div>
              </div>
              
              <button
                onClick={executeTool}
                disabled={isLoading}
                className="btn-primary w-full py-3 text-lg font-semibold disabled:opacity-50"
              >
                {isLoading ? '⏳ Выполнение...' : '🚀 Выполнить'}
              </button>
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎯</div>
              <p className="text-white/60 text-lg">Выберите инструмент для выполнения</p>
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="modern-card p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center">
            📋 Результат выполнения
          </h3>
          <div className={`p-4 rounded-lg ${
            result.success 
              ? 'bg-green-500/10 border border-green-500/20' 
              : 'bg-red-500/10 border border-red-500/20'
          }`}>
            <pre className="text-sm text-white/80 overflow-auto max-h-96 whitespace-pre-wrap">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}