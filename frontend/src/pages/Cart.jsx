import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import CartItem from '../components/CartItem'
import { useCartStore } from '../context/cartStore'
import { ProtectedRoute } from '../components/ProtectedRoute'
import { ShoppingBag } from 'lucide-react'

export default function Cart() {
  const navigate = useNavigate()
  const { cart, isLoading, fetchCart, clearCart } = useCartStore()

  useEffect(() => {
    fetchCart()
  }, [])

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="page-shell flex items-center justify-center">
          <div className="surface-muted">Loading cart...</div>
        </div>
      </ProtectedRoute>
    )
  }

  if (!cart || cart.items.length === 0) {
    return (
      <ProtectedRoute>
        <div className="page-shell">
          <div className="max-w-7xl mx-auto px-4 py-12">
            <div className="text-center">
              <ShoppingBag size={64} className="mx-auto text-gray-400 dark:text-slate-600 mb-4" />
              <h2 className="text-2xl font-bold surface-heading mb-4">Your Cart is Empty</h2>
              <p className="surface-muted mb-8">Start shopping to add items to your cart</p>
              <button
                onClick={() => navigate('/')}
                className="btn-primary px-8 py-3 rounded-lg"
              >
                Continue Shopping
              </button>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    )
  }

  const totalPrice = cart.items.reduce((sum, item) => sum + (item.product?.price * item.quantity || 0), 0)

  return (
    <ProtectedRoute>
      <div className="page-shell py-12">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-3xl font-bold surface-heading mb-8">Shopping Cart</h1>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-4">
              {cart.items.map((item) => (
                <CartItem key={item.id} item={item} />
              ))}
            </div>

            <div className="surface-card rounded-lg shadow-md p-6 h-fit">
              <h2 className="text-xl font-bold surface-heading mb-4">Order Summary</h2>

              <div className="space-y-3 mb-6 border-b border-slate-200 dark:border-slate-800 pb-4">
                <div className="flex justify-between">
                  <span className="surface-muted">Subtotal</span>
                  <span>${totalPrice.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="surface-muted">Shipping</span>
                  <span>Free</span>
                </div>
              </div>

              <div className="flex justify-between text-xl font-bold mb-6">
                <span>Total</span>
                <span className="text-blue-600 dark:text-blue-400">${totalPrice.toFixed(2)}</span>
              </div>

              <button
                onClick={() => navigate('/checkout')}
                className="w-full btn-primary py-3 rounded-lg font-semibold mb-4"
              >
                Proceed to Checkout
              </button>

              <button
                onClick={() => navigate('/')}
                className="w-full btn-secondary border-blue-600 text-blue-600 dark:text-blue-400 py-3 rounded-lg font-semibold hover:bg-blue-50 dark:hover:bg-blue-950"
              >
                Continue Shopping
              </button>

              <button
                onClick={clearCart}
                className="w-full text-red-600 dark:text-red-400 py-3 text-sm mt-4 hover:text-red-800 dark:hover:text-red-300"
              >
                Clear Cart
              </button>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}
