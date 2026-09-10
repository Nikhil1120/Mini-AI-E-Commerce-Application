# AI E-Commerce Backend - API Documentation

Complete FastAPI backend with MongoDB, Google OAuth, Stripe integration, and AI chatbot functionality.

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB with Motor (async)
- **ORM**: SQLAlchemy 2.0
- **Auth**: Google OAuth + JWT (python-jose)
- **AI**: LangChain + Groq
- **Payment**: Stripe
- **Server**: Uvicorn

## Project Structure

```
backend/
├── main.py              # FastAPI app & route imports
├── config.py            # Environment configuration
├── database.py          # MongoDB connection
├── requirements.txt     # Python dependencies
├── models/             # SQLAlchemy models
│   ├── __init__.py
│   ├── user.py
│   ├── product.py
│   ├── cart.py
│   ├── order.py
│   └── order_item.py
├── routes/             # API endpoints
│   ├── __init__.py
│   ├── auth.py
│   ├── products.py
│   ├── cart.py
│   ├── orders.py
│   ├── payments.py
│   ├── admin.py
│   └── ai.py
└── schemas/            # Pydantic models
    ├── __init__.py
    ├── user.py
    ├── product.py
    ├── order.py
    └── ai.py
```

## Installation

### Prerequisites
- Python 3.8+
- MongoDB running on localhost:27017
- Google OAuth credentials
- Stripe API keys
- Groq API key

### Setup Steps

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
Create `.env` file:
```
DATABASE_URL=mongodb://localhost:27017/ecommerce
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
JWT_SECRET_KEY=your_secret_key
STRIPE_SECRET_KEY=your_secret_key
STRIPE_PUBLISHABLE_KEY=your_publishable_key
GROQ_API_KEY=your_groq_api_key
```

4. **Run server**
```bash
uvicorn main:app --reload --port 8000
```

Access API docs at `http://localhost:8000/docs`

## API Endpoints

### Authentication Routes (`/auth`)

#### Google Login
```
POST /auth/google-login
Content-Type: application/json

{
  "credential": "google_token"
}

Response:
{
  "access_token": "jwt_token",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "name": "User Name",
    "role": "CUSTOMER"
  }
}
```

#### Get Current User
```
GET /auth/me
Authorization: Bearer {token}

Response:
{
  "id": "user_id",
  "email": "user@example.com",
  "name": "User Name",
  "role": "CUSTOMER"
}
```

#### Logout
```
POST /auth/logout
Authorization: Bearer {token}

Response:
{
  "message": "Logged out successfully"
}
```

### Products Routes (`/products`)

#### List Products
```
GET /products?page=1&limit=10&search=&category=

Query Parameters:
- page: Page number (default: 1)
- limit: Items per page (default: 10)
- search: Search term (optional)
- category: Category filter (optional)

Response:
{
  "items": [
    {
      "id": "product_id",
      "name": "Product Name",
      "description": "Description",
      "price": 99.99,
      "category": "Category",
      "image_url": "url",
      "stock_quantity": 10,
      "is_active": true
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 10
}
```

#### Get Product Details
```
GET /products/{product_id}

Response:
{
  "id": "product_id",
  "name": "Product Name",
  "description": "Description",
  "price": 99.99,
  "category": "Category",
  "image_url": "url",
  "stock_quantity": 10,
  "is_active": true
}
```

#### Create Product (Admin)
```
POST /products
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Product Name",
  "description": "Description",
  "price": 99.99,
  "category": "Category",
  "image_url": "url",
  "stock_quantity": 10
}

Response: Created product object
```

#### Update Product (Admin)
```
PUT /products/{product_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated Name",
  "price": 129.99,
  "stock_quantity": 5,
  ...
}
```

#### Delete Product (Admin)
```
DELETE /products/{product_id}
Authorization: Bearer {token}
```

### Cart Routes (`/cart`)

#### Get Cart
```
GET /cart
Authorization: Bearer {token}

Response:
{
  "id": "cart_id",
  "user_id": "user_id",
  "items": [
    {
      "id": "item_id",
      "product_id": "product_id",
      "name": "Product Name",
      "price": 99.99,
      "quantity": 2,
      "subtotal": 199.98
    }
  ],
  "total": 199.98
}
```

#### Add to Cart
```
POST /cart/items
Authorization: Bearer {token}
Content-Type: application/json

{
  "product_id": "product_id",
  "quantity": 2
}

Response: Updated cart
```

#### Update Cart Item
```
PUT /cart/items/{item_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "quantity": 3
}

Response: Updated cart
```

#### Remove from Cart
```
DELETE /cart/items/{item_id}
Authorization: Bearer {token}

Response: Updated cart
```

#### Clear Cart
```
DELETE /cart
Authorization: Bearer {token}

Response: {
  "message": "Cart cleared"
}
```

### Orders Routes (`/orders`)

#### Get User Orders
```
GET /orders?page=1&limit=10
Authorization: Bearer {token}

Response:
{
  "items": [
    {
      "id": "order_id",
      "user_id": "user_id",
      "total_amount": 199.98,
      "status": "PENDING",
      "payment_status": "UNPAID",
      "created_at": "2026-09-09T10:00:00Z",
      "items": [...]
    }
  ],
  "total": 10,
  "page": 1
}
```

#### Get Order Details
```
GET /orders/{order_id}
Authorization: Bearer {token}

Response:
{
  "id": "order_id",
  "user_id": "user_id",
  "total_amount": 199.98,
  "status": "PENDING",
  "payment_status": "UNPAID",
  "created_at": "2026-09-09T10:00:00Z",
  "items": [
    {
      "product_id": "product_id",
      "name": "Product Name",
      "quantity": 2,
      "price": 99.99
    }
  ]
}
```

#### Create Order
```
POST /orders
Authorization: Bearer {token}

Response: Created order
```

### Admin Orders Routes (`/admin/orders`)

#### Get All Orders
```
GET /admin/orders?page=1&limit=10&status=
Authorization: Bearer {admin_token}

Query Parameters:
- page: Page number
- limit: Items per page
- status: Filter by status (PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED)

Response: List of all orders
```

#### Update Order Status
```
PUT /admin/orders/{order_id}/status
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "status": "SHIPPED",
  "payment_status": "PAID"
}

Response: Updated order
```

### Payments Routes (`/payments`)

#### Create Checkout Session
```
POST /payments/checkout-session
Authorization: Bearer {token}

Response:
{
  "session_id": "stripe_session_id",
  "publishable_key": "stripe_public_key"
}
```

### AI Routes (`/ai`)

#### Send Message to Chatbot
```
POST /ai/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "What products do you recommend?"
}

Response:
{
  "response": "AI response message"
}
```

## Database Models

### User
```
{
  _id: ObjectId,
  email: String,
  name: String,
  role: String (CUSTOMER, ADMIN),
  google_id: String,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Product
```
{
  _id: ObjectId,
  name: String,
  description: String,
  price: Float,
  category: String,
  image_url: String,
  stock_quantity: Integer,
  is_active: Boolean,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Cart
```
{
  _id: ObjectId,
  user_id: ObjectId,
  items: [{
    product_id: ObjectId,
    name: String,
    price: Float,
    quantity: Integer
  }],
  created_at: DateTime,
  updated_at: DateTime
}
```

### Order
```
{
  _id: ObjectId,
  user_id: ObjectId,
  items: [{
    product_id: ObjectId,
    name: String,
    quantity: Integer,
    price: Float
  }],
  total_amount: Float,
  status: String (PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED),
  payment_status: String (UNPAID, PAID, REFUNDED),
  created_at: DateTime,
  updated_at: DateTime
}
```

## Authentication Flow

1. User sends Google token to `/auth/google-login`
2. Backend verifies token with Google
3. Finds or creates user in database
4. Generates JWT token
5. Returns token and user info
6. Frontend stores token in localStorage
7. Subsequent requests include token in Authorization header
8. Backend validates JWT on each request

## Features

✅ Google OAuth authentication
✅ Role-based access control (CUSTOMER, ADMIN)
✅ Product catalog management
✅ Shopping cart operations
✅ Order processing
✅ Payment integration (Stripe)
✅ AI chatbot with LangChain + Groq
✅ Async database operations
✅ CORS enabled
✅ Request validation
✅ Error handling
✅ Swagger/OpenAPI docs

## Environment Variables

```
DATABASE_URL           # MongoDB connection string
GOOGLE_CLIENT_ID       # Google OAuth client ID
GOOGLE_CLIENT_SECRET   # Google OAuth client secret
JWT_SECRET_KEY         # Secret key for JWT tokens
STRIPE_SECRET_KEY      # Stripe secret API key
STRIPE_PUBLISHABLE_KEY # Stripe public API key
GROQ_API_KEY          # Groq API key for AI
```

## Error Handling

All endpoints return standard error format:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

## CORS Configuration

Backend is configured to accept requests from:
- `http://localhost:5173` (frontend dev server)
- `http://localhost:3000` (alternative)

Update CORS settings in `main.py` for production.

## Running with Docker

```bash
docker build -t ecommerce-backend .
docker run -p 8000:8000 -e DATABASE_URL=mongodb://host.docker.internal:27017/ecommerce ecommerce-backend
```

## Testing

```bash
pytest tests/
pytest tests/test_auth.py -v
pytest tests/test_products.py -v
```

## Deployment

### Production Checklist
- [ ] Set DEBUG=False
- [ ] Update CORS origins
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure error logging
- [ ] Set up monitoring
- [ ] Configure rate limiting
- [ ] Enable authentication

### Deployment Options
- AWS Lambda + API Gateway
- Google Cloud Run
- Azure App Service
- DigitalOcean App Platform
- Heroku
- Self-hosted on VPS

## Performance Tips

- Index frequently queried fields
- Use pagination for list endpoints
- Cache responses where possible
- Use async operations
- Monitor database query performance
- Configure connection pooling

## Support

- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- FastAPI: https://fastapi.tiangolo.com
- MongoDB: https://docs.mongodb.com
- Stripe: https://stripe.com/docs
- Groq: https://groq.com/docs

---

**Backend Last Updated**: 2026-09-09
**Status**: ✅ Complete - Production Ready
