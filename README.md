# BlitzXCreatives Backend

FastAPI + PostgreSQL backend for the BlitzXCreatives Next.js frontend.
Implements Auth (Login/Register), Project Order Submission, and Contact (leads) —
exactly matching the API contracts your frontend already calls.

## Stack

- **FastAPI** (async) + **Uvicorn**
- **PostgreSQL** via **SQLAlchemy 2.0 (async)** + **asyncpg**
- **Alembic** for migrations
- **JWT auth via httpOnly cookies** (access + refresh tokens) — matches `credentials: "include"` in your frontend fetch calls
- **bcrypt** (direct, not passlib — avoids the version-conflict bug) for password hashing
- Honeypot-aware contact/lead endpoint with rate limiting (slowapi)

## Endpoints (match your frontend exactly)

| Method | Path             | Auth required | Frontend page              |
|--------|------------------|----------------|-----------------------------|
| POST   | `/auth/register` | No             | `app/register/page.tsx`     |
| POST   | `/auth/login`    | No             | `app/login/page.tsx`        |
| POST   | `/auth/refresh`  | refresh cookie | (call when access expires)  |
| POST   | `/auth/logout`   | No             | —                            |
| GET    | `/auth/me`       | Yes            | —                            |
| POST   | `/orders`        | Yes            | `app/order/new/page.tsx`    |
| GET    | `/orders`        | Yes            | (future dashboard)          |
| GET    | `/orders/{id}`   | Yes            | `app/order/confirm/page.tsx`|
| POST   | `/leads`         | No             | `app/contact/page.tsx`      |

All responses match what your pages already expect:
- `register`/`login` set httpOnly cookies and return the user object; on failure they return `{detail: "..."}`, which your frontend reads as `data.detail`.
- `POST /orders` returns `{id, service, details, budget, timeline, status, created_at, ...}`; your `order/new` page redirects to `/order/confirm?id=...`.
- `GET /orders/{id}` returns the same shape your `order/confirm` page expects.
- `POST /leads` accepts the honeypot `company` field and silently no-ops bot submissions while still returning 201 (so bots can't detect they were caught).

## Local setup

### 1. With Docker (recommended — zero local Postgres setup)

```bash
cp .env.example .env
# edit .env if needed (defaults work for local dev)
docker compose up --build
```

This starts Postgres + runs migrations + starts the API on `http://localhost:8000`.

### 2. Without Docker

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Make sure DATABASE_URL points to a running Postgres instance

alembic upgrade head               # creates tables
python -m app.seed                  # optional: seeds a demo user/order/lead

uvicorn app.main:app --reload --port 8000
```

### 3. Connect your frontend

In your Next.js project's `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Make sure `FRONTEND_ORIGIN` in the backend's `.env` matches your frontend's URL exactly
(CORS with credentials requires an exact origin match, not `*`).

## Auth flow details

- On register/login, the API sets two httpOnly cookies: `access_token` (short-lived, 15 min default) and `refresh_token` (30 days default).
- Protected routes (`/orders`, `/auth/me`) read `access_token` from the cookie — no `Authorization` header needed, matching your frontend's `credentials: "include"` pattern.
- When the access token expires, call `POST /auth/refresh` (also cookie-based) to get a new pair. You may want to add this as an interceptor on 401 responses in your frontend's fetch wrapper.
- `POST /auth/logout` clears both cookies.

## Security notes

- Passwords hashed with bcrypt (cost factor 12), never stored in plaintext.
- JWTs signed with `JWT_SECRET` — **change this in `.env` for production** to a long random string (e.g. `openssl rand -hex 32`).
- Cookies are `httponly`, `samesite=lax`. Set `COOKIE_SECURE=true` in production (requires HTTPS).
- `/leads` is rate-limited to 5 requests/minute per IP to deter spam/abuse.
- Contact form honeypot (`company` field) is checked server-side; bot submissions return a fake success without touching the database.
- Order ownership is enforced — a user can only fetch their own orders (`403` otherwise).
- Input validation matches your frontend's exact dropdown values for `service`, `budget`, and `timeline` (rejects anything else with a `422`).

## Email notifications

`app/email_utils.py` sends an order-confirmation email to the customer and a lead-notification email internally. By default (no SMTP configured) these are just logged — useful for local dev. To enable real email, set in `.env`:

```
SMTP_HOST=smtp.yourprovider.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
FROM_EMAIL=hello@blitzx.com
```

## Migrations

```bash
# create a new migration after changing models.py
alembic revision --autogenerate -m "describe your change"

# apply migrations
alembic upgrade head
```

## Project structure

```
app/
  main.py          FastAPI app, CORS, exception handlers
  config.py        Settings (env vars)
  database.py      Async SQLAlchemy engine/session
  models.py        User, Order, Lead ORM models
  schemas.py       Pydantic request/response models
  security.py      bcrypt hashing + JWT creation/decoding
  cookies.py       httpOnly cookie helpers
  deps.py          get_current_user dependency (reads cookie)
  email_utils.py   Email sending (logs by default)
  rate_limit.py    slowapi limiter
  seed.py          Demo data seeder
  routers/
    auth.py        register/login/refresh/logout/me
    orders.py      create/list/get orders
    leads.py       contact form submission
alembic/           Migrations
```
