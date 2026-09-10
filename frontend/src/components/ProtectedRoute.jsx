import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'

function AuthLoading() {
  return (
    <div className="min-h-[50vh] flex items-center justify-center">
      <p className="surface-muted text-sm">Checking session…</p>
    </div>
  )
}

export function CustomerRoute({ children }) {
  const location = useLocation()
  const { isAuthenticated, user, isAuthChecking } = useAuthStore()

  if (isAuthChecking) {
    return <AuthLoading />
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (user.role !== 'CUSTOMER') {
    return <Navigate to={user.role === 'ADMIN' ? '/admin' : '/'} replace />
  }

  return children
}

export function ProtectedRoute({ children }) {
  return <CustomerRoute>{children}</CustomerRoute>
}

export function AdminRoute({ children }) {
  const location = useLocation()
  const { isAuthenticated, user, isAuthChecking } = useAuthStore()

  if (isAuthChecking) {
    return <AuthLoading />
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (user.role !== 'ADMIN') {
    return <Navigate to="/" replace />
  }

  return children
}

export function AuthRoute({ children }) {
  const location = useLocation()
  const { isAuthenticated, user, isAuthChecking } = useAuthStore()

  if (isAuthChecking) {
    return <AuthLoading />
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}
