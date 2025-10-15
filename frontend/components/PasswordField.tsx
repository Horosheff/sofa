'use client'

import { useState } from 'react'

type Props = {
  label: string
  name: string
  value?: string
  onChange?: (value: string) => void
  onBlur?: () => void
  placeholder?: string
  readOnly?: boolean
  className?: string
}

export default function PasswordField({
  label,
  name,
  value = '',
  onChange,
  onBlur,
  placeholder,
  readOnly = false,
  className = '',
}: Props) {
  const [visible, setVisible] = useState(false)

  return (
    <div className={className}>
      <label className="block text-sm font-medium text-foreground/80 mb-2">
        {label}
      </label>
      <div className="relative">
        <input
          name={name}
          type={visible ? 'text' : 'password'}
          className="modern-input w-full pr-12"
          placeholder={placeholder}
          readOnly={readOnly}
          value={value}
          onChange={(event) => onChange?.(event.target.value)}
          onBlur={onBlur}
        />
        <button
          type="button"
          className="absolute inset-y-0 right-2 flex items-center text-foreground/60 hover:text-foreground"
          onClick={() => setVisible((prev) => !prev)}
        >
          {visible ? '🙈' : '👁️'}
        </button>
      </div>
    </div>
  )
}

