"""
===========================================================
AulaMind Enterprise 3.0
routes/admin_security.py
-----------------------------------------------------------
Módulo M-09: Administración de Usuarios

• Listado con búsqueda y filtros
• Crear usuario
• Editar usuario (datos, rol, contraseña opcional)
• Activar / desactivar
• Eliminación lógica (desactivación)

Todas las rutas requieren rol "admin".

Autor:
Biotecno Chile
===========================================================
"""

import re

from flask import Blueprint
from flask import render_template
from flask import request
from flask import jsonify
from flask import session

from database.session import SessionLocal
from models.user import User
from services.auth_service import AuthService
from security.authorization import role_required

# ==========================================================
# Blueprint
# ==========================================================

admin_security = Blueprint(
    "admin_security",
    __name__
)

# ==========================================================
# Constantes
# ==========================================================

VALID_ROLES = ("teacher", "admin")

ROLE_LABELS = {
    "teacher": "Docente",
    "admin": "Administrador",
}

EMAIL_RE = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


# ==========================================================
# Helpers
# ==========================================================

def _serialize_user(user):

    data = user.to_dict()

    data["role_label"] = ROLE_LABELS.get(

        user.role,

        user.role

    )

    data["last_login"] = (

        user.last_login.isoformat()

        if user.last_login else None

    )

    return data


def _error(message, status=400):

    return jsonify(

        success=False,

        error=message

    ), status


# ==========================================================
# Verificación de seguridad (existente)
# ==========================================================

@admin_security.route("/admin/security-check")
@role_required("admin")
def security_check():
    return jsonify({"status": "ok", "role": "admin"}), 200


# ==========================================================
# Página principal del módulo
# ==========================================================

@admin_security.route("/admin/usuarios")
@role_required("admin")
def users_page():

    return render_template(

        "admin_users.html",

        roles=ROLE_LABELS

    )


# ==========================================================
# API — Listar usuarios
# ==========================================================

@admin_security.route("/admin/api/usuarios")
@role_required("admin")
def list_users():

    query_text = request.args.get("q", "").strip()

    role = request.args.get("role", "").strip()

    status = request.args.get("status", "").strip()

    db = SessionLocal()

    try:

        query = db.query(User)

        if query_text:

            like = f"%{query_text}%"

            query = query.filter(

                (User.first_name.ilike(like))

                | (User.last_name.ilike(like))

                | (User.email.ilike(like))

            )

        if role in VALID_ROLES:

            query = query.filter(User.role == role)

        if status == "active":

            query = query.filter(User.is_active.is_(True))

        elif status == "inactive":

            query = query.filter(User.is_active.is_(False))

        users = query.order_by(

            User.created_at.desc()

        ).all()

        return jsonify(

            success=True,

            total=len(users),

            items=[_serialize_user(u) for u in users]

        )

    finally:

        db.close()


# ==========================================================
# API — Obtener un usuario
# ==========================================================

@admin_security.route("/admin/api/usuarios/<user_id>")
@role_required("admin")
def get_user(user_id):

    db = SessionLocal()

    try:

        user = db.query(User).filter(

            User.id == user_id

        ).first()

        if user is None:

            return _error(

                "Usuario no encontrado.",

                404

            )

        return jsonify(

            success=True,

            user=_serialize_user(user)

        )

    finally:

        db.close()


# ==========================================================
# API — Crear usuario
# ==========================================================

@admin_security.route(
    "/admin/api/usuarios",
    methods=["POST"]
)
@role_required("admin")
def create_user():

    payload = request.get_json(silent=True) or {}

    first_name = (

        payload.get("first_name") or ""

    ).strip()

    last_name = (

        payload.get("last_name") or ""

    ).strip()

    email = (

        payload.get("email") or ""

    ).strip().lower()

    phone = (

        payload.get("phone") or ""

    ).strip() or None

    role = (

        payload.get("role") or "teacher"

    ).strip()

    password = payload.get("password") or ""

    # ------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------

    if not first_name or not last_name:

        return _error(

            "Nombre y apellido son obligatorios."

        )

    if not EMAIL_RE.match(email):

        return _error(

            "El correo electrónico no es válido."

        )

    if role not in VALID_ROLES:

        return _error(

            "El rol seleccionado no es válido."

        )

    db = SessionLocal()

    try:

        if AuthService.get_user_by_email(db, email):

            return _error(

                "El correo ya está registrado.",

                409

            )

        try:

            AuthService.validate_password(password)

        except ValueError as ex:

            return _error(str(ex))

        user = User(

            first_name=first_name,

            last_name=last_name,

            email=email,

            phone=phone,

            role=role,

            is_admin=(role == "admin"),

            is_active=True,

            password_hash=(

                AuthService.hash_password(password)

            ),

        )

        db.add(user)

        db.commit()

        db.refresh(user)

        return jsonify(

            success=True,

            user=_serialize_user(user)

        ), 201

    finally:

        db.close()


# ==========================================================
# API — Actualizar usuario
# ==========================================================

@admin_security.route(
    "/admin/api/usuarios/<user_id>",
    methods=["PUT"]
)
@role_required("admin")
def update_user(user_id):

    payload = request.get_json(silent=True) or {}

    db = SessionLocal()

    try:

        user = db.query(User).filter(

            User.id == user_id

        ).first()

        if user is None:

            return _error(

                "Usuario no encontrado.",

                404

            )

        first_name = (

            payload.get("first_name") or ""

        ).strip()

        last_name = (

            payload.get("last_name") or ""

        ).strip()

        email = (

            payload.get("email") or ""

        ).strip().lower()

        phone = (

            payload.get("phone") or ""

        ).strip() or None

        role = (

            payload.get("role") or user.role

        ).strip()

        new_password = (

            payload.get("password") or ""

        )

        # --------------------------------------------------
        # Validaciones
        # --------------------------------------------------

        if not first_name or not last_name:

            return _error(

                "Nombre y apellido "

                "son obligatorios."

            )

        if not EMAIL_RE.match(email):

            return _error(

                "El correo electrónico "

                "no es válido."

            )

        if role not in VALID_ROLES:

            return _error(

                "El rol seleccionado "

                "no es válido."

            )

        existing = AuthService.get_user_by_email(

            db,

            email

        )

        if existing and existing.id != user.id:

            return _error(

                "El correo ya está registrado "

                "por otro usuario.",

                409

            )

        # --------------------------------------------------
        # Protección: no quitarse el propio rol admin
        # --------------------------------------------------

        if (

            str(user.id) == str(session.get("user_id"))

            and role != "admin"

        ):

            return _error(

                "No puedes quitarte tu propio "

                "rol de administrador."

            )

        user.first_name = first_name

        user.last_name = last_name

        user.email = email

        user.phone = phone

        user.role = role

        user.is_admin = (role == "admin")

        # --------------------------------------------------
        # Contraseña opcional
        # --------------------------------------------------

        if new_password:

            try:

                AuthService.validate_password(

                    new_password

                )

            except ValueError as ex:

                return _error(str(ex))

            user.password_hash = (

                AuthService.hash_password(

                    new_password

                )

            )

        db.commit()

        db.refresh(user)

        return jsonify(

            success=True,

            user=_serialize_user(user)

        )

    finally:

        db.close()


# ==========================================================
# API — Alternar activo / inactivo
# ==========================================================

@admin_security.route(
    "/admin/api/usuarios/<user_id>/toggle",
    methods=["PATCH"]
)
@role_required("admin")
def toggle_user(user_id):

    db = SessionLocal()

    try:

        user = db.query(User).filter(

            User.id == user_id

        ).first()

        if user is None:

            return _error(

                "Usuario no encontrado.",

                404

            )

        if str(user.id) == str(

            session.get("user_id")

        ):

            return _error(

                "No puedes desactivar "

                "tu propia cuenta."

            )

        if user.is_active:

            AuthService.deactivate_user(db, user)

        else:

            AuthService.activate_user(db, user)

        return jsonify(

            success=True,

            user=_serialize_user(user)

        )

    finally:

        db.close()


# ==========================================================
# API — Eliminar (desactivación lógica)
# ==========================================================

@admin_security.route(
    "/admin/api/usuarios/<user_id>",
    methods=["DELETE"]
)
@role_required("admin")
def delete_user(user_id):

    db = SessionLocal()

    try:

        user = db.query(User).filter(

            User.id == user_id

        ).first()

        if user is None:

            return _error(

                "Usuario no encontrado.",

                404

            )

        if str(user.id) == str(

            session.get("user_id")

        ):

            return _error(

                "No puedes eliminar "

                "tu propia cuenta."

            )

        AuthService.deactivate_user(db, user)

        return jsonify(

            success=True,

            message=(

                "Usuario desactivado "

                "correctamente."

            )

        )

    finally:

        db.close()
