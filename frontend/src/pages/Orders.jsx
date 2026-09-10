import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { getOrders } from '../services/orders'
import { verifyPaymentSession } from '../services/payments'
import { useCartStore } from '../context/cartStore'
import OrderCard from '../components/OrderCard'
import { ProtectedRoute } from '../components/ProtectedRoute'
import { ShoppingBag, CheckCircle, Loader2 } from 'lucide-react'

export default function Orders() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const { fetchCart } = useCartStore()
  const [orders, setOrders] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [paymentNotice, setPaymentNotice] = useState('')
  const [isVerifying, setIsVerifying] = useState(false)

  const loadOrders = async () => {
    setIsLoading(true)
    try {
      const data = await getOrders(currentPage, 10)
      setOrders(data)
    } catch (error) {
      alert('Failed to load orders: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleOrderUpdate = (updatedOrder) => {
    setOrders((prev) => prev.map((o) => (o.id === updatedOrder.id ? updatedOrder : o)))
  }

  const handleOrderRemove = (orderId) => {
    setOrders((prev) => prev.filter((o) => o.id !== orderId))
  }

  useEffect(() => {
    loadOrders()
  }, [currentPage])

  useEffect(() => {
    const payment = searchParams.get('payment')
    const sessionId = searchParams.get('session_id')

    if (payment !== 'success' || !sessionId) {
      return
    }

    let attempts = 0
    const maxAttempts = 8
    setIsVerifying(true)
    setPaymentNotice('Confirming your payment…')

    const pollVerification = async () => {
      try {
        const result = await verifyPaymentSession(sessionId)
        if (result.verified) {
          setPaymentNotice('Payment confirmed! Your order has been placed.')
          await fetchCart()
          await loadOrders()
          setIsVerifying(false)
          setSearchParams({}, { replace: true })
          return
        }
      } catch (error) {
        setPaymentNotice('Unable to verify payment yet. Please refresh in a moment.')
        setIsVerifying(false)
        return
      }

      attempts += 1
      if (attempts >= maxAttempts) {
        setPaymentNotice(
          'Payment submitted. If status still shows pending, wait a moment and refresh.'
        )
        setIsVerifying(false)
        setSearchParams({}, { replace: true })
        return
      }

      window.setTimeout(pollVerification, 1500)
    }

    pollVerification()
  }, [searchParams, setSearchParams, fetchCart])

  return (
    <ProtectedRoute>
      <div className="page-shell py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold surface-heading">My Orders</h1>
            <button
              onClick={() => navigate('/')}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Continue Shopping
            </button>
          </div>

          {paymentNotice && (
            <div
              className={`mb-6 rounded-lg border px-4 py-3 text-sm flex items-center gap-2 ${
                isVerifying
                  ? 'bg-blue-50 border-blue-200 text-blue-800'
                  : 'bg-green-50 border-green-200 text-green-800'
              }`}
            >
              {isVerifying ? <Loader2 size={18} className="animate-spin" /> : <CheckCircle size={18} />}
              <span>{paymentNotice}</span>
            </div>
          )}

          {isLoading ? (
            <div className="text-center surface-muted">Loading orders...</div>
          ) : orders.length === 0 ? (
            <div className="text-center py-12">
              <ShoppingBag size={64} className="mx-auto text-gray-400 mb-4" />
              <p className="surface-muted text-lg">No orders yet</p>
            </div>
          ) : (
            <div className="space-y-6">
              {orders.map((order) => (
                <OrderCard
                  key={order.id}
                  order={order}
                  onUpdate={handleOrderUpdate}
                  onRemove={handleOrderRemove}
                />
              ))}

              <div className="flex justify-center space-x-2 mt-8">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="btn-secondary px-4 py-2 rounded disabled:opacity-50"
                >
                  Previous
                </button>
                <span className="px-4 py-2">Page {currentPage}</span>
                <button
                  onClick={() => setCurrentPage(currentPage + 1)}
                  className="btn-secondary px-4 py-2 rounded"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  )
}
