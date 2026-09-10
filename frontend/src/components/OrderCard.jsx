import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Minus, Trash2 } from 'lucide-react'
import { updateOrderItemQuantity, removeOrder } from '../services/orders'

export default function OrderCard({ order, onUpdate, onRemove }) {
  const [isLoading, setIsLoading] = useState(false)
  const [localOrder, setLocalOrder] = useState(order)

  React.useEffect(() => {
    setLocalOrder(order)
  }, [order])

  const isEditable =
    localOrder.payment_status === 'PENDING' && localOrder.status === 'PENDING'
  const canRemove = localOrder.payment_status !== 'PAID'

  const getStatusColor = (status) => {
    const colors = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      CONFIRMED: 'bg-blue-100 text-blue-800',
      PROCESSING: 'bg-purple-100 text-purple-800',
      SHIPPED: 'bg-indigo-100 text-indigo-800',
      DELIVERED: 'bg-green-100 text-green-800',
      CANCELLED: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getPaymentStatusColor = (status) => {
    const colors = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      PAID: 'bg-green-100 text-green-800',
      FAILED: 'bg-red-100 text-red-800',
      CANCELLED: 'bg-gray-100 text-gray-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const handleQuantityChange = async (item, newQuantity) => {
    if (!isEditable || newQuantity < 1 || isLoading) return

    setIsLoading(true)
    try {
      const updated = await updateOrderItemQuantity(localOrder.id, item.id, newQuantity)
      setLocalOrder(updated)
      onUpdate?.(updated)
    } catch (error) {
      alert(error?.response?.data?.detail || error.message || 'Failed to update quantity')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRemoveOrder = async () => {
    if (!canRemove || isLoading) return
    if (!window.confirm(`Remove order #${localOrder.id} from your orders?`)) return

    setIsLoading(true)
    try {
      await removeOrder(localOrder.id)
      onRemove?.(localOrder.id)
    } catch (error) {
      alert(error?.response?.data?.detail || error.message || 'Failed to remove order')
    } finally {
      setIsLoading(false)
    }
  }

  const date = new Date(localOrder.created_at).toLocaleDateString()

  return (
    <div className="surface-card rounded-lg shadow-md p-6">
      <div className="flex justify-between items-start mb-4 gap-4">
        <div>
          <h3 className="text-lg font-semibold">Order #{localOrder.id}</h3>
          <p className="surface-muted text-sm">{date}</p>
        </div>
        <div className="flex items-center gap-3">
          {canRemove && (
            <button
              type="button"
              onClick={handleRemoveOrder}
              disabled={isLoading}
              className="inline-flex items-center gap-1 text-red-600 hover:text-red-800 text-sm font-medium disabled:opacity-50"
            >
              <Trash2 size={16} />
              Remove
            </button>
          )}
          <Link
            to={`/orders/${localOrder.id}`}
            className="text-blue-600 hover:text-blue-800 font-medium text-sm"
          >
            View Details →
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div>
          <p className="surface-muted text-sm">Total</p>
          <p className="text-2xl font-bold text-blue-600">
            ${localOrder.total_amount.toFixed(2)}
          </p>
        </div>
        <div>
          <p className="surface-muted text-sm">Order Status</p>
          <span
            className={`inline-block px-3 py-1 rounded text-sm font-medium ${getStatusColor(localOrder.status)}`}
          >
            {localOrder.status}
          </span>
        </div>
        <div>
          <p className="surface-muted text-sm">Payment Status</p>
          <span
            className={`inline-block px-3 py-1 rounded text-sm font-medium ${getPaymentStatusColor(localOrder.payment_status)}`}
          >
            {localOrder.payment_status}
          </span>
        </div>
        <div>
          <p className="surface-muted text-sm">Items</p>
          <p className="text-xl font-semibold">{localOrder.items.length}</p>
        </div>
      </div>

      {localOrder.items.length > 0 && (
        <div className="border-t border-slate-200 dark:border-slate-800 pt-4">
          <p className="text-sm surface-muted mb-3">Items:</p>
          <div className="space-y-3">
            {localOrder.items.map((item) => (
              <div
                key={item.id}
                className="flex flex-wrap items-center justify-between gap-3 text-sm"
              >
                <div className="flex-grow min-w-[180px]">
                  <p className="font-medium">{item.product_name}</p>
                  <p className="text-gray-500 dark:text-slate-500">${item.price.toFixed(2)} each</p>
                </div>

                {isEditable ? (
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => handleQuantityChange(item, item.quantity - 1)}
                      disabled={isLoading || item.quantity <= 1}
                      className="p-1 border border-slate-300 dark:border-slate-700 rounded hover:bg-gray-100 dark:hover:bg-slate-800 disabled:opacity-50"
                      aria-label="Decrease quantity"
                    >
                      <Minus size={16} />
                    </button>
                    <span className="w-8 text-center font-semibold">{item.quantity}</span>
                    <button
                      type="button"
                      onClick={() => handleQuantityChange(item, item.quantity + 1)}
                      disabled={isLoading}
                      className="p-1 border border-slate-300 dark:border-slate-700 rounded hover:bg-gray-100 dark:hover:bg-slate-800 disabled:opacity-50"
                      aria-label="Increase quantity"
                    >
                      <Plus size={16} />
                    </button>
                  </div>
                ) : (
                  <span className="text-gray-600 dark:text-slate-400">Qty: {item.quantity}</span>
                )}

                <p className="font-semibold w-20 text-right">${item.subtotal.toFixed(2)}</p>
              </div>
            ))}
          </div>

          {isEditable && (
            <p className="text-xs text-gray-500 dark:text-slate-500 mt-3">
              You can adjust quantities or remove this order before payment is completed.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
