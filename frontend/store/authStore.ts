import { create } from 'zustand'

interface User {
  id: string
  email: string
  full_name: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, full_name: string) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  
  login: async (email: string, password: string) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })
      
      if (!response.ok) {
        throw new Error('Ошибка входа')
      }
      
      const data = await response.json()
      set({ user: data.user, token: data.token, isAuthenticated: true })
    } catch (error) {
      throw error
    }
  },
  
  register: async (email: string, password: string, full_name: string) => {
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, full_name }),
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Ошибка регистрации')
      }
      
      const data = await response.json()
      set({ user: data.user, token: data.token, isAuthenticated: true })
    } catch (error) {
      throw error
    }
  },
  
  logout: () => {
    set({ user: null, token: null, isAuthenticated: false })
  }
}))