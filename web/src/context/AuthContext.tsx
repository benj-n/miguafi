import React, { createContext, useContext, useEffect, useState } from 'react'
import { API_BASE } from '../env'

interface AuthContextValue {
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  loading: boolean
  setToast: (msg: string) => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)


export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState('')

  useEffect(() => {
    if (token) localStorage.setItem('token', token)
    else localStorage.removeItem('token')
  }, [token])

  async function login(email: string, password: string) {
    const form = new URLSearchParams()
    form.set('username', email)
    form.set('password', password)
    setLoading(true)
    const res = await fetch(`${API_BASE}/auth/login`, { method: 'POST', body: form })
    if (!res.ok) throw new Error('Identifiants invalides')
    const data = await res.json()
    setToken(data.access_token)
    setLoading(false)
  }

  function logout() {
    setToken(null)
  }

  return (
    <AuthContext.Provider value={{ token, login, logout, loading, setToast }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
