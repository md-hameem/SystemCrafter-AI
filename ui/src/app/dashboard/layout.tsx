'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store'
import { 
  Sparkles, 
  LayoutDashboard, 
  FolderKanban, 
  Settings, 
  LogOut,
  Menu,
  X
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const pathname = usePathname()
  const { user, isAuthenticated, fetchUser, logout } = useAuthStore()
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  useEffect(() => {
    fetchUser().then(() => {
      if (!useAuthStore.getState().isAuthenticated) {
        router.push('/login')
      }
    })
  }, [fetchUser, router])

  const handleLogout = () => {
    logout()
    router.push('/')
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  const navItems = [
    { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { href: '/dashboard/projects', icon: FolderKanban, label: 'Projects' },
    { href: '/dashboard/settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Mobile header */}
      <header className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-slate-800/90 backdrop-blur-md border-b border-slate-700 z-50 flex items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-primary-500" />
          <span className="font-bold text-white">SystemCrafter</span>
        </div>
        <button
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="p-2 text-slate-400 hover:text-white"
        >
          {isSidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </header>

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed top-0 left-0 h-full w-64 bg-slate-800 border-r border-slate-700 z-40 transform transition-transform duration-300 ease-in-out',
          'lg:translate-x-0',
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="p-6 border-b border-slate-700">
          <Link href="/dashboard" className="flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-primary-500" />
            <span className="text-xl font-bold text-white">SystemCrafter</span>
          </Link>
        </div>

        <nav className="p-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setIsSidebarOpen(false)}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors',
                pathname === item.href
                  ? 'bg-primary-600/20 text-primary-400'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-700">
          <div className="flex items-center gap-3 mb-4 px-4">
            <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-medium">
              {user?.full_name?.[0] || user?.email[0].toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-white truncate">
                {user?.full_name || 'User'}
              </p>
              <p className="text-xs text-slate-500 truncate">
                {user?.email}
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-4 py-3 rounded-lg text-sm font-medium text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
          >
            <LogOut className="h-5 w-5" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <main className="lg:ml-64 pt-16 lg:pt-0 min-h-screen">
        {children}
      </main>
    </div>
  )
}
