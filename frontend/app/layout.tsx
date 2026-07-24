import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'JARVIS OS - Personal AI Operating System',
  description: 'Production-grade JARVIS-grade personal AI assistant for conversation, planning, automation, and plugins.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased overflow-hidden h-screen bg-cyber-darker text-slate-200">
        {children}
      </body>
    </html>
  )
}
