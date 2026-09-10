# AI E-Commerce Platform - Complete Project Guide

## Project Overview

A full-stack e-commerce application with AI features, built with FastAPI backend and React + Vite frontend. The platform enables users to browse products, manage shopping carts, place orders, and interact with an AI assistant for personalized recommendations.

## Architecture

```
AI E-Commerce Platform
├── Backend (FastAPI)
│   ├── Authentication & Authorization
│   ├── Product Management
│   ├── Shopping Cart
│   ├── Order Processing
│   ├── Payment Integration (Stripe)
│   └── AI Chat (LangChain + Groq)
│
└── Frontend (React + Vite)
    ├── Product Browsing & Filtering
    ├── Shopping Cart Management
    ├── Order Checkout & Tracking
    ├── Admin Dashboard
    ├── AI Chatbot Widget
    └── User Authentication
```

## Tech Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB with Motor (async driver)
- **ORM**: SQLAlchemy 2.0
- **Authentication**: Google OAuth, JWT (python-jose)
- **AI**: LangChain + Groq API
- **Payments**: Stripe API
- **Server**: Uvicorn (ASGI)

### Frontend
- **Framework**: React 18.2.0
- **Build Tool**: Vite 5.0.0
- **Styling**: Tailwind CSS 3.3.0
- **Routing**: React Router DOM 6.20.0
- **HTTP Client**: Axios 1.6.0
- **State Management**: Context API with Reducers
- **Icons**: Lucide React 0.292.0
- **Auth**: Google OAuth (@react-oauth/google)
- **Payments**: Stripe (@stripe/react-stripe-js)

## Directory Structure

### Backend Structure
```
backend/
├── main.py                 # FastAPI app initialization
├── config.py              # Configuration (DATABASE_URL, API keys)
├── database.py            # MongoDB connection setup
├── requirements.txt       # Python dependencies
├── models/               # SQLAlchemy models
│   ├── user.py
│   ├── product.py
│   ├── cart.py
│   ├── order.py
│   └── order_item.py
├── routes/               # API route handlers
│   ├── auth.py
│   ├── products.py
│   ├── cart.py
│   ├── orders.py
│   ├── payments.py
│   ├── admin.py
│   └── ai.py
└── schemas/             # Pydantic request/response schemas
    ├── user.py
    ├── product.py
    ├── order.py
    └── ai.py
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── Navbar.jsx
│   │   ├── ProductCard.jsx
│   │   ├── ProductGrid.jsx
│   │   ├── CartItem.jsx
│   │   ├── OrderCard.jsx
│   │   ├── AIChatbot.jsx
│   │   └── ProtectedRoute.jsx
│   ├── pages/           # Page components
│   │   ├── Home.jsx
│   │   ├── ProductDetails.jsx
│   │   ├── Cart.jsx
│   │   ├── Checkout.jsx
│   │   ├── Orders.jsx
│   │   ├── OrderDetails.jsx
│   │   ├── Login.jsx
│   │   ├── AdminDashboard.jsx
│   │   ├── AdminProducts.jsx
│   │   └── AdminOrders.jsx
│   ├── services/        # API client functions
│   │   ├── api.js           (Axios instance with auth interceptor)
│   │   ├── auth.js          (Authentication)
│   │   ├── products.js      (Product operations)
│   │   ├── cart.js          (Cart operations)
│   │   ├── orders.js        (Order operations)
│   │   ├── payments.js      (Stripe)
│   │   └── ai.js            (AI chat)
│   ├── context/         # Context API with reducers
│   │   ├── auth/
│   │   │   ├── state.js
│   │   │   ├── actions.js
│   │   │   └── reducer.js
│   │   ├── cart/
│   │   ├── products/
│   │   ├── orders/
│   │   ├── combineState.js  (Combines all states)
│   │   ├── context.js       (Context creation)
│   │   ├── contextState.js  (Provider component)
│   │   └── index.js
│   ├── App.jsx          # Main app with routing
│   ├── ErrorBoundary.jsx
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.cjs
├── .env.local
├── .gitignore
└── README.md
```

## Installation & Setup

### Prerequisites
- Node.js 16+ (for frontend)
- Python 3.8+ (for backend)
- MongoDB instance running
- Google OAuth credentials
- Stripe API keys

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create `.env` in backend directory:
```
DATABASE_URL=mongodb://localhost:27017/ecommerce
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET_KEY=your_secret_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
GROQ_API_KEY=your_groq_api_key
```

5. **Run backend server**
```bash
uvicorn main:app --reload --port 8000
```

Backend API available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment variables**
Create `.env.local` in frontend directory:
```
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_STRIPE_PUBLIC_KEY=your_stripe_public_key
```

4. **Run development server**
```bash
npm run dev
```

Frontend available at `http://localhost:5173`

## API Endpoints

### Authentication
- `POST /auth/google-login` - Google OAuth login
- `POST /auth/logout` - Logout
- `GET /auth/me` - Get current user

### Products
- `GET /products` - List products (with pagination, search, filter)
- `GET /products/{id}` - Get product details
- `POST /products` - Create product (admin)
- `PUT /products/{id}` - Update product (admin)
- `DELETE /products/{id}` - Delete product (admin)

### Cart
- `GET /cart` - Get cart
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/{item_id}` - Update cart item
- `DELETE /cart/items/{item_id}` - Remove from cart
- `DELETE /cart` - Clear cart

### Orders
- `GET /orders` - Get user orders
- `GET /orders/{id}` - Get order details
- `POST /orders` - Create order
- `GET /admin/orders` - Get all orders (admin)
- `PUT /admin/orders/{id}/status` - Update order status (admin)

### Payments
- `POST /payments/checkout-session` - Create Stripe checkout session

### AI Chat
- `POST /ai/chat` - Send message to AI chatbot

## Features

### User Features
- ✅ User registration & login with Google OAuth
- ✅ Browse products with search and filtering
- ✅ View product details
- ✅ Add products to cart
- ✅ Manage shopping cart (add, update, remove)
- ✅ Checkout and place orders
- ✅ View order history
- ✅ Track order status
- ✅ AI chatbot for shopping assistance
- ✅ Responsive mobile-friendly UI

### Admin Features
- ✅ Admin dashboard with stats
- ✅ Manage products (Create, Read, Update, Delete)
- ✅ View all orders
- ✅ Update order status
- ✅ View sales reports

### Authentication & Security
- ✅ Google OAuth integration
- ✅ JWT-based authorization
- ✅ Role-based access control (Customer, Admin)
- ✅ Protected routes on frontend
- ✅ Secure token storage in localStorage
- ✅ Token refresh mechanism

## State Management

The frontend uses a modular Context API pattern with useReducer:

```
GlobalContext
├── Auth Module
│   ├── State: user, isAuthenticated, isLoading
│   ├── Actions: LOGIN, LOGOUT, SET_USER
│   └── Methods: login(), logout(), checkAuth()
├── Cart Module
│   ├── State: cart, items, isLoading
│   └── Methods: fetchCart(), addToCart(), updateCartItem(), removeFromCart(), clearCart()
├── Products Module
│   ├── State: products, currentProduct, isLoading
│   └── Methods: getProducts(), getProduct(), createProduct(), updateProduct(), deleteProduct()
└── Orders Module
    ├── State: orders, currentOrder, isLoading
    └── Methods: getOrders(), getOrder(), createOrder(), updateOrderStatus()
```

### Using Context in Components

```jsx
import { useContext } from 'react'
import { GlobalContext } from './context'

function MyComponent() {
  const context = useContext(GlobalContext)
  const { Auth, Cart, Products, Orders } = context
  
  // Access auth state
  const { user, isAuthenticated } = Auth
  
  // Call auth methods
  await Auth.login(credential)
  
  // Access cart state and methods
  const { items } = Cart
  await Cart.addToCart(productId, quantity)
}
```

## Component Architecture

### Layout Components
- **Navbar**: Navigation with role-based links
- **ProtectedRoute**: Route wrapper for auth protection

### Product Components
- **ProductCard**: Individual product display
- **ProductGrid**: Grid layout for products

### Cart & Order Components
- **CartItem**: Line item in cart
- **OrderCard**: Order summary display

### Pages
- **Home**: Product listing with filters
- **ProductDetails**: Single product view
- **Cart**: Shopping cart
- **Checkout**: Order confirmation
- **Orders**: Order history
- **OrderDetails**: Order tracking
- **Login**: Authentication
- **AdminDashboard**: Admin stats
- **AdminProducts**: Product management
- **AdminOrders**: Order management

### Special Components
- **AIChatbot**: Floating AI chat widget
- **ErrorBoundary**: Error handling wrapper

## Demo Accounts

### Customer Demo
- Click "Demo Customer" on login page
- Role: CUSTOMER

### Admin Demo
- Click "Demo Admin" on login page
- Role: ADMIN

No authentication required for demo accounts.

## Testing

### Backend Testing
```bash
cd backend
pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm run test
```

## Build & Deployment

### Backend Build
```bash
# Build Docker image (if using Docker)
docker build -t ecommerce-backend .

# Run Docker container
docker run -p 8000:8000 ecommerce-backend
```

### Frontend Build
```bash
cd frontend
npm run build
npm run preview
```

Build output in `dist/` directory

## Troubleshooting

### Backend Issues
- **MongoDB Connection**: Ensure MongoDB is running on localhost:27017
- **CORS Errors**: Check CORS configuration in main.py
- **Missing Dependencies**: Run `pip install -r requirements.txt`
- **Port Already in Use**: Change port in uvicorn command

### Frontend Issues
- **Port Conflict**: Change port in vite.config.js
- **Module Not Found**: Run `npm install`
- **API Not Connecting**: Verify backend is running on localhost:8000
- **Google OAuth Failed**: Verify VITE_GOOGLE_CLIENT_ID is correct

## Performance Optimization

### Frontend
- Lazy loading for routes
- Image optimization
- Memoized components
- Virtualized lists (if needed)

### Backend
- Database indexing
- Query optimization
- Caching with Redis (optional)
- Async operations with Motor

## Security Considerations

- ✅ HTTPS in production
- ✅ Environment variable for sensitive data
- ✅ CORS configuration
- ✅ JWT token expiration
- ✅ Input validation (Pydantic)
- ✅ XSS protection
- ✅ CSRF protection

## Future Enhancements

- [ ] Advanced search with filters
- [ ] Product reviews and ratings
- [ ] Wishlists
- [ ] Email notifications
- [ ] Payment history
- [ ] Refund processing
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Advanced analytics
- [ ] Recommendation engine

## Support & Documentation

- Frontend README: [frontend/README.md](frontend/README.md)
- Backend API Docs: `http://localhost:8000/docs` (Swagger)
- Vite Documentation: https://vitejs.dev
- React Documentation: https://react.dev
- FastAPI Documentation: https://fastapi.tiangolo.com
- MongoDB Documentation: https://docs.mongodb.com
- Stripe Documentation: https://stripe.com/docs

## License

MIT License - See LICENSE file for details

## Contributors

- Frontend Development
- Backend Development
- Full-stack Integration

---

**Project Last Updated**: 2026-09-09
**Status**: ✅ Complete - Ready for Development/Testing
