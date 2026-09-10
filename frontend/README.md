# AI E-Commerce Frontend

React + Vite + JavaScript Frontend for AI-powered E-Commerce Platform

## Features

- 🛍️ Product browsing and filtering
- 🛒 Shopping cart management
- 💳 Checkout and order processing
- 📦 Order tracking and history
- 🤖 AI chatbot assistant
- 👤 User authentication (Google OAuth)
- 👨‍💼 Admin dashboard
- 📊 Product and order management
- 📱 Responsive design

## Tech Stack

- React 18
- Vite
- JavaScript
- Tailwind CSS
- Zustand (State Management)
- React Router
- Axios
- Lucide Icons
- Google OAuth

## Project Structure

```
src/
├── components/       # Reusable UI components
├── pages/           # Page components
├── services/        # API services
├── context/         # Context API with reducers
├── assets/          # Static assets
└── App.jsx          # Main app component
```

## Context Structure

The application uses a modular context system with separate modules for:

- **Auth**: User authentication and login state
- **Cart**: Shopping cart management
- **Products**: Product listing and details
- **Orders**: Order management

Each module contains:
- `state.js` - State hooks
- `actions.js` - Action types
- `reducer.js` - Reducer logic
- `contextState.js` - Context provider

## Getting Started

### Installation

```bash
npm install
```

### Environment Setup

Create `.env.local`:

```
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_STRIPE_PUBLIC_KEY=your_stripe_public_key
```

### Development

```bash
npm run dev
```

Server runs at `http://localhost:5173`

### Build

```bash
npm run build
```

### Preview

```bash
npm run preview
```

## API Integration

All API calls are made through the `services/` directory:

- `api.js` - Axios instance with interceptors
- `auth.js` - Authentication endpoints
- `products.js` - Product endpoints
- `cart.js` - Cart endpoints
- `orders.js` - Order endpoints
- `payments.js` - Payment endpoints
- `ai.js` - AI chatbot endpoints

## Features

### Authentication
- Google OAuth login
- Demo accounts for testing
- Token-based authorization

### Shopping
- Browse products with filtering
- Add to cart
- View cart and proceed to checkout
- Complete orders

### Orders
- View order history
- Track order status
- View order details

### Admin
- Dashboard with stats
- Product management (CRUD)
- Order management
- Status updates

### AI Assistant
- Chat with AI for product recommendations
- Shopping assistance
- Available to logged-in users

## Styling

- Tailwind CSS for utility-first styling
- Responsive design
- Custom animations
- Dark mode ready

## Components

### Layout
- `Navbar` - Navigation bar
- `ProtectedRoute` - Route protection

### Product
- `ProductCard` - Individual product display
- `ProductGrid` - Product listing grid

### Cart & Checkout
- `CartItem` - Cart item component
- `OrderCard` - Order display

### Other
- `AIChatbot` - AI assistant widget

## Notes

- Backend API should be running on `http://localhost:8000`
- Demo login available without authentication
- Stripe integration is configured but requires setup
- Google OAuth requires client ID configuration
