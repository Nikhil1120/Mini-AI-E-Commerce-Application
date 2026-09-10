import React from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Mail, Shield, Calendar, LogOut } from 'lucide-react'
import { useAuthStore } from '../context/authStore'
import { AuthRoute } from '../components/ProtectedRoute'

function ProfileContent() {
  const navigate = useNavigate()
  const { user, logout, isLoading } = useAuthStore()

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true })
  }

  if (!user) return null

  const displayName =
    [user.first_name, user.last_name].filter(Boolean).join(' ') || user.username
  const joinedDate = user.created_at
    ? new Date(user.created_at).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : '—'

  return (
    <div className="page-shell py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="surface-card rounded-2xl overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 px-8 py-10 text-white">
            <div className="flex items-center gap-4">
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-white/20 backdrop-blur">
                <User size={40} />
              </div>
              <div>
                <h1 className="text-3xl font-bold">{displayName}</h1>
                <p className="text-blue-100 mt-1">{user.email}</p>
              </div>
            </div>
          </div>

          <div className="p-8 space-y-6">
            <div>
              <h2 className="text-lg font-semibold mb-4">Account Details</h2>
              <dl className="grid gap-4 sm:grid-cols-2">
                <div className="surface-card rounded-xl p-4">
                  <dt className="flex items-center gap-2 text-sm surface-muted mb-1">
                    <Mail size={16} />
                    Email
                  </dt>
                  <dd className="font-medium break-all">{user.email}</dd>
                </div>
                <div className="surface-card rounded-xl p-4">
                  <dt className="flex items-center gap-2 text-sm surface-muted mb-1">
                    <User size={16} />
                    Username
                  </dt>
                  <dd className="font-medium">{user.username}</dd>
                </div>
                <div className="surface-card rounded-xl p-4">
                  <dt className="flex items-center gap-2 text-sm surface-muted mb-1">
                    <Shield size={16} />
                    Role
                  </dt>
                  <dd>
                    <span className="inline-flex rounded-full bg-blue-100 dark:bg-blue-950 px-3 py-1 text-sm font-medium text-blue-700 dark:text-blue-300">
                      {user.role}
                    </span>
                  </dd>
                </div>
                <div className="surface-card rounded-xl p-4">
                  <dt className="flex items-center gap-2 text-sm surface-muted mb-1">
                    <Calendar size={16} />
                    Member since
                  </dt>
                  <dd className="font-medium">{joinedDate}</dd>
                </div>
              </dl>
            </div>

            <div className="surface-card rounded-xl p-4">
              <p className="text-sm surface-muted mb-1">Account status</p>
              <p className="font-medium">
                {user.is_active ? 'Active' : 'Inactive'}
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <button
                type="button"
                onClick={() => navigate(user.role === 'ADMIN' ? '/admin' : '/')}
                className="btn-secondary flex-1 rounded-lg px-4 py-3 font-medium"
              >
                Back to {user.role === 'ADMIN' ? 'Dashboard' : 'Shopping'}
              </button>
              <button
                type="button"
                onClick={handleLogout}
                disabled={isLoading}
                className="inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-3 font-medium text-white hover:bg-red-700 disabled:opacity-50"
              >
                <LogOut size={18} />
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Profile() {
  return (
    <AuthRoute>
      <ProfileContent />
    </AuthRoute>
  )
}
