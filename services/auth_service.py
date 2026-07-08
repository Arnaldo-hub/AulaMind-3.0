"""
===========================================================
AulaMind Enterprise 3.0
services/auth_service.py
-----------------------------------------------------------

Servicio de autenticación.

Responsabilidades

✓ Registrar usuario

✓ Iniciar sesión

✓ Buscar usuario

✓ Validar contraseña

✓ Hash de contraseña

===========================================================
"""

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from models.user import User


class AuthService:

    """
    Servicio de autenticación.
    """

    # =====================================================
    # Hash Password
    # =====================================================

    @staticmethod
    def hash_password(password: str) -> str:

        return generate_password_hash(password)

    # =====================================================
    # Verificar Password
    # =====================================================

    @staticmethod
    def verify_password(

        password: str,

        password_hash: str

    ) -> bool:

        return check_password_hash(

            password_hash,

            password

        )

    # =====================================================
    # Buscar Usuario
    # =====================================================

    @staticmethod
    def get_user_by_email(

        db,

        email: str

    ):

        return (

            db.query(User)

            .filter(

                User.email == email

            )

            .first()

        )

    # =====================================================
    # Registrar Usuario
    # =====================================================

    @staticmethod
    def register_user(

        db,

        first_name,

        last_name,

        email,

        password

    ):

        existe = AuthService.get_user_by_email(

            db,

            email

        )

        if existe:

            raise ValueError(

                "El correo ya está registrado."

            )

        usuario = User(

            first_name=first_name,

            last_name=last_name,

            email=email,

            password_hash=AuthService.hash_password(

                password

            )

        )

        db.add(usuario)

        db.commit()

        db.refresh(usuario)

        return usuario

    # =====================================================
    # Login
    # =====================================================

    @staticmethod
    def login(

        db,

        email,

        password

    ):

        usuario = AuthService.get_user_by_email(

            db,

            email

        )

        if usuario is None:

            return None

        if not AuthService.verify_password(

            password,

            usuario.password_hash

        ):

            return None

        return usuario

    # =====================================================
    # Cambiar Password
    # =====================================================

    @staticmethod
    def change_password(

        db,

        user,

        new_password

    ):

        user.password_hash = AuthService.hash_password(

            new_password

        )

        db.commit()

        db.refresh(user)

        return user

    # =====================================================
    # Activar Usuario
    # =====================================================

    @staticmethod
    def activate_user(

        db,

        user

    ):

        user.is_active = True

        db.commit()

        db.refresh(user)

        return user

    # =====================================================
    # Desactivar Usuario
    # =====================================================

    @staticmethod
    def deactivate_user(

        db,

        user

    ):

        user.is_active = False

        db.commit()

        db.refresh(user)

        return user