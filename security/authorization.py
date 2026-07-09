"""Autorización centralizada de AulaMind."""

from functools import wraps

from flask import abort, redirect, session, url_for

from database.session import SessionLocal
from models.user import User


def _current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None

    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == str(user_id)).first()
    finally:
        db.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = _current_user()
        if user is None or not user.is_active:
            session.clear()
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def role_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = _current_user()
            if user is None or not user.is_active:
                session.clear()
                return redirect(url_for("auth.login"))
            if user.role not in allowed_roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator
