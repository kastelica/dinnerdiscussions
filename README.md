# Dinner Discussions (Flask MVP)

A starter Flask application for operating hosted discussion dinners at restaurants.

## What is included

- Event publishing with prep video URL
- Host and venue assignment
- Ticket pricing fields for general/member rates
- Membership and RSVP models with scalable role support
- JSON API endpoints for health and published events
- Seed command for local testing

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask init-db
flask run
```

Then open <http://127.0.0.1:5000>.

## API

- `GET /api/health`
- `GET /api/events`

## Suggested next steps

1. Add auth for attendee/member/admin workflows.
2. Integrate payments (Stripe) for tickets and subscriptions.
3. Add cancellation window enforcement and no-show tracking.
4. Add host payout reporting.
5. Add city and venue performance dashboards for SaaS expansion.
