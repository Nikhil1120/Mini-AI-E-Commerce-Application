# System Design

## Architecture Overview

```
                ┌───────────────────┐
                │    React + TS     │
                │ Tailwind/shadcn   │
                └─────────┬─────────┘
                          │ HTTP/REST
                          ▼
                ┌───────────────────┐
                │   FastAPI Backend │
                │                   │
                │ Auth (JWT/Google) │
                │ Products          │
                │ Cart              │
                │ Orders            │
                │ Payments (Stripe) │
                │ AI Agent          │
                └──────┬───────┬────┘
                       │       │
              ┌────────▼───┐   │
              │ PostgreSQL │   │ Tool calls
              │  (or SQLite)│   │
              └────────────┘   │
                               ▼
                  ┌────────────────────────┐
                  │    AI Agent            │
                  │ LangChain + Tools      │
                  └──────────┬─────────────┘
                             │
                    ┌────────▼────────┐
                    │ Gemini / OpenAI │
                    └─────────────────┘
```

## External Integrations

| Service | Flow |
|---------|------|
| Google OAuth | React → Google Sign-In → Backend verifies token → JWT |
| Stripe | Backend creates Checkout Session → User pays (or mock page) → Webhook/mock confirms |
| AI LLM | Backend agent calls DB tools → LLM formats response |

## Authentication Flow

1. User clicks "Sign in with Google" on React frontend
2. Google returns ID token (credential)
3. Frontend POSTs to `/auth/google`
4. Backend verifies token with Google API
5. Backend creates/finds user (always CUSTOMER for new users)
6. Backend returns JWT
7. Frontend stores token in localStorage
8. All API calls include `Authorization: Bearer <token>`

## Payment Flow

1. Customer adds items to cart
2. Customer clicks checkout → POST `/orders` (creates pending order)
3. POST `/payments/create-checkout-session` → Stripe session (or mock session with dummy keys)
4. Frontend redirects to Stripe Checkout (or `/checkout/mock` demo page)
5. Customer completes payment (or selects success/fail/cancel in demo mode)
6. Stripe sends `checkout.session.completed` webhook **or** mock endpoint confirms payment
7. Backend verifies webhook signature (real mode) or processes mock confirmation
8. Backend updates order: payment_status=PAID, status=CONFIRMED
9. Backend reduces product stock
10. Backend clears customer cart

**Important:** Payment is only confirmed via webhook (or mock-complete endpoint), never via frontend redirect alone.

## AI Agent Design

The AI agent uses LangChain tools that query the real database:

- `search_products(query)` — search catalog
- `get_product_by_name(name)` — get price/details
- `get_product_stock(name)` — check availability
- `get_my_orders(user_id)` — customer's orders
- `get_order_status(order_id, user_id)` — order status with ownership check

User identity comes from JWT — the AI never trusts user-provided IDs.

## Deployment (Implemented)

```
User → Vercel (React Frontend)
         ↓ HTTPS / REST + JWT
       Render (FastAPI Backend)
         ↓                    ↓
    Neon (PostgreSQL)    Stripe Webhook / Mock Checkout
                              ↑
                    Google OAuth (ID token verify)
```

**Assignment 1:** GitHub Pages (`Figma-to-Responsive-React-Page` repo)

**AWS production equivalent:** CloudFront + S3 (frontend), ALB + EC2/ECS (API), RDS (database), Secrets Manager, Route 53.

## Scaling Strategy

| Strategy | Why |
|----------|-----|
| Multiple FastAPI instances | Handle more concurrent requests |
| AWS Load Balancer | Distribute traffic across instances |
| Managed PostgreSQL (RDS) | Reliable, scalable database |
| Database indexes | Faster product/order queries |
| Redis caching | Cache product listings, reduce DB load |
| Background workers (Celery) | Offload email, webhook processing |
| Queue AI requests | Prevent LLM API overload |
| Rate-limit AI endpoints | Control costs and abuse |
| Cache frequent product data | Reduce repeated DB queries |
| S3 for product images | Offload static file serving |
| CloudFront CDN | Fast global image delivery |
| Separate AI microservice | Scale AI independently |
| Monitoring (CloudWatch/Datadog) | Detect issues early |
| Connection pooling (PgBouncer) | Efficient DB connections |
| Horizontal scaling | Add instances as traffic grows |
