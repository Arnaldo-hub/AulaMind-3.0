"""Ruta administrativa mínima para validar autorización."""

from flask import Blueprint, jsonify

from security.authorization import role_required

admin_security = Blueprint("admin_security", __name__)


@admin_security.route("/admin/security-check")
@role_required("admin")
def security_check():
    return jsonify({"status": "ok", "role": "admin"}), 200
