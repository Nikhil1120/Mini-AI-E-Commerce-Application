import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getOrder } from '../services/orders'
import { ProtectedRoute } from '../components/ProtectedRoute'
import { ArrowLeft } from 'lucide-react'

export default function OrderDetails() {
  const { orderId } = useParams()
  const navigate = useNavigate()
  const [order, setOrder] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchOrder = async () => {
      setIsLoading(true)
      try {
        const data = await getOrder(orderId)
        setOrder(data)
      } catch (error) {
        alert('Failed to load order: ' + error.message)
        navigate('/orders')
      } finally {
        setIsLoading(false)
      }
    }

    fetchOrder()
  }, [orderId, navigate])

  const getStatusColor = (status) => {
    const colors = {
      'PENDING': 'bg-yellow-100 text-yellow-800',
      'CONFIRMED': 'bg-blue-100 text-blue-800',
      'PROCESSING': 'bg-purple-100 text-purple-800',
      'SHIPPED': 'bg-indigo-100 text-indigo-800',
      'DELIVERED': 'bg-green-100 text-green-800',
      'CANCELLED': 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getPaymentStatusColor = (status) => {
    const colors = {
      'PENDING': 'bg-yellow-100 text-yellow-800',
      'PAID': 'bg-green-100 text-green-800',
      'FAILED': 'bg-red-100 text-red-800',
      'CANCELLED': 'bg-gray-100 text-gray-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-gray-500">Loading order...</div>
        </div>
      </ProtectedRoute>
    )
  }

  if (!order) {
    return (
      <ProtectedRoute>
        <div className="flex items-center justify-center min-h-screen">
          <div>Order not found</div>
        </div>
      </ProtectedRoute>
    )
  }

  const orderDate = new Date(order.created_at).toLocaleDateString()
  const updatedDate = new Date(order.updated_at).toLocaleDateString()

  return (
    <ProtectedRoute>
      <div className="page-shell py-12">
        <div className="max-w-4xl mx-auto px-4">
          {/* Back Button */}
          <button
            onClick={() => navigate('/orders')}
            className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 mb-8"
          >
            <ArrowLeft size={20} />
            <span>Back to Orders</span>
          </button>

          {/* Order Header */}
          <div className="surface-card rounded-lg shadow-md p-8 mb-6">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h1 className="text-3xl font-bold mb-2">Order #{order.id}</h1>
                <p className="text-gray-600">Placed on {orderDate}</p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-blue-600 mb-2">${order.total_amount.toFixed(2)}</p>
              </div>
            </div>

            {/* Status Info */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <p className="text-gray-600 text-sm mb-2">Order Status</p>
                <span className={`inline-block px-3 py-1 rounded text-sm font-medium ${getStatusColor(order.status)}`}>
                  {order.status}
                </span>
              </div>
              <div>
                <p className="text-gray-600 text-sm mb-2">Payment Status</p>
                <span className={`inline-block px-3 py-1 rounded text-sm font-medium ${getPaymentStatusColor(order.payment_status)}`}>
                  {order.payment_status}
                </span>
              </div>
            </div>

            <p className="text-gray-600 text-sm">Last updated: {updatedDate}</p>
          </div>

          {/* Order Items */}
          <div className="surface-card rounded-lg shadow-md overflow-hidden mb-6">
            <div className="bg-gray-50 dark:bg-slate-800 px-8 py-4 border-b border-slate-200 dark:border-slate-700">
              <h2 className="text-xl font-bold">Order Items</h2>
            </div>
            <div className="divide-y">
              {order.items.map((item) => (
                <div key={item.id} className="px-8 py-4 flex justify-between items-center">
                  <div>
                    <p className="font-semibold">{item.product_name}</p>
                    <p className="text-gray-600 text-sm">
                      {item.quantity} x ${item.price.toFixed(2)}
                    </p>
                  </div>
                  <p className="font-semibold">${item.subtotal.toFixed(2)}</p>
                </div>
              ))}
            </div>

            {/* Order Summary */}
            <div className="bg-gray-50 dark:bg-slate-800 px-8 py-4 space-y-2">
              <div className="flex justify-between text-lg font-bold">
                <span>Total</span>
                <span className="text-blue-600">${order.total_amount.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex space-x-4">
            <button
              onClick={() => navigate('/')}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-semibold"
            >
              Continue Shopping
            </button>
            <button
              onClick={() => window.print()}
              className="flex-1 btn-secondary py-3 rounded-lg font-semibold"
            >
              Print Order
            </button>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}
