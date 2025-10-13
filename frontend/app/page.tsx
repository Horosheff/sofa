'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import LoginForm from '@/components/LoginForm'
import RegisterForm from '@/components/RegisterForm'

interface Particle {
  id: number
  x: number
  y: number
  delay: number
}

export default function Home() {
  const router = useRouter()
  const { isAuthenticated, hasHydrated, setHydrated } = useAuthStore()
  const [showRegister, setShowRegister] = useState(false)
  const [particles, setParticles] = useState<Particle[]>([])

  useEffect(() => {
    setHydrated()
  }, [setHydrated])

  useEffect(() => {
    const newParticles = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 15,
    }))
    setParticles(newParticles)
  }, [])

  useEffect(() => {
    if (hasHydrated && isAuthenticated) {
      router.replace('/dashboard')
    }
  }, [hasHydrated, isAuthenticated, router])

  if (!hasHydrated) {
    return null
  }

  if (isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-950 to-indigo-900 flex items-center justify-center">
        <div className="text-center space-y-3">
          <div className="text-white/70 text-sm tracking-wide uppercase">Авторизация выполнена</div>
          <div className="text-white text-2xl font-semibold animate-pulse">Перенаправляем в панель...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="animated-bg"></div>

      <div className="particles">
        {particles.map((particle) => (
          <div
            key={particle.id}
            className="particle"
            style={{
              left: `${particle.x}%`,
              top: `${particle.y}%`,
              animationDelay: `${particle.delay}s`,
            }}
          />
        ))}
      </div>

      <div className="flex items-center justify-center min-h-screen p-4 relative z-10">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center space-y-4">
            <div className="floating">
              <h1 className="text-6xl font-bold gradient-text">MCP KOV4EG</h1>
              <div className="text-xl font-light text-white/80 mt-2">
                WordPress Management Platform
              </div>
            </div>
            <p className="text-white/70 text-lg">Управляйте WordPress через MCP сервер</p>
          </div>

          <div className="modern-card p-8 space-y-6">
            {showRegister ? (
              <RegisterForm onSwitchToLogin={() => setShowRegister(false)} />
            ) : (
              <LoginForm onSwitchToRegister={() => setShowRegister(true)} />
            )}
          </div>

          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="modern-card p-4">
              <div className="text-2xl mb-2">🚀</div>
              <div className="text-sm text-white/70">Быстрая работа</div>
            </div>
            <div className="modern-card p-4">
              <div className="text-2xl mb-2">🔒</div>
              <div className="text-sm text-white/70">Безопасность</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
