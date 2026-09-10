import React from 'react'
import { ShoppingCart } from 'lucide-react'
import { useCartStore } from '../context/cartStore'
import ProductImage from './ProductImage'

export default function ProductCard({ product, onViewDetails }) {
  const [quantity, setQuantity] = React.useState(1)
  const [isLoading, setIsLoading] = React.useState(false)
  const addToCart = useCartStore((state) => state.addToCart)

  const handleAddToCart = async () => {
    if (!product.is_active) {
      alert('Product is not available')
      return
    }
    
    if (quantity > product.stock_quantity) {
      alert(`Only ${product.stock_quantity} items available`)
      return
    }

    setIsLoading(true)
    try {
      await addToCart(product.id, quantity)
      alert('Added to cart!')
      setQuantity(1)
    } catch (error) {
      alert('Failed to add to cart: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="surface-card rounded-lg shadow-md overflow-hidden hover:shadow-lg transition">
      <div className="bg-gray-200 dark:bg-slate-800 h-48 flex items-center justify-center overflow-hidden">
        <ProductImage
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover"
        />
      </div>

      {/* Product Info */}
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-2 truncate surface-heading">{product.name}</h3>
        <p className="surface-muted text-sm mb-2 line-clamp-2">{product.description}</p>

        {/* Category */}
        {product.category && (
          <div className="mb-2">
            <span className="text-xs bg-blue-100 dark:bg-blue-950 text-blue-800 dark:text-blue-300 px-2 py-1 rounded">
              {product.category}
            </span>
          </div>
        )}

        {/* Price and Stock */}
        <div className="flex justify-between items-center mb-3">
          <span className="text-2xl font-bold text-blue-600">${product.price.toFixed(2)}</span>
          <span className={`text-sm font-medium ${product.stock_quantity > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {product.stock_quantity > 0 ? `In Stock (${product.stock_quantity})` : 'Out of Stock'}
          </span>
        </div>

        {/* Quantity Selector */}
        {product.is_active && product.stock_quantity > 0 && (
          <div className="flex items-center space-x-2 mb-3">
            <button
              onClick={() => setQuantity(Math.max(1, quantity - 1))}
              className="px-2 py-1 border border-slate-300 dark:border-slate-700 rounded hover:bg-gray-100 dark:hover:bg-slate-800"
              disabled={isLoading}
            >
              -
            </button>
            <input
              type="number"
              min="1"
              max={product.stock_quantity}
              value={quantity}
              onChange={(e) => setQuantity(Math.min(product.stock_quantity, Math.max(1, parseInt(e.target.value))))}
              className="w-12 text-center border border-slate-300 dark:border-slate-700 rounded py-1 bg-white dark:bg-slate-900"
              disabled={isLoading}
            />
            <button
              onClick={() => setQuantity(Math.min(product.stock_quantity, quantity + 1))}
              className="px-2 py-1 border border-slate-300 dark:border-slate-700 rounded hover:bg-gray-100 dark:hover:bg-slate-800"
              disabled={isLoading}
            >
              +
            </button>
          </div>
        )}

        {/* Buttons */}
        <div className="flex space-x-2">
          <button
            onClick={handleAddToCart}
            disabled={!product.is_active || product.stock_quantity === 0 || isLoading}
            className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center space-x-2"
          >
            <ShoppingCart size={18} />
            <span>{isLoading ? 'Adding...' : 'Add to Cart'}</span>
          </button>
          <button
            onClick={() => onViewDetails(product.id)}
            className="flex-1 border border-blue-600 text-blue-600 dark:text-blue-400 py-2 rounded hover:bg-blue-50 dark:hover:bg-blue-950"
          >
            View Details
          </button>
        </div>
      </div>
    </div>
  )
}
