import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'WordPress MCP Platform',
  description: 'Управляйте WordPress через MCP сервер',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  )
}
