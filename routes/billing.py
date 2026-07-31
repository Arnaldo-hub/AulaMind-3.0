"""
===========================================================
AulaMind Enterprise 3.0
routes/billing.py
-----------------------------------------------------------

Estado de plan del usuario (v3.1)

• GET /plan → panel "Mi Plan" (trial / activo / expirado)

Autor:
Biotecno Chile
===========================================================
"""

from datetime import datetime

from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for

from services.entitlements import Entitlements

# ==========================================================
# Blueprint
# ==========================================================

billing = Blueprint(
    "billing",
    __name__,
    url_prefix="/plan"
)


# ==========================================================
# Mi Plan
# ==========================================================

@billing.route("/", methods=["GET"])
def status():

    # El guardia global ya exige sesión; doble chequeo defensivo
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth.login"))

    plan = Entitlements.get_status(user_id)

    # Días restantes (la plantilla no calcula fechas)
    days_left = None
    ends_at = plan.get("ends_at")

    if ends_at:
        delta = ends_at - datetime.utcnow()
        days_left = max(0, delta.days)

    return render_template(
        "plan_status.html",
        plan=plan,
        days_left=days_left
    )
