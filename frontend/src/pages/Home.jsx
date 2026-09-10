import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ProductGrid from '../components/ProductGrid'
import { getProducts } from '../services/products'
import { Search } from 'lucide-react'

export default function Home() {
  const [products, setProducts] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchProducts = async () => {
      setIsLoading(true)
      try {
        const data = await getProducts(currentPage, 12, searchTerm, categoryFilter)
        setProducts(data)
      } catch (error) {
        alert('Failed to load products: ' + error.message)
      } finally {
        setIsLoading(false)
      }
    }

    fetchProducts()
  }, [currentPage, searchTerm, categoryFilter])

  const handleViewDetails = (productId) => {
    navigate(`/products/${productId}`)
  }

  return (
    <div className="page-shell">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-4xl font-bold mb-4">Welcome to AI Store</h1>
          <p className="text-xl mb-8">Shop smarter with AI-powered recommendations</p>

          {/* Search Bar */}
          <div className="flex space-x-2">
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value)
                setCurrentPage(1)
              }}
              className="input-field flex-1 py-3"
            />
            <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100">
              <Search size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Filters */}
        <div className="mb-8 flex space-x-4">
          <select
            value={categoryFilter}
            onChange={(e) => {
              setCategoryFilter(e.target.value)
              setCurrentPage(1)
            }}
            className="input-field"
          >
            <option value="">All Categories</option>
            <option value="Electronics">Electronics</option>
            <option value="Computers">Computers</option>
            <option value="Audio">Audio</option>
            <option value="Accessories">Accessories</option>
            <option value="Wearables">Wearables</option>
          </select>
        </div>

        {/* Products Grid */}
        <ProductGrid
          products={products}
          onViewDetails={handleViewDetails}
          isLoading={isLoading}
        />

        {/* Pagination */}
        {!isLoading && products.length > 0 && (
          <div className="flex justify-center space-x-2 mt-12">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="btn-secondary px-4 py-2 rounded-lg disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-4 py-2">Page {currentPage}</span>
            <button
              onClick={() => setCurrentPage(currentPage + 1)}
              className="px-4 py-2 border rounded hover:bg-gray-100"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
