from __future__ import annotations

import os
from datetime import datetime, timedelta

from flask import Flask

from .extensions import db
from .models import Event, Membership, MembershipStatus, RSVP, RSVPStatus, User, UserRole, Venue
from .routes import bp as core_bp


def _database_uri() -> str:
    raw = os.getenv("DATABASE_URL", "sqlite:///dinner_discussions.db")
    if raw.startswith("postgres://"):
        return raw.replace("postgres://", "postgresql://", 1)
    return raw


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTO_SEED_DEMO = _env_flag("AUTO_SEED_DEMO", default=True)


def _seed_sample_data() -> bool:
    """Seed demo records if they are not already present."""
    if User.query.filter_by(email="host@dinnerdiscussions.local").first():
        return False

    host = User(
        first_name="Alex",
        last_name="Rivera",
        email="host@dinnerdiscussions.local",
        role=UserRole.HOST.value,
        city="San Diego",
    )
    admin = User(
        first_name="Jordan",
        last_name="Lee",
        email="admin@dinnerdiscussions.local",
        role=UserRole.SUPER_ADMIN.value,
        city="San Diego",
    )
    member = User(
        first_name="Julian",
        last_name="Barnes",
        email="member@dinnerdiscussions.local",
        role=UserRole.ATTENDEE.value,
        city="San Diego",
    )
    venue = Venue(
        name="Luna Harbor",
        neighborhood="Little Italy",
        city="San Diego",
        contact_name="Taylor Kim",
        notes="Quiet back room holds 24. Confirm headcount 48 hours prior.",
    )
    venue_two = Venue(
        name="Marina Atelier",
        neighborhood="Seaport Village",
        city="San Diego",
        contact_name="Casey Morgan",
        notes="Private mezzanine for 16 guests.",
    )
    event = Event(
        title="Can AI Improve Human Connection?",
        topic_summary="Discuss the social upside and tradeoffs of AI companionship tools.",
        prep_video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        starts_at=datetime.utcnow() + timedelta(days=21),
        capacity=24,
        general_price_cents=2400,
        member_price_cents=1900,
        is_published=True,
        host=host,
        venue=venue,
    )
    event_two = Event(
        title="The Philosophy of Sourdough",
        topic_summary="Explore fermentation, culture, and ethics through food.",
        prep_video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        starts_at=datetime.utcnow() + timedelta(days=12),
        capacity=18,
        general_price_cents=2600,
        member_price_cents=2100,
        is_published=True,
        host=host,
        venue=venue_two,
    )

    db.session.add_all([host, admin, member, venue, venue_two, event, event_two])
    db.session.flush()

    membership = Membership(
        user_id=member.id,
        status=MembershipStatus.ACTIVE.value,
        monthly_price_cents=4500,
        includes_monthly_credit=True,
        discount_percent=20,
        guest_passes_per_quarter=1,
    )
    rsvp = RSVP(
        event_id=event_two.id,
        attendee_id=member.id,
        status=RSVPStatus.CONFIRMED.value,
        used_monthly_credit=True,
        is_guest_pass=False,
        amount_paid_cents=0,
    )

    db.session.add_all([membership, rsvp])
    db.session.commit()
    return True


def _ensure_database_exists() -> None:
    """Create tables if they do not exist so first run does not fail."""
    db.create_all()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(core_bp)

    with app.app_context():
        _ensure_database_exists()
        if app.config.get("AUTO_SEED_DEMO", True):
            _seed_sample_data()

    @app.cli.command("init-db")
    def init_db() -> None:
        """Create database tables (idempotent)."""
        db.create_all()
        print("Database tables created/verified.")

    @app.cli.command("seed-demo")
    def seed_demo() -> None:
        """Insert sample local demo data once."""
        db.create_all()
        inserted = _seed_sample_data()
        if inserted:
            print("Seeded sample records.")
        else:
            print("Sample records already exist; no changes made.")

    return app
