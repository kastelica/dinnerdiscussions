# Dinner Discussions (Flask MVP)

A starter Flask application for operating hosted discussion dinners at restaurants.

## What is included

- Event publishing with prep video URL
- Host and venue assignment
- Ticket pricing fields for general/member rates
- Membership and RSVP models with scalable role support
- JSON API endpoints for health and published events
- Auto database create + auto demo seed by default
- Admin backend for creating venues/events and toggling publish status
- Render-ready web service process config (`Procfile`)

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ADMIN_EMAIL=admin@dinnerdiscussions.local
export ADMIN_PASSWORD='changeme-admin'
flask --app app.py run --port 5001
```


Then open:

- Public site: <http://127.0.0.1:5001>
- Member sign-in: <http://127.0.0.1:5001/account/sign-in>
- Admin login: <http://127.0.0.1:5001/admin/login>

On first startup, tables are created and sample records are seeded automatically.

## Admin backend access

By default, login credentials come from environment variables:

- `ADMIN_EMAIL` (default: `admin@dinnerdiscussions.local`)
- `ADMIN_PASSWORD` (default: `changeme-admin`)

After logging in, use `/admin` to:

- add venues
- create events
- toggle event publish/draft status

## Optional CLI bootstrap commands

```bash
flask --app app.py init-db
flask --app app.py seed-demo
```

These commands are idempotent.

## Deploy on Render (Web Service — trial-friendly)

1. Push this repo to GitHub.
2. In Render, choose **New +** → **Web Service**.
3. Connect your repo and set:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Add environment variables:
   - `SECRET_KEY` = any long random value
   - `DATABASE_URL` = your Render Postgres URL (recommended)
   - `ADMIN_EMAIL` = your login email
   - `ADMIN_PASSWORD` = your login password
   - `AUTO_SEED_DEMO` = `true` (default; set to `false` if you do not want demo records)
5. Deploy.

## API

- `GET /api/health`
- `GET /api/events`

## Suggested next steps

1. Add proper user auth and role-based permissions per-user.
2. Integrate payments (Stripe) for tickets and subscriptions.
3. Add cancellation window enforcement and no-show tracking.
4. Add host payout reporting.
5. Add city and venue performance dashboards for SaaS expansion.

## Member account dashboard

- Visit `/account/sign-in` and choose a demo attendee profile.
- Dashboard shows membership status, upcoming RSVPs, and past dinners.
- Use the membership toggle button to start/pause membership in-app.
