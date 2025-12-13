import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import Cookies from 'js-cookie'
import { apiClient, User } from './api'

// =============================================================================
// Auth Store
// =============================================================================

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await apiClient.login(email, password)
          Cookies.set('access_token', response.access_token, {
            expires: 7, // 7 days
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'strict',
          })

          const user = await apiClient.getCurrentUser()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (email: string, password: string, fullName?: string) => {
        set({ isLoading: true })
        try {
          await apiClient.register(email, password, fullName)
          // Login after successful registration
          const response = await apiClient.login(email, password)
          Cookies.set('access_token', response.access_token, {
            expires: 7,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'strict',
          })

          const user = await apiClient.getCurrentUser()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        Cookies.remove('access_token')
        set({ user: null, isAuthenticated: false })
      },

      fetchUser: async () => {
        const token = Cookies.get('access_token')
        if (!token) {
          set({ user: null, isAuthenticated: false })
          return
        }

        set({ isLoading: true })
        try {
          const user = await apiClient.getCurrentUser()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error) {
          Cookies.remove('access_token')
          set({ user: null, isAuthenticated: false, isLoading: false })
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

// =============================================================================
// UI Store (for global UI state)
// =============================================================================

interface UIState {
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  toggleSidebar: () => void
  setTheme: (theme: 'light' | 'dark') => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      theme: 'dark',

      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'ui-storage',
    }
  )
)
