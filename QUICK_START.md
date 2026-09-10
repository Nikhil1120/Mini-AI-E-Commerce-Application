# Quick Start Guide - AI E-Commerce Platform

Get the full-stack application running in 5 minutes!

## Prerequisites

- Node.js 16+ 
- Python 3.8+
- MongoDB running locally
- Google OAuth credentials
- Stripe API keys

## 1. Backend Setup (2 minutes)

### Terminal 1: Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Create .env file
echo DATABASE_URL=mongodb://localhost:27017/ecommerce > .env
echo GOOGLE_CLIENT_ID=your_id >> .env
echo GOOGLE_CLIENT_SECRET=your_secret >> .env
echo JWT_SECRET_KEY=your_secret >> .env
echo STRIPE_SECRET_KEY=your_key >> .env
echo STRIPE_PUBLISHABLE_KEY=your_key >> .env
echo GROQ_API_KEY=your_key >> .env

uvicorn main:app --reload --port 8000
```

✅ Backend runs at `http://localhost:8000`
📚 API Docs: `http://localhost:8000/docs`

## 2. Frontend Setup (2 minutes)

### Terminal 2: Start Frontend

```bash
cd frontend
npm install

# Create .env.local file
echo VITE_API_URL=http://localhost:8000 > .env.local
echo VITE_GOOGLE_CLIENT_ID=your_id >> .env.local
echo VITE_STRIPE_PUBLIC_KEY=your_key >> .env.local

npm run dev
```

✅ Frontend runs at `http://localhost:5173`

## 3. Login & Test (1 minute)

1. Open `http://localhost:5173`
2. Click "Demo Customer" or "Demo Admin" to login
3. Browse products, add to cart, checkout

## Test Accounts

### Customer Demo
- Click "Demo Customer"
- Access: Products, Cart, Orders, AI Chat

### Admin Demo
- Click "Demo Admin"
- Access: All customer features + Admin Dashboard, Product Manager, Order Manager

## API Testing

Test API endpoints using Swagger:
```
http://localhost:8000/docs
```

### Test Products
```bash
curl http://localhost:8000/products?page=1&limit=10
```

### Test Auth
```bash
curl -X POST http://localhost:8000/auth/google-login \
  -H "Content-Type: application/json" \
  -d '{"credential": "token"}'
```

## Common Commands

### Backend
```bash
# Run development server
uvicorn main:app --reload

# Run with specific port
uvicorn main:app --reload --port 8000

# Install new package
pip install package_name

# Add to requirements
pip freeze > requirements.txt
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Install new package
npm install package_name
```

## Project Structure Overview

```
assignment2/
├── backend/                    # FastAPI server
│   ├── main.py                # API setup
│   ├── routers/               # API routes
│   ├── models.py              # Database models
│   ├── schemas.py             # Request/response schemas
│   ├── config.py              # Configuration
│   ├── database.py            # DB connection
│   └── requirements.txt
│
└── frontend/                   # React Vite app
    ├── src/
    │   ├── App.jsx            # Main routing
    │   ├── components/        # Reusable components
    │   ├── pages/             # Page components
    │   ├── services/          # API clients
    │   ├── context/           # State management
    │   └── main.jsx           # Entry point
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

## Features to Test

### Shopping
- [ ] Browse products on home page
- [ ] Search products
- [ ] Filter by category
- [ ] View product details
- [ ] Add product to cart
- [ ] Update cart quantities
- [ ] Remove from cart
- [ ] Clear cart
- [ ] Proceed to checkout

### Orders
- [ ] Create order from cart
- [ ] View order history
- [ ] View order details
- [ ] See order status

### Admin
- [ ] View dashboard stats
- [ ] Add new product
- [ ] Edit product
- [ ] Delete product
- [ ] View all orders
- [ ] Update order status

### AI Assistant
- [ ] Open chat widget
- [ ] Send message to AI
- [ ] Get product recommendations

## Troubleshooting

### Backend Issues

**Port 8000 already in use**
```bash
# Use different port
uvicorn main:app --reload --port 8001
# Update frontend VITE_API_URL in .env.local
```

**MongoDB connection error**
```bash
# Ensure MongoDB is running
mongod --dbpath data/

# Check connection string in .env
DATABASE_URL=mongodb://localhost:27017/ecommerce
```

**Missing dependencies**
```bash
pip install -r requirements.txt
```

### Frontend Issues

**Port 5173 already in use**
```bash
# Change port in vite.config.js server.port
# Or use different port
npm run dev -- --port 5174
```

**Module not found**
```bash
rm -rf node_modules package-lock.json
npm install
```

**API not connecting**
- Verify backend is running on http://localhost:8000
- Check VITE_API_URL in .env.local
- Check browser console for CORS errors

**Blank page after login**
- Check browser console for errors
- Ensure backend token validation is working
- Clear localStorage and try again

## Environment Setup

### Backend .env
```
DATABASE_URL=mongodb://localhost:27017/ecommerce
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET_KEY=your_super_secret_key
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
GROQ_API_KEY=your_groq_api_key
```

### Frontend .env.local
```
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_STRIPE_PUBLIC_KEY=pk_test_xxx
```

## Development Tips

### Hot Reload
- Frontend: Automatic (Vite)
- Backend: Use `--reload` flag with uvicorn

### Debug Mode
```bash
# Backend
export DEBUG=True
uvicorn main:app --reload

# Frontend
# Check Chrome DevTools console
```

### Database Inspection
```bash
# Connect to MongoDB
mongosh

# Use database
use ecommerce

# View collections
db.getCollectionNames()

# Query data
db.users.find()
db.products.find()
db.orders.find()
```

## Next Steps

1. **Customize**: Update brand, colors, and styling
2. **Deploy**: Push to GitHub, deploy to cloud
3. **Add Features**: Extend with more functionality
4. **Secure**: Add HTTPS, secure credentials
5. **Monitor**: Set up logging and analytics

## Useful Links

- 📖 Project Guide: [PROJECT_GUIDE.md](PROJECT_GUIDE.md)
- 📖 Backend Docs: [backend/README.md](backend/README.md)
- 📖 Frontend Docs: [frontend/README.md](frontend/README.md)
- 🔧 FastAPI: https://fastapi.tiangolo.com
- ⚛️ React: https://react.dev
- 🌾 Vite: https://vitejs.dev
- 📦 MongoDB: https://docs.mongodb.com
- 💳 Stripe: https://stripe.com/docs

## Getting Help

1. Check error messages in console
2. Review logs in terminal
3. Verify environment variables
4. Check API documentation at `/docs`
5. Review code in relevant files

## Production Deployment

### Backend (Heroku Example)
```bash
heroku create your-app-name
git push heroku main
heroku config:set DATABASE_URL=...
```

### Frontend (Netlify/Vercel)
```bash
npm run build
# Deploy dist/ folder to Netlify or Vercel
```

---

**Ready to develop!** 🚀

Start both servers and navigate to http://localhost:5173
