from __future__ import annotations

from flask import Blueprint, jsonify, render_template
from sqlalchemy.exc import OperationalError

from .models import Event

bp = Blueprint("core", __name__)


@bp.get("/")
def home():
    try:
        upcoming_events = (
            Event.query.filter_by(is_published=True)
            .order_by(Event.starts_at.asc())
            .limit(8)
            .all()
        )
    except OperationalError:
        upcoming_events = []
    return render_template("home.html", events=upcoming_events)


@bp.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "dinner-discussions"})


@bp.get("/api/events")
def list_events():
    try:
        events = Event.query.filter_by(is_published=True).order_by(Event.starts_at.asc()).all()
    except OperationalError:
        return jsonify([])

    payload = [
        {
            "id": event.id,
            "title": event.title,
            "topic_summary": event.topic_summary,
            "prep_video_url": event.prep_video_url,
            "starts_at": event.starts_at.isoformat(),
            "capacity": event.capacity,
            "general_price_cents": event.general_price_cents,
            "member_price_cents": event.member_price_cents,
            "host": f"{event.host.first_name} {event.host.last_name}",
            "venue": event.venue.name,
            "city": event.venue.city,
        }
        for event in events
    ]
    return jsonify(payload)
