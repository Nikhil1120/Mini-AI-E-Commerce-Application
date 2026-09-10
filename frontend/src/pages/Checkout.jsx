import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useCartStore } from '../context/cartStore'
import { createOrder } from '../services/orders'
import { createCheckoutSession } from '../services/payments'
import { ProtectedRoute } from '../components/ProtectedRoute'
import { CreditCard, ShoppingCart } from 'lucide-react'

export default function Checkout() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { cart, fetchCart } = useCartStore()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchCart()
  }, [fetchCart])

  useEffect(() => {
    if (searchParams.get('payment') === 'cancelled') {
      setError('Payment was cancelled. Your order is still pending — you can try again.')
    }
  }, [searchParams])

  const handleCheckout = async () => {
    if (!cart || cart.items.length === 0) {
      setError('Cart is empty')
      return
    }

    setIsLoading(true)
    setError('')
    try {
      const order = await createOrder()
      const session = await createCheckoutSession(order.id)

      if (session.checkout_url) {
        window.location.href = session.checkout_url
        return
      }

      setError('Checkout session created but no redirect URL was returned.')
      navigate(`/orders/${order.id}`)
    } catch (err) {
      const message =
        err?.response?.data?.detail || err?.message || 'Checkout failed'
      setError(typeof message === 'string' ? message : 'Checkout failed')
    } finally {
      setIsLoading(false)
    }
  }

  if (!cart || cart.items.length === 0) {
    return (
      <ProtectedRoute>
        <div className="page-shell py-12">
          <div className="max-w-2xl mx-auto px-4 text-center">
            <ShoppingCart size={64} className="mx-auto text-slate-400 mb-4" />
            <h2 className="text-2xl font-bold mb-4">Your Cart is Empty</h2>
            <button
              onClick={() => navigate('/')}
              className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700"
            >
              Continue Shopping
            </button>
          </div>
        </div>
      </ProtectedRoute>
    )
  }

  const totalPrice =
    cart.total_price ??
    cart.items.reduce((sum, item) => sum + (item.product?.price * item.quantity || 0), 0)

  return (
    <ProtectedRoute>
      <div className="page-shell py-12">
        <div className="max-w-4xl mx-auto px-4">
          <h1 className="text-3xl font-bold mb-8">Checkout</h1>

          {error && (
            <div className="mb-6 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 text-sm">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-2 surface-card rounded-lg shadow-sm p-6">
              <h2 className="text-2xl font-bold mb-6">Order Summary</h2>
              <div className="space-y-4 mb-6 border-b pb-6">
                {cart.items.map((item) => (
                  <div key={item.id} className="flex justify-between items-center">
                    <div>
                      <p className="font-semibold">{item.product?.name}</p>
                      <p className="surface-muted text-sm">Quantity: {item.quantity}</p>
                    </div>
                    <p className="font-semibold">
                      ${((item.product?.price || 0) * item.quantity).toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>
              <div className="flex justify-between text-xl font-bold">
                <span>Total</span>
                <span className="text-blue-600">${Number(totalPrice).toFixed(2)}</span>
              </div>
            </div>

            <div className="surface-card rounded-lg shadow-sm p-6 h-fit">
              <h2 className="text-xl font-bold mb-4">Payment</h2>
              <p className="text-sm surface-muted mb-4">
                You will be redirected to Stripe Checkout. With dummy keys, a demo payment page
                simulates success, failure, and cancellation. Payment is confirmed only by the
                backend webhook logic — not by the success page alone.
              </p>
              <p className="text-3xl font-bold text-blue-600 mb-6">
                ${Number(totalPrice).toFixed(2)}
              </p>
              <button
                onClick={handleCheckout}
                disabled={isLoading}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                <CreditCard size={20} />
                <span>{isLoading ? 'Redirecting…' : 'Pay with Stripe'}</span>
              </button>
              <button
                onClick={() => navigate('/cart')}
                className="w-full btn-secondary py-3 rounded-lg mt-4"
              >
                Back to Cart
              </button>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}
