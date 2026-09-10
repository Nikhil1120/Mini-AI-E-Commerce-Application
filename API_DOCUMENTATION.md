# API Documentation

Base URL (local): `http://localhost:8000`

Base URL (production): `https://mini-ai-e-commerce-application-x1eg.onrender.com`

Interactive docs: `/docs` (Swagger) | `/redoc`

All authenticated endpoints require header: `Authorization: Bearer <token>`

---

## AUTH

### POST /auth/google
Google OAuth login. Creates user as CUSTOMER if new.

**Request:**
```json
{ "credential": "google-id-token" }
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "user": { "id": 1, "email": "...", "role": "CUSTOMER" }
}
```

### POST /auth/dev-login (DEV_MODE only)
Development login without Google.

**Request:** `{ "email": "admin@ecommerce.local" }`

### GET /auth/me
Returns current authenticated user. **Auth required.**

### POST /auth/logout
Logout (client discards token).

---

## PRODUCTS

### GET /products
List active products. Supports `?page=1&limit=10&search=phone&category=electronics`

### GET /products/{id}
Get product details.

---

## ADMIN PRODUCTS

**Admin auth required for all endpoints below.**

### POST /admin/products
Create product.

### PUT /admin/products/{id}
Update product.

### DELETE /admin/products/{id}
Soft-delete (deactivate) product.

### PUT /admin/products/{id}/stock?stock_quantity=50
Update stock.

---

## CART

**Auth required.**

### GET /cart
Get current user's cart.

### POST /cart/items
Add item. `{ "product_id": 1, "quantity": 2 }`

### PUT /cart/items/{id}
Update quantity. `{ "quantity": 3 }`

### DELETE /cart/items/{id}
Remove item.

### DELETE /cart
Clear cart.

---

## ORDERS

**Auth required.**

### POST /orders
Create order from cart. Backend calculates total.

### GET /orders
List user's orders.

### GET /orders/{id}
Get order details (own orders only for customers).

### PUT /orders/{id}/items/{item_id}
Update quantity on a pending unpaid order. `{ "quantity": 3 }`

### DELETE /orders/{id}
Remove a pending, failed, or cancelled order. Paid orders cannot be removed.

---

## ADMIN ORDERS

**Admin auth required.**

### GET /admin/orders
List all orders.

### GET /admin/orders/{id}
Get any order.

### PUT /admin/orders/{id}/status
Update status. `{ "status": "SHIPPED", "payment_status": "PAID" }`

---

## PAYMENTS

### POST /payments/create-checkout-session
**Auth required.** Creates Stripe session for latest pending order.

**Response:**
```json
{
  "session_id": "cs_mock_1_abc123",
  "checkout_url": "http://localhost:5173/checkout/mock?session_id=...",
  "order_id": 1,
  "mock_mode": true
}
```

### GET /payments/verify-session/{session_id}
**Auth required.** Verifies payment status for the user's order. In real Stripe mode, can sync status from Stripe if webhook is delayed.

**Response:**
```json
{
  "session_id": "cs_mock_1_abc123",
  "order_id": 1,
  "payment_status": "PAID",
  "order_status": "CONFIRMED",
  "verified": true,
  "mock_mode": true
}
```

### POST /payments/mock-complete (mock mode only)
Simulates `checkout.session.completed`. **Auth required.**

**Request:** `{ "session_id": "cs_mock_1_abc123" }`

### POST /payments/mock-fail (mock mode only)
Simulates failed payment. **Auth required.**

### POST /payments/mock-cancel (mock mode only)
Simulates cancelled/expired checkout. **Auth required.**

### POST /payments/webhook
Stripe webhook. Handles `checkout.session.completed`, `checkout.session.expired`, `payment_intent.payment_failed`. Disabled in mock mode.

---

## AI

### POST /ai/chat
**Auth required.**

**Request:** `{ "message": "What is the price of iPhone 15?" }`

**Response:** `{ "response": "The price of iPhone 15 is $999.99." }`

---

## ADMIN DASHBOARD

### GET /admin/dashboard
**Admin auth required.** Returns product/order/revenue statistics.
