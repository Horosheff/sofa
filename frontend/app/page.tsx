'use client'

import { useState, useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import LoginForm from '@/components/LoginForm'
import RegisterForm from '@/components/RegisterForm'
import Dashboard from '@/components/Dashboard'

export default function Home() {
  const { isAuthenticated } = useAuthStore()
  const [showRegister, setShowRegister] = useState(false)
  const [particles, setParticles] = useState<Array<{id: number, x: number, y: number, delay: number}>>([])

  useEffect(() => {
    // Create floating particles
    const newParticles = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 15
    }))
    setParticles(newParticles)
  }, [])

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen relative overflow-hidden">
        {/* Animated Background */}
        <div className="animated-bg"></div>
        
        {/* Floating Particles */}
        <div className="particles">
          {particles.map((particle) => (
            <div
              key={particle.id}
              className="particle"
              style={{
                left: `${particle.x}%`,
                top: `${particle.y}%`,
                animationDelay: `${particle.delay}s`
              }}
            />
          ))}
        </div>
        
        <div className="flex items-center justify-center min-h-screen p-4 relative z-10">
          <div className="max-w-md w-full space-y-8">
            {/* Header */}
            <div className="text-center space-y-4">
              <div className="floating">
                <h1 className="text-6xl font-bold gradient-text">
                  MCP KOV4EG
                </h1>
                <div className="text-xl font-light text-white/80 mt-2">
                  WordPress Management Platform
                </div>
              </div>
              <p className="text-white/70 text-lg">
                Управляйте WordPress через MCP сервер
              </p>
            </div>
            
            {/* Auth Form */}
            <div className="modern-card p-8 space-y-6">
              {showRegister ? (
                <RegisterForm onSwitchToLogin={() => setShowRegister(false)} />
              ) : (
                <LoginForm onSwitchToRegister={() => setShowRegister(true)} />
              )}
            </div>
            
            {/* Features */}
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

  return <Dashboard />
}
