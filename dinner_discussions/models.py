from __future__ import annotations

from datetime import datetime
from enum import Enum

from .extensions import db


class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    OPERATIONS_ADMIN = "operations_admin"
    HOST = "host"
    ATTENDEE = "attendee"


class MembershipStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"


class RSVPStatus(str, Enum):
    CONFIRMED = "confirmed"
    WAITLIST = "waitlist"
    CANCELED = "canceled"
    NO_SHOW = "no_show"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    role = db.Column(db.String(40), nullable=False, default=UserRole.ATTENDEE.value)
    city = db.Column(db.String(120), nullable=False, default="San Diego")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    hosted_events = db.relationship("Event", back_populates="host", lazy=True)


class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    neighborhood = db.Column(db.String(120), nullable=True)
    city = db.Column(db.String(120), nullable=False, default="San Diego")
    contact_name = db.Column(db.String(120), nullable=True)
    contact_email = db.Column(db.String(255), nullable=True)
    contact_phone = db.Column(db.String(32), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    events = db.relationship("Event", back_populates="venue", lazy=True)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    topic_summary = db.Column(db.Text, nullable=False)
    prep_video_url = db.Column(db.String(500), nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=20)
    general_price_cents = db.Column(db.Integer, nullable=False, default=2400)
    member_price_cents = db.Column(db.Integer, nullable=False, default=1900)
    is_published = db.Column(db.Boolean, nullable=False, default=False)

    host_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)

    host = db.relationship("User", back_populates="hosted_events")
    venue = db.relationship("Venue", back_populates="events")
    rsvps = db.relationship("RSVP", back_populates="event", cascade="all, delete-orphan", lazy=True)


class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(40), nullable=False, default=MembershipStatus.ACTIVE.value)
    monthly_price_cents = db.Column(db.Integer, nullable=False, default=2900)
    includes_monthly_credit = db.Column(db.Boolean, nullable=False, default=True)
    discount_percent = db.Column(db.Integer, nullable=False, default=20)
    guest_passes_per_quarter = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    attendee_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False, default=RSVPStatus.CONFIRMED.value)
    used_monthly_credit = db.Column(db.Boolean, nullable=False, default=False)
    is_guest_pass = db.Column(db.Boolean, nullable=False, default=False)
    amount_paid_cents = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    event = db.relationship("Event", back_populates="rsvps")
