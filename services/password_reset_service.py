import hashlib
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from config import Config

class PasswordResetService:
    SALT = "aulamind-password-reset-v1"

    @staticmethod
    def _serializer():
        return URLSafeTimedSerializer(Config.SECRET_KEY)

    @staticmethod
    def _fingerprint(password_hash):
        return hashlib.sha256(password_hash.encode("utf-8")).hexdigest()[:24]

    @classmethod
    def generate_token(cls, user):
        return cls._serializer().dumps(
            {"uid": str(user.id), "pwd": cls._fingerprint(user.password_hash)},
            salt=cls.SALT,
        )

    @classmethod
    def verify_token(cls, token, db):
        from models.user import User
        try:
            data = cls._serializer().loads(
                token, salt=cls.SALT,
                max_age=Config.PASSWORD_RESET_TOKEN_MAX_AGE,
            )
        except (BadSignature, SignatureExpired):
            return None
        user = db.query(User).filter(User.id == str(data.get("uid", ""))).first()
        if user is None or not user.is_active:
            return None
        if data.get("pwd") != cls._fingerprint(user.password_hash):
            return None
        return user
