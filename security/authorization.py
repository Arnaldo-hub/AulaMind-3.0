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


def subscription_required(view):
    """
    Portero comercial: exige suscripción vigente
    (trial activo o plan pagado) antes de generar con IA.
    Responde 402 con motivo para el paywall si no puede.
    """
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            session.clear()
            return redirect(url_for("auth.login"))

        from flask import jsonify
        from services.entitlements import Entitlements

        result = Entitlements.check_generation(user_id)

        if not result.get("allowed"):
            return jsonify({
                "success": False,
                "error": result.get(
                    "message", "Suscripción requerida."
                ),
                "paywall": True,
                "reason": result.get("reason"),
                "plan_url": "/plan",
            }), 402

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
