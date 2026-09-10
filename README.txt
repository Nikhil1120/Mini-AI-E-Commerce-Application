================================================================================
MINI AI E-COMMERCE APPLICATION — README & SETUP INSTRUCTIONS
================================================================================

Production-style mini e-commerce app demonstrating:

  Frontend UI -> FastAPI -> Auth -> RBAC -> Database -> Business Logic
  -> Stripe -> Webhooks -> AI Agent


FEATURES
--------------------------------------------------------------------------------

Customer:
  - Google Sign-In / Logout
  - Product listing, search, details, stock
  - Cart (add / update / remove / clear)
  - Checkout with Stripe test mode (or mock mode)
  - Order history and details
  - AI support chatbot (real DB-backed tools)

Admin:
  - Admin dashboard stats
  - Product CRUD + stock updates
  - View all orders / update status
  - Backend-enforced RBAC (role never trusted from frontend)


TECH STACK
--------------------------------------------------------------------------------

Layer      | Stack
-----------|------------------------------------------------------------------
Frontend   | React, Vite, Tailwind CSS, React Router, Axios, Zustand, Lucide
Backend    | Python, FastAPI, SQLAlchemy, Pydantic
Database   | PostgreSQL (prod) / SQLite (local)
Auth       | Google OAuth + JWT
Payments   | Stripe Checkout + webhooks
AI         | LangChain + Gemini/OpenAI with tool calling (fallback router)


PROJECT STRUCTURE
--------------------------------------------------------------------------------

assignment2/
  backend/
    main.py, config.py, database.py, models.py, schemas.py
    dependencies.py, seed.py, requirements.txt, .env.example
    routers/     (auth, products, cart, orders, payments, admin, ai)
    services/    (google_auth, stripe_service, ai_service)
    ai/          (agent + tools)
    tests/
  frontend/
    src/components, src/pages, src/context, src/services
    .env.example
  README.md, API_DOCUMENTATION.md, DATABASE_SCHEMA.md, SYSTEM_DESIGN.md


PREREQUISITES
--------------------------------------------------------------------------------

  - Python 3.10+
  - Node.js 18+
  - PostgreSQL (optional; SQLite works locally)
  - Google Cloud OAuth Client ID (Web application)
  - Stripe account (test mode) — optional; mock mode works without Stripe
  - Gemini and/or OpenAI API key (optional — tool router works without LLM)


BACKEND SETUP
--------------------------------------------------------------------------------

  cd backend
  python -m venv venv

  Windows:
    venv\Scripts\activate

  macOS/Linux:
    source venv/bin/activate

  pip install -r requirements.txt
  copy .env.example .env        (Windows)
  cp .env.example .env            (macOS/Linux)
  (then edit .env with your values)

  python seed.py
  uvicorn main:app --reload --port 8000

  API:     http://localhost:8000
  Swagger: http://localhost:8000/docs

Promote an admin (after signing in once with Google):

  python seed.py --promote-admin your-google-email@gmail.com

Or set ADMIN_EMAIL to that Google email before first login.


FRONTEND SETUP
--------------------------------------------------------------------------------

  cd frontend
  npm install
  copy .env.example .env.local    (Windows)
  cp .env.example .env.local      (macOS/Linux)

  Set in .env.local:
    VITE_GOOGLE_CLIENT_ID=your-google-client-id
    VITE_API_URL=http://localhost:8000

  npm run dev

  App: http://localhost:5173


GOOGLE OAUTH SETUP
--------------------------------------------------------------------------------

1. Open Google Cloud Console: https://console.cloud.google.com/
2. Create a project -> APIs & Services -> Credentials
3. Create OAuth client ID -> Application type: Web application
4. Authorized JavaScript origins: http://localhost:5173
5. Authorized redirect URIs: http://localhost:5173 (and production URL when deploying)
6. Copy Client ID into:
     backend/.env          -> GOOGLE_CLIENT_ID
     frontend/.env.local   -> VITE_GOOGLE_CLIENT_ID

The backend verifies the Google ID token. New users are always CUSTOMER unless
their email matches ADMIN_EMAIL.


STRIPE SETUP
--------------------------------------------------------------------------------

Demo mode (dummy keys — no Stripe account needed)
  The app ships with placeholder Stripe keys in .env / .env.example.
  When dummy keys are detected (STRIPE_MOCK_MODE=auto), checkout uses a
  simulated Stripe page at /checkout/mock with:
    - Pay Successfully   -> backend confirms payment
    - Simulate Failed    -> payment_status=FAILED
    - Cancel Payment     -> payment_status=CANCELLED

Real Stripe test mode
1. Create a Stripe account and enable test mode
2. Copy Secret + Publishable keys into backend/frontend env files
3. Set STRIPE_MOCK_MODE=false in backend/.env
4. For local webhooks install Stripe CLI:
     stripe login
     stripe listen --forward-to localhost:8000/payments/webhook
5. Put the CLI webhook signing secret into STRIPE_WEBHOOK_SECRET

Payment business rules:
  - Order + OrderItems created with PENDING payment/status
  - Stock is NOT reduced at order creation
  - Only checkout.session.completed webhook sets PAID / CONFIRMED,
    reduces stock, clears cart
  - Frontend success redirect alone never marks payment paid
  - Failed payment -> FAILED (no stock change)
  - Expired/cancelled session -> CANCELLED (no stock change)

Test card: 4242 4242 4242 4242, any future expiry, any CVC.


AI SETUP
--------------------------------------------------------------------------------

In backend/.env:

  AI_PROVIDER=gemini          (or openai, or leave keys empty for fallback)
  GEMINI_API_KEY=...
  OPENAI_API_KEY=...

Tools (always use authenticated user from JWT):
  - get_product_by_name / search_products / get_product_stock
  - get_my_orders / get_order_status


DATABASE
--------------------------------------------------------------------------------

SQLite (default local):

  DATABASE_URL=sqlite:///./ecommerce.db

PostgreSQL:

  DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce

Tables are created on startup via Base.metadata.create_all.
Run python seed.py for sample products.


TESTING
--------------------------------------------------------------------------------

  cd backend
  pytest -q


LIVE DEMO URLS
--------------------------------------------------------------------------------

Frontend:    https://mini-ai-e-commerce-application-bnmpf5vmx.vercel.app
Backend API: https://mini-ai-e-commerce-application-x1eg.onrender.com
Swagger:     https://mini-ai-e-commerce-application-x1eg.onrender.com/docs
GitHub:      https://github.com/Nikhil1120/Mini-AI-E-Commerce-Application


DEPLOYMENT (FREE TIER — USED)
--------------------------------------------------------------------------------

Layer      | Platform
-----------|----------
Frontend   | Vercel
Backend    | Render
Database   | Neon (PostgreSQL)

Frontend -> Vercel:
  1. Connect the frontend folder as a Vercel project
  2. Set env: VITE_API_URL, VITE_GOOGLE_CLIENT_ID, VITE_STRIPE_PUBLISHABLE_KEY
  3. Add production origin to Google OAuth + backend FRONTEND_URL / CORS

Backend -> Render:
  - Web service, backend/ root directory
  - Start: uvicorn main:app --host 0.0.0.0 --port $PORT
  - Set: DATABASE_URL, FRONTEND_URL, GOOGLE_CLIENT_ID, ADMIN_EMAIL,
         JWT_SECRET_KEY, DEV_MODE=true, STRIPE_MOCK_MODE=auto

Database -> Neon:
  - Create PostgreSQL project on neon.tech
  - Copy connection string to DATABASE_URL on Render

See RENDER_DEPLOY.md and SUBMISSION.txt for full deployment steps.


KNOWN LIMITATION — STRIPE ON LIVE DEMO
--------------------------------------------------------------------------------

Real Stripe checkout requires a verified business email for account activation.
The live demo uses mock payment mode (STRIPE_MOCK_MODE=auto). Full payment logic
is implemented and testable via mock checkout; real Stripe test mode works
locally with configured keys.


DEMO / ADMIN CREDENTIALS
--------------------------------------------------------------------------------

There are no passwords. Auth is Google OAuth only.
Seed creates/promotes admin via ADMIN_EMAIL or --promote-admin.
Never commit real .env secrets.


TOTAL TIME TAKEN
--------------------------------------------------------------------------------

~27-35 hours total (both assignments + deployment). See SUBMISSION.txt.


AI TOOLS USED DURING DEVELOPMENT
--------------------------------------------------------------------------------

  - Cursor IDE / Cursor AI Agent
  - ChatGPT / Claude
  - Figma (Assignment 1 design reference)

================================================================================
