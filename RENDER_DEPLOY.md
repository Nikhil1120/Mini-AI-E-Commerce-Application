# Deploy Backend on Render (Free)

## Fix for Python 3.14 build errors

Render defaults to Python 3.14, which breaks older pinned packages (`pydantic-core` Rust build).

This repo includes `backend/runtime.txt` pinning **Python 3.11.11**. Push to GitHub and redeploy.

Alternatively in Render → **Environment** → add:

```
PYTHON_VERSION=3.11.11
```

## Render service settings

| Setting | Value |
|---------|--------|
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

## Minimum environment variables

These four are enough to start (you already have them):

| Variable | Example |
|----------|---------|
| `DATABASE_URL` | Neon Postgres URL with `?sslmode=require` |
| `FRONTEND_URL` | `https://your-app.vercel.app` |
| `GOOGLE_CLIENT_ID` | Google OAuth Web client ID |
| `ADMIN_EMAIL` | your@gmail.com |

## Recommended extra variables (no Stripe/Gemini account required)

| Variable | Value | Why |
|----------|--------|-----|
| `JWT_SECRET_KEY` | long random string | secure sessions |
| `DEV_MODE` | `true` | demo login on `/login` without full OAuth setup |
| `STRIPE_MOCK_MODE` | `auto` | mock checkout without Stripe keys |
| `AI_PROVIDER` | `gemini` | optional; works without API key (tool fallback) |

You do **not** need `GOOGLE_CLIENT_SECRET` for frontend Google Sign-In (ID token flow).

## After first deploy

Open Render **Shell** and run:

```bash
python seed.py
```

Test:

- `https://YOUR-SERVICE.onrender.com/health`
- `https://YOUR-SERVICE.onrender.com/docs`
