import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { useAuthStore } from './context/authStore'
import { CustomerRoute, AdminRoute } from './components/ProtectedRoute'

import Navbar from './components/Navbar'
import AIChatbot from './components/AIChatbot'

import Home from './pages/Home'
import Login from './pages/Login'
import ProductDetails from './pages/ProductDetails'
import Cart from './pages/Cart'
import Checkout from './pages/Checkout'
import MockStripeCheckout from './pages/MockStripeCheckout'
import Orders from './pages/Orders'
import OrderDetails from './pages/OrderDetails'
import AdminDashboard from './pages/AdminDashboard'
import AdminProducts from './pages/AdminProducts'
import AdminOrders from './pages/AdminOrders'
import Profile from './pages/Profile'

function AppContent() {
  const checkAuth = useAuthStore((state) => state.checkAuth)

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  return (
    <Router>
      <div className="page-shell">
        <Navbar />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Home />} />
          <Route path="/products/:productId" element={<ProductDetails />} />
          <Route path="/profile" element={<Profile />} />

          <Route
            path="/cart"
            element={
              <CustomerRoute>
                <Cart />
              </CustomerRoute>
            }
          />
          <Route
            path="/checkout"
            element={
              <CustomerRoute>
                <Checkout />
              </CustomerRoute>
            }
          />
          <Route
            path="/checkout/mock"
            element={
              <CustomerRoute>
                <MockStripeCheckout />
              </CustomerRoute>
            }
          />
          <Route
            path="/orders"
            element={
              <CustomerRoute>
                <Orders />
              </CustomerRoute>
            }
          />
          <Route
            path="/orders/:orderId"
            element={
              <CustomerRoute>
                <OrderDetails />
              </CustomerRoute>
            }
          />

          <Route
            path="/admin"
            element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/products"
            element={
              <AdminRoute>
                <AdminProducts />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/orders"
            element={
              <AdminRoute>
                <AdminOrders />
              </AdminRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <AIChatbot />
      </div>
    </Router>
  )
}

function App() {
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''

  if (!googleClientId) {
    console.warn('VITE_GOOGLE_CLIENT_ID is not set — use dev login buttons on /login')
  }

  return (
    <GoogleOAuthProvider clientId={googleClientId || 'missing-client-id'}>
      <AppContent />
    </GoogleOAuthProvider>
  )
}

export default App
