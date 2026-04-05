from __future__ import annotations

import os
from datetime import datetime
from functools import wraps

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy.exc import OperationalError

from .extensions import db
from .models import Event, Membership, MembershipStatus, RSVP, RSVPStatus, User, UserRole, Venue

bp = Blueprint("core", __name__)


ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@dinnerdiscussions.local")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme-admin")


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("core.admin_login"))
        return view_func(*args, **kwargs)

    return wrapped


def member_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("member_user_id"):
            return redirect(url_for("core.member_sign_in"))
        return view_func(*args, **kwargs)

    return wrapped


@bp.get("/")
def home():
    selected_city = request.args.get("city", "").strip()
    search = request.args.get("q", "").strip()

    try:
        query = Event.query.filter_by(is_published=True)

        if selected_city:
            query = query.join(Venue).filter(Venue.city == selected_city)

        if search:
            like_term = f"%{search}%"
            query = query.filter(
                (Event.title.ilike(like_term)) | (Event.topic_summary.ilike(like_term))
            )

        events = query.order_by(Event.starts_at.asc()).all()
        available_cities = [
            row[0]
            for row in db.session.query(Venue.city)
            .join(Event)
            .filter(Event.is_published.is_(True))
            .distinct()
            .order_by(Venue.city.asc())
            .all()
        ]
    except OperationalError:
        events = []
        available_cities = []

    return render_template(
        "home.html",
        events=events,
        available_cities=available_cities,
        selected_city=selected_city,
        search=search,
    )


@bp.get("/events/<int:event_id>")
def event_detail(event_id: int):
    event = Event.query.get_or_404(event_id)

    if not event.is_published and not session.get("is_admin"):
        return redirect(url_for("core.home"))

    related_events = (
        Event.query.filter(Event.is_published.is_(True), Event.id != event.id)
        .order_by(Event.starts_at.asc())
        .limit(3)
        .all()
    )

    return render_template("event_detail.html", event=event, related_events=related_events)


@bp.get("/account/sign-in")
def member_sign_in():
    members = User.query.filter_by(role=UserRole.ATTENDEE.value).order_by(User.first_name.asc()).all()
    return render_template("member_sign_in.html", members=members)


@bp.post("/account/sign-in")
def member_sign_in_post():
    member_id = int(request.form.get("member_id", "0"))
    member = User.query.filter_by(id=member_id, role=UserRole.ATTENDEE.value).first()
    if not member:
        flash("Member not found.", "error")
        return redirect(url_for("core.member_sign_in"))

    session["member_user_id"] = member.id
    return redirect(url_for("core.member_dashboard"))


@bp.post("/account/sign-out")
def member_sign_out():
    session.pop("member_user_id", None)
    return redirect(url_for("core.home"))


@bp.get("/account")
@member_required
def member_dashboard():
    member = User.query.get_or_404(session["member_user_id"])
    membership = (
        Membership.query.filter_by(user_id=member.id)
        .order_by(Membership.created_at.desc())
        .first()
    )

    current_rsvps = (
        db.session.query(RSVP, Event, Venue, User)
        .join(Event, RSVP.event_id == Event.id)
        .join(Venue, Event.venue_id == Venue.id)
        .join(User, Event.host_id == User.id)
        .filter(RSVP.attendee_id == member.id, RSVP.status == RSVPStatus.CONFIRMED.value)
        .order_by(Event.starts_at.asc())
        .all()
    )

    past_dinners = (
        db.session.query(RSVP, Event, Venue)
        .join(Event, RSVP.event_id == Event.id)
        .join(Venue, Event.venue_id == Venue.id)
        .filter(RSVP.attendee_id == member.id, Event.starts_at < datetime.utcnow())
        .order_by(Event.starts_at.desc())
        .limit(6)
        .all()
    )

    return render_template(
        "account_dashboard.html",
        member=member,
        membership=membership,
        current_rsvps=current_rsvps,
        past_dinners=past_dinners,
    )


@bp.post("/account/membership/toggle")
@member_required
def membership_toggle():
    member_id = session["member_user_id"]
    membership = Membership.query.filter_by(user_id=member_id).order_by(Membership.created_at.desc()).first()

    if membership and membership.status == MembershipStatus.ACTIVE.value:
        membership.status = MembershipStatus.CANCELED.value
        flash("Membership paused.", "success")
    elif membership:
        membership.status = MembershipStatus.ACTIVE.value
        flash("Membership reactivated.", "success")
    else:
        membership = Membership(
            user_id=member_id,
            status=MembershipStatus.ACTIVE.value,
            monthly_price_cents=4500,
            includes_monthly_credit=True,
            discount_percent=20,
            guest_passes_per_quarter=1,
        )
        db.session.add(membership)
        flash("Membership started.", "success")

    db.session.commit()
    return redirect(url_for("core.member_dashboard"))


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


@bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if email == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            session["admin_email"] = email
            return redirect(url_for("core.admin_dashboard"))

        flash("Invalid admin credentials.", "error")

    return render_template("admin_login.html", default_email=ADMIN_EMAIL)


@bp.post("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("core.home"))


@bp.get("/admin")
@admin_required
def admin_dashboard():
    hosts = User.query.filter(
        User.role.in_([UserRole.HOST.value, UserRole.SUPER_ADMIN.value])
    ).order_by(User.first_name.asc()).all()
    venues = Venue.query.order_by(Venue.name.asc()).all()
    events = Event.query.order_by(Event.starts_at.desc()).all()
    return render_template("admin_dashboard.html", hosts=hosts, venues=venues, events=events)


@bp.post("/admin/venues")
@admin_required
def create_venue():
    venue = Venue(
        name=request.form["name"].strip(),
        neighborhood=request.form.get("neighborhood", "").strip() or None,
        city=request.form.get("city", "San Diego").strip() or "San Diego",
        contact_name=request.form.get("contact_name", "").strip() or None,
        contact_email=request.form.get("contact_email", "").strip() or None,
        contact_phone=request.form.get("contact_phone", "").strip() or None,
        notes=request.form.get("notes", "").strip() or None,
    )
    db.session.add(venue)
    db.session.commit()
    flash("Venue added.", "success")
    return redirect(url_for("core.admin_dashboard"))


@bp.post("/admin/events")
@admin_required
def create_event():
    starts_at_raw = request.form.get("starts_at", "")
    starts_at = datetime.strptime(starts_at_raw, "%Y-%m-%dT%H:%M")

    event = Event(
        title=request.form["title"].strip(),
        topic_summary=request.form["topic_summary"].strip(),
        prep_video_url=request.form["prep_video_url"].strip(),
        starts_at=starts_at,
        capacity=int(request.form.get("capacity", 20)),
        general_price_cents=int(float(request.form.get("general_price", 24)) * 100),
        member_price_cents=int(float(request.form.get("member_price", 19)) * 100),
        is_published=bool(request.form.get("is_published")),
        host_id=int(request.form["host_id"]),
        venue_id=int(request.form["venue_id"]),
    )

    db.session.add(event)
    db.session.commit()
    flash("Event created.", "success")
    return redirect(url_for("core.admin_dashboard"))


@bp.post("/admin/events/<int:event_id>/toggle-publish")
@admin_required
def toggle_event_publish(event_id: int):
    event = Event.query.get_or_404(event_id)
    event.is_published = not event.is_published
    db.session.commit()
    flash("Event publish status updated.", "success")
    return redirect(url_for("core.admin_dashboard"))
