import React from 'react'
import { Trash2, Plus, Minus } from 'lucide-react'
import { useCartStore } from '../context/cartStore'
import ProductImage from './ProductImage'

export default function CartItem({ item }) {
  const [quantity, setQuantity] = React.useState(item.quantity)
  const [isLoading, setIsLoading] = React.useState(false)
  const updateCartItem = useCartStore((state) => state.updateCartItem)
  const removeFromCart = useCartStore((state) => state.removeFromCart)

  const handleQuantityChange = async (newQuantity) => {
    if (newQuantity < 1) return
    if (newQuantity > item.product.stock_quantity) {
      alert('Insufficient stock')
      return
    }

    setIsLoading(true)
    try {
      setQuantity(newQuantity)
      await updateCartItem(item.id, newQuantity)
    } catch (error) {
      alert('Failed to update cart: ' + error.message)
      setQuantity(item.quantity)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRemove = async () => {
    setIsLoading(true)
    try {
      await removeFromCart(item.id)
    } catch (error) {
      alert('Failed to remove item: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="surface-card rounded-lg shadow p-4 flex items-center space-x-4">
      {/* Product Image */}
      <div className="w-20 h-20 bg-gray-200 dark:bg-slate-800 rounded flex-shrink-0 overflow-hidden">
        <ProductImage
          src={item.product?.image_url}
          alt={item.product?.name || 'Product'}
          className="w-full h-full object-cover"
        />
      </div>

      {/* Product Info */}
      <div className="flex-grow">
        <h3 className="font-semibold">{item.product?.name}</h3>
        <p className="surface-muted text-sm">${item.product?.price.toFixed(2)}</p>
      </div>

      {/* Quantity Controls */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => handleQuantityChange(quantity - 1)}
          disabled={isLoading || quantity <= 1}
          className="p-1 border border-slate-300 dark:border-slate-700 rounded hover:bg-gray-100 dark:hover:bg-slate-800 disabled:opacity-50"
        >
          <Minus size={18} />
        </button>
        <span className="w-8 text-center font-semibold">{quantity}</span>
        <button
          onClick={() => handleQuantityChange(quantity + 1)}
          disabled={isLoading || quantity >= item.product?.stock_quantity}
          className="p-1 border border-slate-300 dark:border-slate-700 rounded hover:bg-gray-100 dark:hover:bg-slate-800 disabled:opacity-50"
        >
          <Plus size={18} />
        </button>
      </div>

      {/* Subtotal */}
      <div className="w-24 text-right">
        <p className="font-semibold">${(item.product?.price * quantity).toFixed(2)}</p>
      </div>

      {/* Remove Button */}
      <button
        onClick={handleRemove}
        disabled={isLoading}
        className="p-2 text-red-500 hover:bg-red-50 rounded disabled:opacity-50"
      >
        <Trash2 size={20} />
      </button>
    </div>
  )
}
