# Dinner Discussions (Flask MVP)

A starter Flask application for operating hosted discussion dinners at restaurants.

## What is included

- Event publishing with prep video URL
- Host and venue assignment
- Ticket pricing fields for general/member rates
- Membership and RSVP models with scalable role support
- JSON API endpoints for health and published events
- Idempotent DB bootstrap + optional demo seed command
- Render-ready process and service configuration (`Procfile` + `render.yaml`)

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask init-db
flask seed-demo
flask run --port 5001
```

Then open <http://127.0.0.1:5001>.

For production-like local execution:

```bash
gunicorn app:app
```

## Fix for `sqlite3.OperationalError: no such table: event`

If you cloned fresh and see this error, run:

```bash
flask --app app.py init-db
flask --app app.py seed-demo
```

This app now also auto-runs `db.create_all()` at startup to prevent first-load table errors.

## Deploy on Render

This repo includes both a `Procfile` and `render.yaml`.

### Option A: Blueprint deploy (recommended)

1. Push this repo to GitHub.
2. In Render, choose **New +** → **Blueprint**.
3. Select this repository.
4. Render will apply settings from `render.yaml`:
   - build: `pip install -r requirements.txt`
   - start: `gunicorn app:app`
5. After first deploy, open a shell and run:

```bash
flask --app app.py init-db
flask --app app.py seed-demo
```

### Option B: Manual Web Service

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Environment variables:
  - `SECRET_KEY` (random long value)
  - `DATABASE_URL` (replace sqlite with managed Postgres for production)

## API

- `GET /api/health`
- `GET /api/events`

## Suggested next steps

1. Add auth for attendee/member/admin workflows.
2. Integrate payments (Stripe) for tickets and subscriptions.
3. Add cancellation window enforcement and no-show tracking.
4. Add host payout reporting.
5. Add city and venue performance dashboards for SaaS expansion.
