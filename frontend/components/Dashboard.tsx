'use client'

import { useState, useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import api from '@/lib/api'

export default function Dashboard() {
  const { user, logout } = useAuthStore()
  const [mcpTools, setMcpTools] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchMcpTools = async () => {
      try {
        const response = await api.get('/mcp/tools')
        setMcpTools(response.data.tools || [])
      } catch (error) {
        console.error('Ошибка загрузки MCP инструментов:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchMcpTools()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                Добро пожаловать, {user?.full_name || user?.email}!
              </h1>
              
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-gray-700 mb-4">
                  MCP Инструменты
                </h2>
                
                {isLoading ? (
                  <div className="text-gray-500">Загрузка инструментов...</div>
                ) : mcpTools.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {mcpTools.map((tool, index) => (
                      <div key={index} className="bg-white p-4 rounded-lg shadow">
                        <h3 className="font-medium text-gray-900">{tool.name}</h3>
                        <p className="text-sm text-gray-600">{tool.description}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-gray-500">
                    MCP инструменты недоступны
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                  <h3 className="text-lg font-medium text-blue-900">
                    WordPress MCP Platform
                  </h3>
                  <p className="text-blue-700">
                    Управляйте WordPress сайтами через MCP протокол
                  </p>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-md p-4">
                  <h3 className="text-lg font-medium text-green-900">
                    Доступные функции
                  </h3>
                  <ul className="text-green-700 space-y-1">
                    <li>• Создание и управление постами</li>
                    <li>• Загрузка медиафайлов</li>
                    <li>• Управление пользователями</li>
                    <li>• Настройка плагинов и тем</li>
                  </ul>
                </div>
              </div>

              <div className="mt-8">
                <button
                  onClick={logout}
                  className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                >
                  Выйти
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}