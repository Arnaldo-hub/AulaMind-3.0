"""
===========================================================
AulaMind Enterprise 3.0
routes/admin_comercial.py
-----------------------------------------------------------
Panel Comercial (v3.3)

Visibilidad comercial de la plataforma para el rol admin:

• KPIs: usuarios, trials activos, Plan Pro activos,
  expirados y activaciones del mes.
• Tabla comercial: estado del plan, días restantes,
  uso de trial y origen del alta por usuario.
• Pipeline de pagos: últimos eventos PaymentEvent
  (Mercado Pago + activaciones manuales).
• Activaciones pendientes: usuarios que pagaron en MP
  pero el webhook no activó el plan.

La activación manual de planes reutiliza el endpoint
existente PUT /admin/api/usuarios/<id>/plan
(routes/admin_security.py).

Todas las rutas requieren rol "admin".

Autor:
Biotecno Chile
===========================================================
"""

from datetime import datetime, timedelta

from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

from database.session import SessionLocal
from models.checkout_attempt import CheckoutAttempt
from models.payment_event import PaymentEvent
from models.user import User
from models.user_subscription import UserSubscription
from security.authorization import role_required
from services.entitlements import Entitlements

# ==========================================================
# Blueprint
# ==========================================================

admin_comercial = Blueprint(
    "admin_comercial",
    __name__
)

# ==========================================================
# Constantes
# ==========================================================

EVENTS_LIMIT = 50

VALID_STATUS_FILTERS = ("trial", "active", "expired")

STATUS_LABELS = {
    "trial": "Trial",
    "active": "Plan Pro",
    "expired": "Expirado",
    "cancelled": "Cancelado",
    "admin": "Admin",
    "none": "Sin plan",
}

SOURCE_LABELS = {
    "auto_trial": "Registro web",
    "manual": "Manual",
    "mercadopago": "Mercado Pago",
}


# ==========================================================
# Helpers
# ==========================================================

def _effective_status(user, sub, now):
    """
    Estado comercial real del usuario.

    Admin de la plataforma → "admin".
    Trial o Plan Pro con ends_at vencido → "expired"
    (aunque la fila aún diga trial/active: el portero
    lo expira perezosamente en el próximo acceso).
    """

    if user.role == "admin":
        return "admin"

    if sub is None:
        return "none"

    if sub.status in ("trial", "active"):

        if sub.ends_at and now > sub.ends_at:
            return "expired"

    return sub.status


def _days_left(sub, effective, now):
    """Días restantes (solo trial / Plan Pro vigente)."""

    if effective not in ("trial", "active"):
        return None

    if not sub or not sub.ends_at:
        return None

    delta = sub.ends_at - now

    days = delta.days + (1 if delta.seconds > 0 else 0)

    return max(0, days)


def _serialize_commercial(user, sub, now):
    """Fila de la tabla comercial."""

    effective = _effective_status(user, sub, now)

    return {
        "id": user.id,
        "name": (
            f"{user.first_name or ''} "
            f"{user.last_name or ''}"
        ).strip() or user.email,
        "email": user.email,
        "is_active": bool(user.is_active),
        "created_at": (
            user.created_at.isoformat()
            if user.created_at else None
        ),
        "status": effective,
        "status_label": STATUS_LABELS.get(
            effective, effective
        ),
        "days_left": _days_left(sub, effective, now),
        "ends_at": (
            sub.ends_at.isoformat()
            if sub and sub.ends_at else None
        ),
        "generations_used": (
            sub.generations_used if sub else 0
        ),
        "plan_name": (
            sub.plan.name
            if sub and sub.plan else "—"
        ),
        "source": (
            sub.source if sub else ""
        ),
        "source_label": SOURCE_LABELS.get(
            sub.source if sub else "",
            sub.source if sub else "—"
        ),
    }


def _load_rows(db):
    """Usuarios + suscripciones en 2 consultas."""

    users = db.query(User).order_by(
        User.created_at.desc()
    ).all()

    subs = db.query(UserSubscription).all()

    sub_by_user = {s.user_id: s for s in subs}

    now = datetime.utcnow()

    return [
        _serialize_commercial(
            u, sub_by_user.get(u.id), now
        )
        for u in users
    ], now


def _build_stats(db):
    """KPIs para el template de activaciones."""
    rows, now = _load_rows(db)
    month_start = now.replace(
        day=1, hour=0, minute=0,
        second=0, microsecond=0
    )
    activaciones_mes = db.query(
        PaymentEvent
    ).filter(
        PaymentEvent.action == "activated",
        PaymentEvent.created_at >= month_start,
    ).count()

    teachers = [
        r for r in rows
        if r["status"] != "admin"
    ]

    return {
        "usuarios": len(teachers),
        "trials": sum(
            1 for r in teachers
            if r["status"] == "trial"
        ),
        "pro_activos": sum(
            1 for r in teachers
            if r["status"] == "active"
        ),
        "expirados": sum(
            1 for r in teachers
            if r["status"] == "expired"
        ),
        "activaciones_mes": activaciones_mes,
    }


# ==========================================================
# Página principal
# ==========================================================

@admin_comercial.route("/admin/comercial")
@role_required("admin")
def comercial_page():

    return render_template("admin_comercial.html")


# ==========================================================
# API — KPIs del panel
# ==========================================================

@admin_comercial.route("/admin/api/comercial/resumen")
@role_required("admin")
def resumen():

    db = SessionLocal()

    try:

        rows, now = _load_rows(db)

        month_start = now.replace(
            day=1, hour=0, minute=0,
            second=0, microsecond=0
        )

        activaciones_mes = db.query(
            PaymentEvent
        ).filter(
            PaymentEvent.action == "activated",
            PaymentEvent.created_at >= month_start,
        ).count()

        teachers = [
            r for r in rows
            if r["status"] != "admin"
        ]

        return jsonify(
            success=True,
            kpis={
                "usuarios": len(teachers),
                "trials": sum(
                    1 for r in teachers
                    if r["status"] == "trial"
                ),
                "pro_activos": sum(
                    1 for r in teachers
                    if r["status"] == "active"
                ),
                "expirados": sum(
                    1 for r in teachers
                    if r["status"] == "expired"
                ),
                "activaciones_mes": activaciones_mes,
            },
        )

    finally:

        db.close()


# ==========================================================
# API — Tabla comercial de usuarios
# ==========================================================

@admin_comercial.route("/admin/api/comercial/usuarios")
@role_required("admin")
def usuarios():

    query_text = request.args.get("q", "").strip().lower()

    status_filter = request.args.get(
        "status", ""
    ).strip()

    db = SessionLocal()

    try:

        rows, _now = _load_rows(db)

        if query_text:

            rows = [
                r for r in rows
                if query_text in r["name"].lower()
                or query_text in r["email"].lower()
            ]

        if status_filter in VALID_STATUS_FILTERS:

            rows = [
                r for r in rows
                if r["status"] == status_filter
            ]

        return jsonify(
            success=True,
            total=len(rows),
            items=rows,
        )

    finally:

        db.close()


# ==========================================================
# API — Pipeline de pagos (últimos eventos)
# ==========================================================

@admin_comercial.route("/admin/api/comercial/eventos")
@role_required("admin")
def eventos():

    db = SessionLocal()

    try:

        events = db.query(PaymentEvent).order_by(
            PaymentEvent.created_at.desc()
        ).limit(EVENTS_LIMIT).all()

        user_ids = {
            e.user_id for e in events if e.user_id
        }

        emails = {}

        if user_ids:

            for u in db.query(User).filter(
                User.id.in_(user_ids)
            ).all():

                emails[u.id] = u.email

        return jsonify(
            success=True,
            total=len(events),
            items=[
                {
                    "created_at": (
                        e.created_at.isoformat()
                        if e.created_at else None
                    ),
                    "provider": e.provider,
                    "action": e.action,
                    "detail": e.detail or "",
                    "user_email": emails.get(
                        e.user_id, ""
                    ),
                }
                for e in events
            ],
        )

    finally:

        db.close()


# ==========================================================
# Activaciones pendientes (v3.2)
# ==========================================================

@admin_comercial.route("/admin/comercial/activaciones-pendientes")
@role_required("admin")
def activaciones_pendientes():
    """
    v3.2: Muestra usuarios que iniciaron checkout en MP
    pero cuyo plan no se activó automáticamente.
    """
    db = SessionLocal()
    try:
        desde = datetime.utcnow() - timedelta(hours=48)

        attempts = (
            db.query(CheckoutAttempt)
            .filter(CheckoutAttempt.created_at >= desde)
            .order_by(CheckoutAttempt.created_at.desc())
            .all()
        )

        pendientes = []
        for attempt in attempts:
            user = db.query(User).filter(
                User.id == attempt.user_id
            ).first()

            if not user:
                continue

            status = Entitlements.get_status(user.id)
            if status.get("status") != "active":
                pendientes.append({
                    "user_id": user.id,
                    "email": user.email,
                    "nombre": user.name or "Sin nombre",
                    "checkout_at": attempt.created_at,
                })

        return render_template(
            "admin_comercial.html",
            stats=_build_stats(db),
            tab="activaciones",
            pendientes=pendientes,
        )

    finally:
        db.close()
