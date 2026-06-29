import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import type { User } from '@/types/auth'
import { authApi } from '@/api/auth.api'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  isAdmin: boolean
  isOwner: boolean
  login: (username: string, password: string) => Promise<void>
  register: (username: string, password: string, confirmPassword: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setUser(null)
        return
      }
      const userData = await authApi.getMe()
      setUser(userData)
    } catch {
      localStorage.removeItem('access_token')
      setUser(null)
    }
  }, [])

  useEffect(() => {
    refreshUser().finally(() => setIsLoading(false))
  }, [refreshUser])

  const login = async (username: string, password: string) => {
    const data = await authApi.login({ username, password })
    localStorage.setItem('access_token', data.access_token)
    await refreshUser()
  }

  const register = async (username: string, password: string, confirmPassword: string) => {
    await authApi.register({ username, password, confirm_password: confirmPassword })
    const data = await authApi.login({ username, password })
    localStorage.setItem('access_token', data.access_token)
    await refreshUser()
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      localStorage.removeItem('access_token')
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        isAdmin: user?.role === 'admin' || user?.role === 'owner',
        isOwner: user?.role === 'owner',
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
