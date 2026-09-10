import { create } from 'zustand'
import * as authService from '../services/auth'

export const useAuthStore = create((set, get) => ({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  isAuthChecking: true,

  setUser: (user) => set({ user }),
  setIsAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
  setIsLoading: (isLoading) => set({ isLoading }),

  login: async (credential) => {
    set({ isLoading: true })
    try {
      const data = await authService.googleLogin(credential)
      set({
        user: data.user,
        isAuthenticated: true,
        isLoading: false,
        isAuthChecking: false,
      })
      return data
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },

  devLogin: async (email) => {
    set({ isLoading: true })
    try {
      const data = await authService.devLogin(email)
      set({
        user: data.user,
        isAuthenticated: true,
        isLoading: false,
        isAuthChecking: false,
      })
      return data
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },

  logout: async () => {
    set({ isLoading: true })
    try {
      await authService.logout()
    } finally {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        isAuthChecking: false,
      })
    }
  },

  clearSession: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    set({
      user: null,
      isAuthenticated: false,
      isAuthChecking: false,
    })
  },

  checkAuth: async () => {
    set({ isAuthChecking: true })
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ user: null, isAuthenticated: false, isAuthChecking: false })
      return
    }

    const user = await authService.getCurrentUser()
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
      set({ user, isAuthenticated: true, isAuthChecking: false })
    } else {
      get().clearSession()
    }
  },
}))
