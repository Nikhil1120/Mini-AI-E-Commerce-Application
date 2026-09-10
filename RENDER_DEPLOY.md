# Deploy Backend on Render (Free)

## Fix for Python 3.14 build errors

Render may use Python 3.14, which breaks old `pydantic==2.5.0` (Rust compile fails).

This repo fixes that in two ways:

1. **`requirements.txt` updated** — newer packages use pre-built wheels (no Rust build).
2. **Python pinned to 3.11** via `runtime.txt` (repo root + `backend/`) and `backend/.python-version`.

After pulling latest code, redeploy on Render.

### Force Python 3.11 on Render (dashboard)

1. Open your Web Service on Render
2. Click **Environment** in the left sidebar
3. Click **+ Add Environment Variable**
4. Key: `PYTHON_VERSION` → Value: `3.11.11`
5. Click **Save Changes** (triggers redeploy)

If you only see "Deploy latest commit" without env vars, you are on the **Events/Deploy** tab — switch to **Environment** tab first.

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
