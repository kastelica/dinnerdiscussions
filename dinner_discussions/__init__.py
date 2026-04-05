from __future__ import annotations

import os
from datetime import datetime, timedelta

from flask import Flask

from .extensions import db
from .models import Event, User, UserRole, Venue
from .routes import bp as core_bp


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dinner_discussions.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(core_bp)

    @app.cli.command("init-db")
    def init_db() -> None:
        """Create tables and seed sample data."""
        db.drop_all()
        db.create_all()

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
        venue = Venue(
            name="Luna Harbor",
            neighborhood="Little Italy",
            city="San Diego",
            contact_name="Taylor Kim",
            notes="Quiet back room holds 24. Confirm headcount 48 hours prior.",
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

        db.session.add_all([host, admin, venue, event])
        db.session.commit()
        print("Initialized database with seed data.")

    return app
