# Mini AI E-Commerce Application

Production-style mini e-commerce app demonstrating:

**Frontend UI → FastAPI → Auth → RBAC → Database → Business Logic → Stripe → Webhooks → AI Agent**

## Features

### Customer
- Google Sign-In / Logout
- Product listing, search, details, stock
- Cart (add / update / remove / clear)
- Checkout with Stripe test mode
- Order history and details
- AI support chatbot (real DB-backed tools)

### Admin
- Admin dashboard stats
- Product CRUD + stock updates
- View all orders / update status
- Backend-enforced RBAC (role never trusted from frontend)

## Tech Stack

| Layer | Stack |
|-------|--------|
| Frontend | React, Vite, Tailwind CSS, React Router, Axios, Zustand, Lucide, Google Identity |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| DB | PostgreSQL (prod) / SQLite (local) |
| Auth | Google OAuth + JWT |
| Payments | Stripe Checkout + webhooks |
| AI | LangChain + Gemini/OpenAI with tool calling (deterministic fallback) |

## Architecture

See [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) and [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md).

## Project Structure

```
assignment2/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── dependencies.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── routers/          # auth, products, cart, orders, payments, admin, ai
│   ├── services/         # google_auth, stripe_service, ai_service
│   ├── ai/               # agent + tools
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/
│   │   └── services/
│   └── .env.example
├── README.md
├── API_DOCUMENTATION.md
├── DATABASE_SCHEMA.md
└── SYSTEM_DESIGN.md
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL (optional; SQLite works locally)
- Google Cloud OAuth Client ID (Web application)
- Stripe account (test mode)
- Gemini and/or OpenAI API key (optional — tool router works without LLM)

## Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # then edit values

python seed.py
uvicorn main:app --reload --port 8000
```

- API: http://localhost:8000  
- Swagger: http://localhost:8000/docs  

### Promote an admin

After signing in once with Google:

```bash
python seed.py --promote-admin your-google-email@gmail.com
```

Or set `ADMIN_EMAIL` to that Google email before first login.

## Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env.local   # set VITE_GOOGLE_CLIENT_ID and VITE_API_URL
npm run dev
```

App: http://localhost:5173

## Google OAuth Setup

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → APIs & Services → Credentials
3. Create OAuth client ID → Application type: **Web application**
4. Authorized JavaScript origins: `http://localhost:5173`
5. Authorized redirect URIs: `http://localhost:5173` (and production URL when deploying)
6. Copy Client ID into:
   - `backend/.env` → `GOOGLE_CLIENT_ID`
   - `frontend/.env.local` → `VITE_GOOGLE_CLIENT_ID`

The backend verifies the Google ID token with `google.oauth2.id_token`. New users are always `CUSTOMER` unless their email matches `ADMIN_EMAIL`.

## Stripe Setup

### Demo mode (dummy keys — no Stripe account needed)

The app ships with placeholder Stripe keys in `.env` / `.env.example`. When dummy keys are detected (`STRIPE_MOCK_MODE=auto`), checkout uses a **simulated Stripe page** at `/checkout/mock` with:

- **Pay Successfully** → backend confirms payment (same logic as webhook)
- **Simulate Failed Payment** → `payment_status=FAILED`
- **Cancel Payment** → `payment_status=CANCELLED`

Flow: **Frontend → FastAPI → Mock Stripe Checkout → Backend verification → Order status update**

### Real Stripe test mode

1. Create a Stripe account and enable **test mode**
2. Copy Secret + Publishable keys into backend/frontend env files
3. Set `STRIPE_MOCK_MODE=false` in `backend/.env`
4. For local webhooks install [Stripe CLI](https://stripe.com/docs/stripe-cli):

```bash
stripe login
stripe listen --forward-to localhost:8000/payments/webhook
```

5. Put the CLI webhook signing secret into `STRIPE_WEBHOOK_SECRET`

### Payment business rules

- Order + OrderItems created with `PENDING` payment/status
- Stock is **not** reduced at order creation
- Only `checkout.session.completed` webhook sets `PAID` / `CONFIRMED`, reduces stock, clears cart
- Frontend success redirect alone never marks payment paid
- Failed payment → `FAILED` (no stock change)
- Expired/cancelled session → `CANCELLED` (no stock change)

Test card: `4242 4242 4242 4242`, any future expiry, any CVC.

## AI Setup

```env
AI_PROVIDER=gemini   # or openai, or leave keys empty for tool-router fallback
GEMINI_API_KEY=...
OPENAI_API_KEY=...
```

Tools (always use authenticated user from JWT):

- `get_product_by_name` / `search_products` / `get_product_stock`
- `get_my_orders` / `get_order_status`

## Database

SQLite (default):

```env
DATABASE_URL=sqlite:///./ecommerce.db
```

PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce
```

Tables are created on startup via `Base.metadata.create_all`. Run `python seed.py` for sample products.

## API Documentation

- Interactive: `/docs` and `/redoc`
- Written reference: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

## Demo / Admin Credentials

There are **no passwords**. Auth is Google OAuth only.

- Seed creates/promotes admin via `ADMIN_EMAIL` or `--promote-admin`
- Never commit real `.env` secrets

## Testing

```bash
cd backend
pytest -q
```

## Live Demo URLs

| Service | URL |
|---------|-----|
| **Frontend** | https://mini-ai-e-commerce-application-bnmpf5vmx.vercel.app |
| **Backend API** | https://mini-ai-e-commerce-application-x1eg.onrender.com |
| **API Docs (Swagger)** | https://mini-ai-e-commerce-application-x1eg.onrender.com/docs |
| **GitHub** | https://github.com/Nikhil1120/Mini-AI-E-Commerce-Application |

## Deployment (Used — Free Tier)

| Layer | Platform |
|-------|----------|
| Frontend | Vercel |
| Backend | Render |
| Database | Neon (PostgreSQL) |

See [RENDER_DEPLOY.md](./RENDER_DEPLOY.md) and [SUBMISSION.md](./SUBMISSION.md) for full steps.

### Frontend → Vercel

1. Connect the `frontend` folder as a Vercel project
2. Set env: `VITE_API_URL`, `VITE_GOOGLE_CLIENT_ID`, `VITE_STRIPE_PUBLISHABLE_KEY`
3. Add production origin to Google OAuth + backend `FRONTEND_URL` / CORS

### Backend → Render (or AWS EC2 for production)

**Render (used):** Web service, `backend/` root, `uvicorn main:app --host 0.0.0.0 --port $PORT`

**AWS EC2 (production alternative):** EC2 + Nginx + RDS + Stripe webhook endpoint

### Database → Neon / RDS

PostgreSQL via Neon (free) or AWS RDS in production.

## Scaling

See [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) for horizontal scaling, Redis, workers, CDN, etc.

## AI Tools Used During Development

- Cursor
- ChatGPT / Grok (Cursor)

## Submission Documents

- [SUBMISSION.md](./SUBMISSION.md) — Full deliverables, deployment flow, known limitations
- [ONE_PAGE_SYSTEM_DESIGN.md](./ONE_PAGE_SYSTEM_DESIGN.md) — One-page architecture diagram
- [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) — Detailed design + scaling
- [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) — Database schema
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) — API reference

## Known Limitation — Stripe on Live Demo

Real Stripe checkout requires a verified business email for account activation. The live demo uses **mock payment mode** (`STRIPE_MOCK_MODE=auto`). Full payment logic is implemented and testable via mock checkout; real Stripe test mode works locally with configured keys.

## Total Time Taken

~27–35 hours total (both assignments + deployment). See [SUBMISSION.md](./SUBMISSION.md).

## License

Educational assignment project.
