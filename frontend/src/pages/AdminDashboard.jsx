import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getDashboardStats } from '../services/admin'
import { AdminRoute } from '../components/ProtectedRoute'
import { BarChart3, Users, ShoppingCart, TrendingUp } from 'lucide-react'

export default function AdminDashboard() {
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      setIsLoading(true)
      try {
        const data = await getDashboardStats()
        setStats(data)
      } catch (error) {
        console.error('Failed to load stats:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (isLoading || !stats) {
    return (
      <AdminRoute>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-gray-500">Loading...</div>
        </div>
      </AdminRoute>
    )
  }

  return (
    <AdminRoute>
      <div className="page-shell py-12">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-4xl font-bold mb-12">Admin Dashboard</h1>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="surface-card rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm mb-2">Total Revenue</p>
                  <p className="text-3xl font-bold text-blue-600">
                    ${stats.revenue.total.toFixed(2)}
                  </p>
                </div>
                <TrendingUp size={40} className="text-blue-600 opacity-20" />
              </div>
            </div>

            <div className="surface-card rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm mb-2">Products</p>
                  <p className="text-3xl font-bold">{stats.products.total}</p>
                  <p className="text-gray-600 text-xs mt-1">{stats.products.active} active</p>
                </div>
                <ShoppingCart size={40} className="text-green-600 opacity-20" />
              </div>
            </div>

            <div className="surface-card rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm mb-2">Total Orders</p>
                  <p className="text-3xl font-bold">{stats.orders.total}</p>
                  <p className="text-gray-600 text-xs mt-1">{stats.orders.pending} pending</p>
                </div>
                <BarChart3 size={40} className="text-purple-600 opacity-20" />
              </div>
            </div>

            <div className="surface-card rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm mb-2">Pending Payment</p>
                  <p className="text-3xl font-bold text-yellow-600">
                    {stats.orders.pending_payment}
                  </p>
                  <p className="text-gray-600 text-xs mt-1">Awaiting payment</p>
                </div>
                <Users size={40} className="text-yellow-600 opacity-20" />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="surface-card rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/admin/products')}
                  className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 text-left px-4"
                >
                  → Manage Products
                </button>
                <button
                  onClick={() => navigate('/admin/orders')}
                  className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700 text-left px-4"
                >
                  → View All Orders
                </button>
              </div>
            </div>

            <div className="surface-card rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4">Order Summary</h2>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Confirmed</span>
                  <span className="font-bold">{stats.orders.confirmed}</span>
                </div>
                <div className="flex justify-between">
                  <span>Shipped</span>
                  <span className="font-bold">{stats.orders.shipped}</span>
                </div>
                <div className="flex justify-between">
                  <span>Pending</span>
                  <span className="font-bold">{stats.orders.pending}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AdminRoute>
  )
}
