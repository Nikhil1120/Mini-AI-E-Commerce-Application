import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getProduct } from '../services/products'
import { useCartStore } from '../context/cartStore'
import { ShoppingCart, ArrowLeft } from 'lucide-react'
import ProductImage from '../components/ProductImage'

export default function ProductDetails() {
  const { productId } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [quantity, setQuantity] = useState(1)
  const [isAdding, setIsAdding] = useState(false)
  const addToCart = useCartStore((state) => state.addToCart)

  useEffect(() => {
    const fetchProduct = async () => {
      setIsLoading(true)
      try {
        const data = await getProduct(productId)
        setProduct(data)
      } catch (error) {
        alert('Failed to load product: ' + error.message)
        navigate('/')
      } finally {
        setIsLoading(false)
      }
    }

    fetchProduct()
  }, [productId, navigate])

  const handleAddToCart = async () => {
    if (!product.is_active) {
      alert('Product is not available')
      return
    }

    if (quantity > product.stock_quantity) {
      alert(`Only ${product.stock_quantity} items available`)
      return
    }

    setIsAdding(true)
    try {
      await addToCart(product.id, quantity)
      alert('Added to cart!')
      navigate('/cart')
    } catch (error) {
      alert('Failed to add to cart: ' + error.message)
    } finally {
      setIsAdding(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Product not found</p>
          <button
            onClick={() => navigate('/')}
            className="text-blue-600 hover:text-blue-800"
          >
            ← Back to Products
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="page-shell py-12">
      <div className="max-w-7xl mx-auto px-4">
        {/* Back Button */}
        <button
          onClick={() => navigate('/')}
          className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 mb-8"
        >
          <ArrowLeft size={20} />
          <span>Back to Products</span>
        </button>

        {/* Product Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 surface-card rounded-lg shadow-md p-8">
          {/* Image */}
          <div className="bg-gray-200 rounded-lg h-96 overflow-hidden">
            <ProductImage
              src={product.image_url}
              alt={product.name}
              className="w-full h-full object-cover rounded"
            />
          </div>

          {/* Info */}
          <div>
            <h1 className="text-4xl font-bold mb-4">{product.name}</h1>

            {/* Category */}
            {product.category && (
              <div className="mb-4">
                <span className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded">
                  {product.category}
                </span>
              </div>
            )}

            {/* Price */}
            <div className="mb-6">
              <p className="text-gray-600 text-sm mb-2">Price</p>
              <p className="text-4xl font-bold text-blue-600">${product.price.toFixed(2)}</p>
            </div>

            {/* Stock Status */}
            <div className="mb-6">
              <p className="text-gray-600 text-sm mb-2">Availability</p>
              <p className={`text-lg font-semibold ${product.stock_quantity > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {product.stock_quantity > 0 ? `In Stock (${product.stock_quantity} available)` : 'Out of Stock'}
              </p>
            </div>

            {/* Description */}
            <div className="mb-8 pb-8 border-b">
              <p className="text-gray-600 text-lg">{product.description}</p>
            </div>

            {/* Quantity Selector */}
            {product.is_active && product.stock_quantity > 0 && (
              <div className="mb-8">
                <p className="text-gray-600 text-sm mb-3">Quantity</p>
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="px-4 py-2 border rounded hover:bg-gray-100"
                    disabled={isAdding}
                  >
                    -
                  </button>
                  <input
                    type="number"
                    min="1"
                    max={product.stock_quantity}
                    value={quantity}
                    onChange={(e) => setQuantity(Math.min(product.stock_quantity, Math.max(1, parseInt(e.target.value))))}
                    className="w-16 text-center border rounded py-2"
                    disabled={isAdding}
                  />
                  <button
                    onClick={() => setQuantity(Math.min(product.stock_quantity, quantity + 1))}
                    className="px-4 py-2 border rounded hover:bg-gray-100"
                    disabled={isAdding}
                  >
                    +
                  </button>
                </div>
              </div>
            )}

            {/* Add to Cart Button */}
            <button
              onClick={handleAddToCart}
              disabled={!product.is_active || product.stock_quantity === 0 || isAdding}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center space-x-2 text-lg"
            >
              <ShoppingCart size={24} />
              <span>{isAdding ? 'Adding to Cart...' : 'Add to Cart'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
