'use client'

import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { useAuthStore } from '@/store/authStore'

interface UserSettings {
  has_wordpress_credentials: boolean
  has_wordstat_credentials: boolean
  has_telegram_bot: boolean
}

interface ExecuteResult {
  success?: boolean
  message?: string
  [key: string]: any
}

type ToolsDictionary = Record<string, string[]>

type ToolKind = 'wordpress' | 'wordstat' | 'telegram' | 'google' | 'other'

const WORDPRESS_TOOLS = new Set([
  'create_post',
  'update_post',
  'get_posts',
  'delete_post',
  'search_posts',
  'bulk_update_posts',
  'create_category',
  'get_categories',
  'update_category',
  'delete_category',
  'upload_media',
  'upload_image_from_url',
  'get_media',
  'delete_media',
  'create_comment',
  'get_comments',
  'update_comment',
  'delete_comment',
])

const WORDSTAT_TOOLS = new Set([
  'set_wordstat_token',
  'get_wordstat_regions_tree',
  'get_wordstat_top_requests',
  'get_wordstat_dynamics',
  'get_wordstat_regions',
  'get_wordstat_user_info',
  'auto_setup_wordstat',
])

const TELEGRAM_TOOLS = new Set([
  'send_message',
  'send_photo',
  'send_document',
  'send_media_group',
  'send_audio',
  'send_video',
  'send_animation',
  'set_webhook',
  'delete_webhook',
  'get_webhook_info',
  'get_bot_info',
  'get_updates',
  'set_commands',
  'delete_message',
  'edit_message',
  'send_poll',
  'stop_poll',
  'answer_callback_query',
  'send_chat_action',
  'get_user_profile_photos',
  'get_file',
])

const GOOGLE_TOOLS = new Set([
  'google_trends',
  'google_search_volume',
  'google_keywords',
  'google_analytics',
  'google_ads',
  'youtube_analytics',
  'google_maps',
])

const DESCRIPTION_MAP: Record<string, string> = {
  create_post: 'Создать новый пост в WordPress',
  update_post: 'Обновить существующий пост',
  get_posts: 'Получить список постов',
  delete_post: 'Удалить пост',
  search_posts: 'Поиск постов',
  bulk_update_posts: 'Массовое обновление постов',
  create_category: 'Создать категорию',
  get_categories: 'Получить список категорий',
  update_category: 'Обновить категорию',
  delete_category: 'Удалить категорию',
  upload_media: 'Загрузить медиафайл',
  upload_image_from_url: 'Загрузить изображение по URL',
  get_media: 'Получить список медиафайлов',
  delete_media: 'Удалить медиафайл',
  create_comment: 'Создать комментарий',
  get_comments: 'Получить комментарии',
  update_comment: 'Обновить комментарий',
  delete_comment: 'Удалить комментарий',
  set_wordstat_token: 'Установить токен Wordstat',
  get_wordstat_regions_tree: 'Получить дерево регионов Wordstat',
  get_wordstat_top_requests: 'Получить топ запросов Wordstat',
  get_wordstat_dynamics: 'Получить динамику запросов Wordstat',
  get_wordstat_regions: 'Получить статистику по регионам Wordstat',
  get_wordstat_user_info: 'Получить информацию об аккаунте Wordstat',
  auto_setup_wordstat: 'Автоматическая настройка подключения Wordstat',
  send_message: 'Отправить текстовое сообщение в Telegram',
  send_photo: 'Отправить фото в Telegram',
  send_document: 'Отправить документ в Telegram',
  send_media_group: 'Отправить альбом медиа в Telegram',
  send_audio: 'Отправить аудио в Telegram',
  send_video: 'Отправить видео в Telegram',
  send_animation: 'Отправить GIF/анимацию в Telegram',
  set_webhook: 'Установить webhook для Telegram бота',
  delete_webhook: 'Удалить webhook Telegram бота',
  get_webhook_info: 'Показать статус webhook Telegram бота',
  get_bot_info: 'Получить информацию о Telegram боте',
  get_updates: 'Получить обновления (long polling)',
  set_commands: 'Настроить команды Telegram бота',
  delete_message: 'Удалить сообщение в Telegram',
  edit_message: 'Редактировать сообщение в Telegram',
  send_poll: 'Создать опрос в Telegram',
  stop_poll: 'Завершить опрос в Telegram',
  answer_callback_query: 'Ответить на inline-кнопку',
  send_chat_action: 'Отправить статус "печатает" и т.п.',
  get_user_profile_photos: 'Получить аватары пользователя',
  get_file: 'Получить файл по file_id',
  google_trends: 'Получить тренды Google (через MCP)',
  google_search_volume: 'Объем поисковых запросов Google (через MCP)',
  google_keywords: 'Анализ ключевых слов Google (через MCP)',
  google_analytics: 'Запрос данных Google Analytics (через MCP)',
  google_ads: 'Управление кампаниями Google Ads (через MCP)',
  youtube_analytics: 'Получить аналитику YouTube (через MCP)',
  google_maps: 'Работа с данными Google Maps (через MCP)',
}

const DEFAULT_PARAMS: Record<string, Record<string, any>> = {
  create_post: { title: '', content: '', status: 'draft' },
  update_post: { post_id: '', title: '', content: '' },
  get_posts: { per_page: 10, page: 1 },
  delete_post: { post_id: '' },
  search_posts: { search: '', per_page: 10 },
  bulk_update_posts: { post_ids: [], updates: {} },
  create_category: { name: '', description: '' },
  get_categories: { per_page: 10 },
  update_category: { category_id: '', name: '', description: '' },
  delete_category: { category_id: '' },
  upload_media: { file_path: '', alt_text: '' },
  upload_image_from_url: { image_url: '', alt_text: '' },
  get_media: { per_page: 10 },
  delete_media: { media_id: '' },
  create_comment: { post_id: '', content: '', author: '' },
  get_comments: { post_id: '', per_page: 10 },
  update_comment: { comment_id: '', content: '' },
  delete_comment: { comment_id: '' },
  set_wordstat_token: { token: '' },
  get_wordstat_top_requests: { phrase: '', regions: [] },
  get_wordstat_dynamics: { phrase: '', regions: [] },
  send_message: { chat_id: '', text: '', parse_mode: 'HTML' },
  send_photo: { chat_id: '', photo: '', caption: '', parse_mode: 'HTML' },
  send_document: { chat_id: '', document: '', caption: '', parse_mode: 'HTML' },
  send_media_group: { chat_id: '', media: [] },
  send_audio: { chat_id: '', audio: '', caption: '', parse_mode: 'HTML' },
  send_video: { chat_id: '', video: '', caption: '', parse_mode: 'HTML' },
  send_animation: { chat_id: '', animation: '', caption: '', parse_mode: 'HTML' },
  set_webhook: { url: '', secret_token: '' },
  delete_webhook: { drop_pending_updates: false },
  get_updates: { offset: null, limit: 100 },
  set_commands: { commands: [{ command: 'start', description: 'Начать работу' }] },
  delete_message: { chat_id: '', message_id: '' },
  edit_message: { chat_id: '', message_id: '', text: '', parse_mode: 'HTML' },
  send_poll: { chat_id: '', question: '', options: [] },
  stop_poll: { chat_id: '', message_id: '' },
  answer_callback_query: { callback_query_id: '', text: '', show_alert: false },
  send_chat_action: { chat_id: '', action: 'typing' },
  get_user_profile_photos: { user_id: '', limit: 5 },
  get_file: { file_id: '' },
}

function detectToolKind(tool: string): ToolKind {
  if (WORDPRESS_TOOLS.has(tool)) return 'wordpress'
  if (WORDSTAT_TOOLS.has(tool)) return 'wordstat'
  if (TELEGRAM_TOOLS.has(tool)) return 'telegram'
  if (GOOGLE_TOOLS.has(tool)) return 'google'
  return 'other'
}

function formatLabel(tool: string): string {
  switch (detectToolKind(tool)) {
    case 'wordpress':
      return 'WordPress'
    case 'wordstat':
      return 'Wordstat'
    case 'telegram':
      return 'Telegram'
    case 'google':
      return 'MCP'
    default:
      return 'Инструмент'
  }
}

export default function ToolsPanel() {
  const { token } = useAuthStore()
  const [tools, setTools] = useState<ToolsDictionary>({})
  const [selectedTool, setSelectedTool] = useState<string>('')
  const [params, setParams] = useState<Record<string, any>>({})
  const [result, setResult] = useState<ExecuteResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [settings, setSettings] = useState<UserSettings>({
    has_wordpress_credentials: false,
    has_wordstat_credentials: false,
    has_telegram_bot: false,
  })

  useEffect(() => {
    fetchTools()
  }, [])

  useEffect(() => {
    if (token) {
      fetchSettings()
    }
  }, [token])

  const availableTools = useMemo(() => {
    const list: string[] = []
    Object.values(tools).forEach((group) => {
      list.push(...group)
    })
    return list
  }, [tools])

  useEffect(() => {
    if (!selectedTool && availableTools.length > 0) {
      const firstAllowed = availableTools.find(canUseTool)
      if (firstAllowed) {
        setSelectedTool(firstAllowed)
        setParams(DEFAULT_PARAMS[firstAllowed] || {})
      }
    }
  }, [availableTools, selectedTool])

  async function fetchTools() {
    try {
      const response = await axios.get<ToolsDictionary>('/api/mcp/tools')
      setTools(response.data)
    } catch (error) {
      console.error('Ошибка загрузки списка инструментов', error)
      // Устанавливаем тестовые инструменты
      setTools({
        'WordPress': ['create_post', 'update_post', 'get_posts', 'delete_post'],
        'Wordstat': ['set_wordstat_token', 'get_wordstat_regions_tree', 'get_wordstat_top_requests'],
        'Google': ['google_trends', 'google_search_volume', 'google_keywords']
      })
    }
  }

  async function fetchSettings() {
    try {
      const response = await axios.get<UserSettings>('/api/user/settings', {
        headers: { Authorization: `Bearer ${token}` },
      })
      setSettings(response.data)
    } catch (error) {
      console.error('Ошибка загрузки пользовательских настроек', error)
    }
  }

  function canUseTool(tool: string): boolean {
    const kind = detectToolKind(tool)
    if (kind === 'wordpress') return settings.has_wordpress_credentials
    if (kind === 'wordstat') return settings.has_wordstat_credentials
    if (kind === 'telegram') return settings.has_telegram_bot
    return true
  }

  function getDescription(tool: string): string {
    return DESCRIPTION_MAP[tool] ?? 'Описание недоступно'
  }

  async function executeSelectedTool() {
    if (!selectedTool || !token) {
      setResult({ success: false, message: 'Сначала выберите инструмент.' })
      return
    }

    if (!canUseTool(selectedTool)) {
      setResult({
        success: false,
        message: 'Для этого инструмента необходимо заполнить настройки профиля.',
      })
      return
    }

    setIsLoading(true)
    setResult(null)

    try {
      const response = await axios.post<ExecuteResult>(
        '/api/mcp/execute',
        { tool: selectedTool, params },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      setResult(response.data)
    } catch (error: any) {
      const message =
        error?.response?.data?.detail || error?.message || 'Ошибка выполнения команды'
      setResult({ success: false, message })
    } finally {
      setIsLoading(false)
    }
  }

  function handleToolSelect(tool: string) {
    setSelectedTool(tool)
    setParams(DEFAULT_PARAMS[tool] ? { ...DEFAULT_PARAMS[tool] } : {})
    setResult(null)
  }

  function renderToolButton(tool: string) {
    const locked = !canUseTool(tool)
    const isActive = tool === selectedTool
    const label = formatLabel(tool)
    const description = getDescription(tool)
    const toolKind = detectToolKind(tool)

    return (
      <button
        key={tool}
        onClick={() => handleToolSelect(tool)}
        disabled={locked}
        className={`glass-tool text-left transition-all duration-300 p-4 ${
          isActive ? 'border-indigo-400 shadow-lg' : ''
        } ${locked ? 'opacity-60 cursor-not-allowed' : ''}`}
      >
        <div className="flex items-start justify-between mb-2">
          <span className="font-semibold text-foreground text-sm leading-tight">{tool}</span>
          <div className="flex items-center gap-2 ml-2">
            <span className="glass-status text-xs">
              {label}
            </span>
            {!locked && (
              <div className="w-2 h-2 bg-green-500 rounded-full flex-shrink-0"></div>
            )}
          </div>
        </div>
        <p className="text-xs text-foreground/70 leading-relaxed mb-2">{description}</p>
        {locked ? (
          <p className="text-xs text-yellow-600">
            ⚠️ Требуется настройка
          </p>
        ) : (
          <p className="text-xs text-green-600">
            ✅ Готов к работе
          </p>
        )}
      </button>
    )
  }

  const toolGroups = useMemo(() => {
    const groups: Record<ToolKind, string[]> = {
      wordpress: [],
      wordstat: [],
      telegram: [],
      google: [],
      other: [],
    }

    availableTools.forEach((tool) => {
      const kind = detectToolKind(tool)
      groups[kind].push(tool)
    })

    return groups
  }, [availableTools])

  return (
    <div className="space-y-10">
      <div className="text-center">
        <h2 className="text-3xl font-bold gradient-text mb-4">Инструменты MCP</h2>
        <p className="text-foreground/70">
          Управляйте WordPress, Wordstat и сервисами Google через одну панель
        </p>
      </div>

      {/* Service Status */}
      <div className="glass-panel mb-8">
        <h3 className="text-xl font-bold text-foreground flex items-center gap-2 mb-6">
          🔗 Статус подключений
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="glass-form flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${settings.has_wordpress_credentials ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <div>
              <h4 className="font-semibold text-foreground">WordPress</h4>
              <p className="text-sm text-foreground/70">
                {settings.has_wordpress_credentials ? 'Подключен' : 'Не настроен'}
              </p>
            </div>
          </div>
          <div className="glass-form flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${settings.has_wordstat_credentials ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <div>
              <h4 className="font-semibold text-foreground">Wordstat</h4>
              <p className="text-sm text-foreground/70">
                {settings.has_wordstat_credentials ? 'Подключен' : 'Не настроен'}
              </p>
            </div>
          </div>
          <div className="glass-form flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${settings.has_telegram_bot ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <div>
              <h4 className="font-semibold text-foreground">Telegram</h4>
              <p className="text-sm text-foreground/70">
                {settings.has_telegram_bot ? 'Подключен' : 'Не настроен'}
              </p>
            </div>
          </div>
          <div className="glass-form flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <div>
              <h4 className="font-semibold text-foreground">MCP Server</h4>
              <p className="text-sm text-foreground/70">Активен</p>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-8">
        <section className="glass-panel space-y-6">
          <h3 className="text-xl font-bold text-foreground flex items-center gap-2">
            🛠️ Доступные команды
          </h3>

          {toolGroups.wordpress.length > 0 && (
            <div>
              <div className="flex items-center gap-3 mb-3">
                <h4 className="text-lg font-semibold text-indigo-600">📝 WordPress</h4>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${settings.has_wordpress_credentials ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="text-xs text-foreground/70">
                    {settings.has_wordpress_credentials ? 'Подключен' : 'Не настроен'}
                  </span>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {toolGroups.wordpress.map(renderToolButton)}
              </div>
            </div>
          )}

          {toolGroups.wordstat.length > 0 && (
            <div>
              <div className="flex items-center gap-3 mb-3">
                <h4 className="text-lg font-semibold text-green-600">📊 Wordstat</h4>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${settings.has_wordstat_credentials ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="text-xs text-foreground/70">
                    {settings.has_wordstat_credentials ? 'Подключен' : 'Не настроен'}
                  </span>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {toolGroups.wordstat.map(renderToolButton)}
              </div>
            </div>
          )}

          {toolGroups.telegram.length > 0 && (
            <div>
              <div className="flex items-center gap-3 mb-3">
                <h4 className="text-lg font-semibold text-blue-600">🤖 Telegram</h4>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${settings.has_telegram_bot ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="text-xs text-foreground/70">
                    {settings.has_telegram_bot ? 'Подключен' : 'Не настроен'}
                  </span>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {toolGroups.telegram.map(renderToolButton)}
              </div>
            </div>
          )}

          {toolGroups.google.length > 0 && (
            <div>
              <div className="flex items-center gap-3 mb-3">
                <h4 className="text-lg font-semibold text-red-600">🔍 Google (MCP)</h4>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                  <span className="text-xs text-foreground/70">Доступен</span>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {toolGroups.google.map(renderToolButton)}
              </div>
            </div>
          )}

          {toolGroups.other.length > 0 && (
            <div>
              <div className="flex items-center gap-3 mb-3">
                <h4 className="text-lg font-semibold text-foreground/70">Дополнительные</h4>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                  <span className="text-xs text-foreground/70">Доступны</span>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {toolGroups.other.map(renderToolButton)}
              </div>
            </div>
          )}
        </section>

        {/* Command Execution Section */}
        {selectedTool && (
          <section className="glass-panel space-y-6">
            <h3 className="text-xl font-bold text-foreground flex items-center gap-2">
              ⚡ Выполнение команды: {selectedTool}
            </h3>

            <div className="space-y-6">
              <div className="space-y-4">
                {Object.entries(params).length === 0 && (
                  <p className="text-sm text-foreground/60">
                    Для этого инструмента параметры не требуются. Можно запускать сразу.
                  </p>
                )}

                {Object.entries(params).map(([key, value]) => (
                  <div key={key}>
                    <label className="block text-sm font-medium text-foreground/70 mb-2">
                      {key}
                    </label>
                    <input
                      type={key.includes('password') || key.includes('secret') ? 'password' : 'text'}
                      value={value}
                      onChange={(event) =>
                        setParams((prev) => ({ ...prev, [key]: event.target.value }))
                      }
                      className="modern-input w-full"
                      placeholder={`Введите ${key}`}
                    />
                  </div>
                ))}
              </div>

              <button
                onClick={executeSelectedTool}
                disabled={isLoading || !canUseTool(selectedTool)}
                className="btn-primary w-full py-3 text-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? '⏳ Выполнение...' : '🚀 Выполнить'}
              </button>
            </div>
          </section>
        )}
      </div>

      {result && (
        <section className="glass-panel">
          <h3 className="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
            📋 Результат выполнения
          </h3>
          <div
            className={`glass-form ${
              result.success ? 'border-green-500/30' : 'border-red-500/30'
            }`}
          >
            <pre className="text-sm text-foreground/80 overflow-auto max-h-96 whitespace-pre-wrap">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </section>
      )}
    </div>
  )
}