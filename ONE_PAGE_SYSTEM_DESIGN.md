# One-Page System Design — Mini AI E-Commerce

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              END USER (Browser)                              │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ HTTPS
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  FRONTEND — React + Vite + Tailwind (Vercel)                                 │
│  • Product catalog, cart, checkout UI                                        │
│  • Google Sign-In button (@react-oauth/google)                               │
│  • Admin dashboard                                                           │
│  • AI chat widget                                                            │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ REST API (Axios) + JWT Bearer
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  BACKEND — FastAPI (Render)                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ Auth Router │ │ Products    │ │ Cart/Orders │ │ Admin RBAC  │              │
│  │ JWT + Google│ │ + Payments  │ │             │ │             │              │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────────────┘              │
│         │               │               │                                    │
│         └───────────────┴───────────────┘                                    │
│                         │                                                    │
│              ┌──────────▼──────────┐    ┌──────────────────┐               │
│              │   SQLAlchemy ORM    │    │   AI Agent       │               │
│              │   Business Logic    │◄──►│ LangChain Tools  │               │
│              └──────────┬──────────┘    └────────┬─────────┘               │
└─────────────────────────┼────────────────────────┼──────────────────────────┘
                          │                        │
          ┌───────────────▼──────────────┐   ┌─────▼─────┐
          │  DATABASE — PostgreSQL (Neon) │   │ Gemini /  │
          │  users, products, carts,      │   │ OpenAI    │
          │  orders, payments           │   │ (optional)│
          └─────────────────────────────┘   └───────────┘

EXTERNAL SERVICES
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Google OAuth     │     │ Stripe Checkout  │     │ Deployment       │
│ ID token verify  │     │ + Webhooks       │     │ Vercel (FE)      │
│ on backend       │     │ (mock mode used  │     │ Render (API)     │
│                  │     │  in live demo)   │     │ Neon (DB)        │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

## Component Summary

| Component | Technology | Role |
|-----------|------------|------|
| **Frontend** | React, Vite, Tailwind, Zustand | UI, routing, state, API calls |
| **Backend** | FastAPI, Uvicorn, Pydantic | REST API, auth, business rules |
| **Database** | PostgreSQL (Neon) / SQLite (local) | Persistent data |
| **AI Agent** | LangChain + DB tools | Customer support; tool-router fallback without LLM keys |
| **Google Auth** | Google Identity + JWT | Login; RBAC (CUSTOMER / ADMIN) |
| **Stripe** | Checkout Session + Webhook | Payment flow (mock mode enabled for demo) |
| **Deployment** | Vercel + Render + Neon | Free-tier cloud hosting (AWS-ready architecture) |

## Key Flows

**Auth:** Browser → Google credential → `POST /auth/google` → JWT → all protected routes.

**Checkout:** Cart → Create order (PENDING) → Stripe/mock checkout → Webhook or mock-complete → PAID + stock reduced.

**AI:** User message → FastAPI `/ai/chat` → tools query DB (products/orders) → LLM or deterministic router → response.

## Deployment Approach (Used)

| Layer | Platform | Why |
|-------|----------|-----|
| Frontend | **Vercel** | Free, auto-deploy from GitHub, global CDN |
| Backend | **Render** | Free Python web service for FastAPI |
| Database | **Neon** | Free managed PostgreSQL |
| Assignment 1 UI | **GitHub Pages** | Static React build hosting |

*Production AWS equivalent: S3+CloudFront (frontend), EC2/ECS or Lambda (API), RDS (database), API Gateway, Secrets Manager.*

## Scaling (High Users + High AI Requests)

1. **Horizontal API scaling** — Multiple FastAPI instances behind a load balancer (AWS ALB / Render scaling).
2. **Database** — Read replicas, connection pooling (PgBouncer), indexes on `products`, `orders`, `users`.
3. **Caching** — Redis for product listings and session data; CDN for images (S3 + CloudFront).
4. **AI traffic** — Queue AI requests (Celery/RabbitMQ or SQS); rate-limit `/ai/chat`; cache common answers; separate AI microservice.
5. **Payments** — Stripe webhooks processed by background workers; idempotent handlers.
6. **Monitoring** — CloudWatch/Datadog, health checks, auto-scaling policies.

---

*Full details: [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) | Schema: [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) | API: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)*
