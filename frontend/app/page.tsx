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
    <div className="min-h-screen lava-bg relative overflow-hidden">
      {/* Лавовые капли */}
      <div className="lava-blob lava-blob-1"></div>
      <div className="lava-blob lava-blob-2"></div>
      <div className="lava-blob lava-blob-3"></div>
      <div className="lava-blob lava-blob-4"></div>
      <div className="lava-blob lava-blob-5"></div>
      
      {/* Эффект матрицы */}
      <div className="matrix-bg">
        {Array.from({ length: 20 }, (_, i) => (
          <div
            key={i}
            className="matrix-column"
            style={{
              left: `${i * 5}%`,
              animationDelay: `${i * 0.5}s`,
            }}
          >
            {Array.from({ length: 50 }, (_, j) => (
              <span
                key={j}
                className="matrix-char"
                style={{
                  '--delay': j,
                } as React.CSSProperties}
              >
                {String.fromCharCode(0x30A0 + Math.random() * 96)}
              </span>
            ))}
          </div>
        ))}
      </div>

      <div className="min-h-screen relative z-10">
        {/* Основной контент */}
        <div className="container mx-auto px-6 py-12">
          <div className="grid lg:grid-cols-2 gap-12 items-center min-h-screen">
            
            {/* Левая часть - заголовок и описание */}
            <div className="space-y-8">
              {/* Заголовок */}
              <div className="space-y-2">
                <h1 className="text-8xl md:text-9xl lg:text-[10rem] font-black text-white leading-none tracking-tight">
                  ВСЁ
                </h1>
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-white leading-none tracking-tight ml-2 md:ml-4 transform -rotate-2">
                  ПОДКЛЮЧЕНО
                </h1>
              </div>
              
              {/* Подзаголовок */}
              <div className="space-y-2">
                <p className="text-2xl lg:text-3xl font-light main-subtitle tracking-wider">
                  by Kov4eg
                </p>
                <p className="text-lg lg:text-xl text-white/70">
                  Universal Connection Platform
                </p>
              </div>
              
              {/* Описание */}
              <div className="space-y-4">
                <p className="text-lg text-white/80 leading-relaxed max-w-lg">
                  Подключайте свои аккаунты к ChatGPT через MCP и управляйте Wordstat, WordPress, Telegram, Threads и другими сервисами из одного окна.
                </p>
                <p className="text-sm text-white/60">
                  Быстрый старт • Безопасная авторизация • Универсальная платформа
                </p>
              </div>
              
              {/* Социальные логотипы */}
              <div className="flex justify-start gap-4">
                <a 
                  href="https://t.me/maya_pro" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center hover:scale-110 transition-all duration-300 shadow-xl hover:shadow-blue-500/30"
                >
                  <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
                  </svg>
                </a>
                
                <a 
                  href="https://vk.com/kov4eg_ai" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl flex items-center justify-center hover:scale-110 transition-all duration-300 shadow-xl hover:shadow-blue-600/30"
                >
                  <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M15.684 0H8.316C1.592 0 0 1.592 0 8.316v7.368C0 22.408 1.592 24 8.316 24h7.368C22.408 24 24 22.408 24 15.684V8.316C24 1.592 22.408 0 15.684 0zm3.692 17.123h-1.744c-.66 0-.864-.525-2.05-1.727-1.033-1.01-1.49-1.135-1.744-1.135-.356 0-.458.102-.458.593v1.575c0 .424-.135.678-1.253.678-1.846 0-3.896-1.118-5.335-3.202C4.624 10.857 4.03 8.57 4.03 8.096c0-.254.102-.491.593-.491h1.744c.441 0 .61.203.78.677.864 2.49 2.303 4.675 2.896 4.675.22 0 .322-.102.322-.66V9.721c-.068-1.186-.695-1.287-.695-1.71 0-.203.17-.407.441-.407h2.744c.373 0 .508.203.508.643v3.473c0 .372.17.508.271.678.102.17.102.271.305.271.22 0 .407-.068.678-.305.254-.22 1.744-1.695 2.728-3.202.22-.322.44-.441.763-.441h1.744c.525 0 .644.271.525.643-.22 1.017-1.253 2.728-2.744 3.202-.22.102-.373.305-.17.644.203.373.864 1.253 1.322 2.051.407.78.78 1.017 1.253 1.017z"/>
                  </svg>
                </a>
              </div>
            </div>
            
            {/* Правая часть - форма в стекломорфизме */}
            <div className="flex justify-center lg:justify-end">
              <div className="w-full max-w-md">
                <div className="glass-panel p-8 space-y-6">
                  {showRegister ? (
                    <RegisterForm onSwitchToLogin={() => setShowRegister(false)} />
                  ) : (
                    <LoginForm onSwitchToRegister={() => setShowRegister(true)} />
                  )}
                </div>
                
                {/* Дополнительные карточки */}
                <div className="grid grid-cols-2 gap-4 mt-6">
                  <div className="glass-panel p-4 text-center">
                    <div className="text-2xl mb-2">🚀</div>
                    <div className="text-sm text-white/70">Быстрая работа</div>
                  </div>
                  <div className="glass-panel p-4 text-center">
                    <div className="text-2xl mb-2">🔒</div>
                    <div className="text-sm text-white/70">Безопасность</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
