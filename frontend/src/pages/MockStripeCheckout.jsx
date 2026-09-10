import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { getOrder } from '../services/orders'
import {
  mockCompletePayment,
  mockFailPayment,
  mockCancelPayment,
} from '../services/payments'
import { ProtectedRoute } from '../components/ProtectedRoute'
import { CreditCard, CheckCircle, XCircle, Ban } from 'lucide-react'

export default function MockStripeCheckout() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const sessionId = searchParams.get('session_id') || ''
  const orderId = searchParams.get('order_id') || ''
  const [order, setOrder] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!sessionId || !orderId) {
      setError('Invalid checkout session.')
      setIsLoading(false)
      return
    }

    const loadOrder = async () => {
      try {
        const data = await getOrder(orderId)
        setOrder(data)
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to load order details.')
      } finally {
        setIsLoading(false)
      }
    }

    loadOrder()
  }, [sessionId, orderId])

  const handleSuccess = async () => {
    setIsProcessing(true)
    setError('')
    try {
      await mockCompletePayment(sessionId)
      navigate(`/orders?payment=success&session_id=${sessionId}`, { replace: true })
    } catch (err) {
      setError(err?.response?.data?.detail || 'Mock payment failed.')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleFail = async () => {
    setIsProcessing(true)
    setError('')
    try {
      await mockFailPayment(sessionId)
      navigate(`/orders/${orderId}?payment=failed`, { replace: true })
    } catch (err) {
      setError(err?.response?.data?.detail || 'Could not simulate failed payment.')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleCancel = async () => {
    setIsProcessing(true)
    setError('')
    try {
      await mockCancelPayment(sessionId)
      navigate('/checkout?payment=cancelled', { replace: true })
    } catch (err) {
      setError(err?.response?.data?.detail || 'Could not cancel payment.')
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="page-shell py-12 px-4">
        <div className="max-w-lg mx-auto">
          <div className="surface-card rounded-xl shadow-lg overflow-hidden">
            <div className="bg-indigo-600 px-6 py-5 text-white">
              <div className="flex items-center gap-3">
                <CreditCard size={28} />
                <div>
                  <h1 className="text-xl font-bold">Stripe Checkout (Demo Mode)</h1>
                  <p className="text-indigo-100 text-sm">Simulated payment — dummy keys active</p>
                </div>
              </div>
            </div>

            <div className="p-6">
              {isLoading ? (
                <p className="text-slate-500 text-sm">Loading order…</p>
              ) : error && !order ? (
                <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
                  {error}
                </div>
              ) : (
                <>
                  <div className="mb-6 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-4">
                    <p className="text-sm text-slate-500 mb-1">Order #{orderId}</p>
                    <p className="text-2xl font-bold text-slate-900">
                      ${Number(order?.total_amount || 0).toFixed(2)}
                    </p>
                    <p className="text-xs text-slate-400 mt-2 break-all">Session: {sessionId}</p>
                  </div>

                  <div className="mb-6 rounded-lg bg-blue-50 border border-blue-200 p-4 text-sm text-blue-900">
                    <p className="font-semibold mb-1">Test card (for real Stripe mode)</p>
                    <p>4242 4242 4242 4242 · any future expiry · any CVC</p>
                  </div>

                  {error && (
                    <div className="mb-4 rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
                      {error}
                    </div>
                  )}

                  <div className="space-y-3">
                    <button
                      type="button"
                      onClick={handleSuccess}
                      disabled={isProcessing}
                      className="w-full flex items-center justify-center gap-2 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50"
                    >
                      <CheckCircle size={18} />
                      {isProcessing ? 'Processing…' : 'Pay Successfully'}
                    </button>
                    <button
                      type="button"
                      onClick={handleFail}
                      disabled={isProcessing}
                      className="w-full flex items-center justify-center gap-2 bg-red-600 text-white py-3 rounded-lg font-semibold hover:bg-red-700 disabled:opacity-50"
                    >
                      <XCircle size={18} />
                      Simulate Failed Payment
                    </button>
                    <button
                      type="button"
                      onClick={handleCancel}
                      disabled={isProcessing}
                      className="w-full flex items-center justify-center gap-2 btn-secondary py-3 rounded-lg font-semibold disabled:opacity-50"
                    >
                      <Ban size={18} />
                      Cancel Payment
                    </button>
                  </div>

                  <p className="text-xs text-slate-500 mt-6 text-center">
                    Payment is confirmed server-side (webhook logic) before the order is marked PAID.
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}
