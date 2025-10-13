'use client'

import { useAuthStore } from '@/store/authStore'

export default function Dashboard() {
  const { user, logout } = useAuthStore()

  return (
    <div className="max-w-4xl mx-auto mt-8 p-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Добро пожаловать, {user?.full_name}!
          </h1>
          <button
            onClick={logout}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            Выйти
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Информация о пользователе
            </h3>
            <p className="text-gray-600">
              <strong>Email:</strong> {user?.email}
            </p>
            <p className="text-gray-600">
              <strong>Имя:</strong> {user?.full_name}
            </p>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Статус
            </h3>
            <p className="text-green-600 font-medium">
              ✅ Аккаунт активен
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}