import React from 'react'
import { GoogleLogin } from '@react-oauth/google'
import { useNavigate, Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''
const isDev = import.meta.env.DEV

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, devLogin, isAuthenticated, user, isAuthChecking } = useAuthStore()
  const [isLoading, setIsLoading] = React.useState(false)
  const [error, setError] = React.useState('')
  const [showGoogleButton, setShowGoogleButton] = React.useState(false)

  const redirectTo = location.state?.from?.pathname
    || (user?.role === 'ADMIN' ? '/admin' : '/')

  React.useEffect(() => {
    if (googleClientId) {
      setShowGoogleButton(true)
    }
  }, [])

  if (isAuthChecking) {
    return (
      <div className="page-shell flex items-center justify-center">
        <p className="surface-muted text-sm">Checking session…</p>
      </div>
    )
  }

  if (isAuthenticated && user) {
    return <Navigate to={redirectTo} replace />
  }

  const handleLoginSuccess = async (credentialResponse) => {
    if (!credentialResponse?.credential) {
      setError('Google did not return a credential. Please try again.')
      return
    }

    setIsLoading(true)
    setError('')
    try {
      // Frontend → Google Sign-In → FastAPI /auth/google → JWT session
      const data = await login(credentialResponse.credential)
      const destination = data.user?.role === 'ADMIN' ? '/admin' : (redirectTo === '/admin' ? '/' : redirectTo)
      navigate(destination, { replace: true })
    } catch (err) {
      const message =
        err?.response?.data?.detail || err?.message || 'Login failed'
      setError(typeof message === 'string' ? message : 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDevLogin = async (email) => {
    setIsLoading(true)
    setError('')
    try {
      const data = await devLogin(email)
      navigate(data.user?.role === 'ADMIN' ? '/admin' : '/', { replace: true })
    } catch (err) {
      const message =
        err?.response?.data?.detail || err?.message || 'Dev login failed'
      setError(typeof message === 'string' ? message : 'Dev login failed')
    } finally {
      setIsLoading(false)
    }
  }

  const currentPort = window.location.port || '80'
  const originMismatch = currentPort !== '5173'

  return (
    <div className="page-shell flex items-center justify-center py-12 px-4">
      <div className="surface-card rounded-xl shadow-lg p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold surface-heading tracking-tight">AI Store</h1>
          <p className="surface-muted mt-2">Sign in with Google to shop and get AI support</p>
          <p className="text-slate-400 dark:text-slate-500 text-xs mt-2">
            New customers are registered automatically on first sign-in
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {!googleClientId && (
          <div className="mb-4 rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-xs">
            Missing <code>VITE_GOOGLE_CLIENT_ID</code> in <code>.env.local</code>.
          </div>
        )}

        {googleClientId && originMismatch && (
          <div className="mb-4 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 text-xs">
            Google Sign-In requires port <strong>5173</strong> or the current origin registered in
            Google Cloud Console. You are on port <strong>{currentPort}</strong>.
            Add <code className="bg-amber-100 px-1 rounded">http://localhost:{currentPort}</code>
            under Authorized JavaScript origins.
          </div>
        )}

        <div className="flex flex-col items-center gap-4">
          {isLoading ? (
            <p className="text-slate-500 text-sm">Signing you in…</p>
          ) : (
            showGoogleButton && googleClientId && (
              <GoogleLogin
                onSuccess={handleLoginSuccess}
                onError={() =>
                  setError(
                    'Google Sign-In failed. Verify VITE_GOOGLE_CLIENT_ID and Authorized JavaScript origins in Google Cloud Console.'
                  )
                }
                text="signin_with"
                useOneTap={false}
              />
            )
          )}
        </div>

        {isDev && !isLoading && (
          <details className="mt-6 pt-6 border-t border-slate-200">
            <summary className="text-center text-slate-500 text-xs cursor-pointer">
              Development login (DEV_MODE=true)
            </summary>
            <div className="flex flex-col gap-2 mt-3">
              <button
                type="button"
                onClick={() => handleDevLogin('customer@ecommerce.local')}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-700 px-4 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800"
              >
                Login as Customer
              </button>
              <button
                type="button"
                onClick={() => handleDevLogin('admin@ecommerce.local')}
                className="w-full rounded-lg border border-indigo-300 px-4 py-2 text-sm text-indigo-700 hover:bg-indigo-50"
              >
                Login as Admin
              </button>
            </div>
          </details>
        )}

        <p className="text-center text-slate-500 text-xs mt-8">
          Protected routes: cart, checkout, orders, and AI chat require a customer account.
        </p>
      </div>
    </div>
  )
}
