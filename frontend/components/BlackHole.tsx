'use client'

import React, { useEffect, useRef, useState } from 'react'

const BlackHole: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null)
  const blackHoleRef = useRef<HTMLDivElement>(null)
  const [currentAnimationDuration, setCurrentAnimationDuration] = useState(8) // seconds

  useEffect(() => {
    const blackHoleElement = blackHoleRef.current
    const containerElement = containerRef.current

    if (!blackHoleElement || !containerElement) return

    const createParticle = (x: number, y: number) => {
      const particle = document.createElement('div')
      particle.className = 'particle'
      const size = Math.random() * 5 + 2
      particle.style.width = `${size}px`
      particle.style.height = `${size}px`
      particle.style.left = `${x}px`
      particle.style.top = `${y}px`

      const angle = Math.random() * Math.PI * 2
      const distance = Math.random() * 200 + 50
      const targetX = x + distance * Math.cos(angle)
      const targetY = y + distance * Math.sin(angle)

      particle.style.setProperty('--x', `${targetX - x}px`)
      particle.style.setProperty('--y', `${targetY - y}px`)
      particle.style.animationDuration = `${Math.random() * 3 + 2}s`
      particle.style.animationDelay = `${Math.random() * 0.5}s`

      containerElement.appendChild(particle)

      particle.addEventListener('animationend', () => {
        particle.remove()
      })
    }

    const handleClick = (e: MouseEvent) => {
      const rect = blackHoleElement.getBoundingClientRect()
      for (let i = 0; i < 30; i++) {
        createParticle(e.clientX - rect.left, e.clientY - rect.top)
      }
      setCurrentAnimationDuration(4) // Faster spin on click
      blackHoleElement.style.animationDuration = `${4}s`
    }

    const handleMouseEnter = () => {
      blackHoleElement.style.animationDuration = '4s' // Faster spin on hover
    }

    const handleMouseLeave = () => {
      blackHoleElement.style.animationDuration = `${currentAnimationDuration}s` // Revert to current speed
    }

    blackHoleElement.addEventListener('click', handleClick)
    blackHoleElement.addEventListener('mouseenter', handleMouseEnter)
    blackHoleElement.addEventListener('mouseleave', handleMouseLeave)

    return () => {
      blackHoleElement.removeEventListener('click', handleClick)
      blackHoleElement.removeEventListener('mouseenter', handleMouseEnter)
      blackHoleElement.removeEventListener('mouseleave', handleMouseLeave)
    }
  }, [currentAnimationDuration])

  return (
    <div ref={containerRef} className="black-hole-container">
      <div ref={blackHoleRef} className="black-hole"></div>
    </div>
  )
}

export default BlackHole