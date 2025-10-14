"use client"

import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface User {
  id: string
  email: string
  full_name: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  hasHydrated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, full_name: string) => Promise<void>
  logout: () => void
  reset: () => void
  setHydrated: () => void
}

const baseState = {
  user: null,
  token: null,
  isAuthenticated: false,
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      ...baseState,
      hasHydrated: false,

      login: async (email: string, password: string) => {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password }),
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          const message = errorData?.detail || 'Ошибка входа'
          throw new Error(message)
        }

        const data = await response.json()
        set({ user: data.user, token: data.access_token, isAuthenticated: true, hasHydrated: true })
      },

      register: async (email: string, password: string, full_name: string) => {
        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password, full_name }),
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          const message = errorData?.detail || 'Ошибка регистрации'
          throw new Error(message)
        }

        const data = await response.json()
        set({ user: data.user, token: data.access_token, isAuthenticated: true, hasHydrated: true })
      },

      logout: () => {
        set({ ...baseState, hasHydrated: true })
      },

      reset: () => {
        set({ ...baseState, hasHydrated: true })
      },

      setHydrated: () => {
        set({ hasHydrated: true })
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state, error) => {
        if (error) {
          console.error('Ошибка восстановления состояния:', error)
        }
        // Устанавливаем hasHydrated в true после восстановления
        if (state) {
          state.hasHydrated = true
        }
      },
    }
  )
)