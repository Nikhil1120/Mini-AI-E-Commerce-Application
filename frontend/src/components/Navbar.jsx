import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'
import { ShoppingCart, User, Menu } from 'lucide-react'
import ThemeToggle from './ThemeToggle'

function NavLink({ to, children, className = '', onClick }) {
  return (
    <Link
      to={to}
      onClick={onClick}
      className={`surface-muted hover:text-blue-600 dark:hover:text-blue-400 transition-colors ${className}`}
    >
      {children}
    </Link>
  )
}

export default function Navbar() {
  const { user, isAuthenticated } = useAuthStore()
  const navigate = useNavigate()
  const [isOpen, setIsOpen] = React.useState(false)

  const closeMobile = () => setIsOpen(false)

  const actionGroup = (
    <div className="flex items-center gap-2 sm:gap-3">
      <ThemeToggle />

      {isAuthenticated && user?.role === 'CUSTOMER' && (
        <Link
          to="/cart"
          onClick={closeMobile}
          className="theme-toggle-btn inline-flex items-center gap-1 rounded-lg border px-3 py-2 transition-colors"
        >
          <ShoppingCart size={18} />
          <span className="hidden sm:inline">Cart</span>
        </Link>
      )}

      {isAuthenticated ? (
        <button
          type="button"
          onClick={() => {
            closeMobile()
            navigate('/profile')
          }}
          aria-label="Open profile"
          title="Profile"
          className="theme-toggle-btn inline-flex items-center justify-center rounded-lg border p-2 transition-colors"
        >
          <User size={18} />
        </button>
      ) : (
        <Link
          to="/login"
          onClick={closeMobile}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          Login
        </Link>
      )}
    </div>
  )

  return (
    <nav className="app-navbar sticky top-0 z-40 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center space-x-2" onClick={closeMobile}>
            <div className="text-2xl font-bold text-blue-600">🛍️</div>
            <span className="text-xl font-bold surface-heading">AI Store</span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <NavLink to="/">Home</NavLink>

            {isAuthenticated && user?.role === 'ADMIN' && (
              <>
                <NavLink to="/admin">Admin</NavLink>
                <NavLink to="/admin/products">Products</NavLink>
                <NavLink to="/admin/orders">Orders</NavLink>
              </>
            )}

            {isAuthenticated && user?.role === 'CUSTOMER' && (
              <NavLink to="/orders">Orders</NavLink>
            )}

            {actionGroup}
          </div>

          <div className="flex items-center gap-2 md:hidden">
            {actionGroup}
            <button
              type="button"
              onClick={() => setIsOpen(!isOpen)}
              className="theme-toggle-btn rounded-lg border p-2"
              aria-label="Toggle menu"
            >
              <Menu size={22} />
            </button>
          </div>
        </div>

        {isOpen && (
          <div className="md:hidden border-t border-[var(--app-border)] pb-4 pt-2 space-y-1">
            <NavLink to="/" className="block py-2" onClick={closeMobile}>Home</NavLink>
            {isAuthenticated && user?.role === 'CUSTOMER' && (
              <>
                <NavLink to="/orders" className="block py-2" onClick={closeMobile}>Orders</NavLink>
                <NavLink to="/cart" className="block py-2" onClick={closeMobile}>Cart</NavLink>
              </>
            )}
            {isAuthenticated && user?.role === 'ADMIN' && (
              <>
                <NavLink to="/admin" className="block py-2" onClick={closeMobile}>Admin</NavLink>
                <NavLink to="/admin/products" className="block py-2" onClick={closeMobile}>Products</NavLink>
                <NavLink to="/admin/orders" className="block py-2" onClick={closeMobile}>Orders</NavLink>
              </>
            )}
            {isAuthenticated && (
              <NavLink to="/profile" className="block py-2" onClick={closeMobile}>Profile</NavLink>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}
