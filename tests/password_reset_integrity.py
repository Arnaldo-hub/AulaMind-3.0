from sqlalchemy import text
from app import app
from database.session import SessionLocal
from services.password_reset_service import PasswordResetService

def run():
    db=SessionLocal()
    try:
        row=db.execute(text("SELECT id FROM users WHERE is_active = 1 LIMIT 1")).first()
        assert row is not None, "Se necesita al menos un usuario activo"
        from models.school import School
        from models.subscription import Subscription
        from models.user import User
        user=db.query(User).filter(User.id==str(row[0])).first()
        token=PasswordResetService.generate_token(user)
        assert PasswordResetService.verify_token(token,db) is not None
        assert PasswordResetService.verify_token(token+"x",db) is None
        old=user.password_hash
        user.password_hash=old+"-test-change"
        db.flush()
        assert PasswordResetService.verify_token(token,db) is None
        db.rollback()
        client=app.test_client()
        assert client.get("/auth/forgot-password").status_code==200
        print({"valid_token":"OK","tampered_token":"REJECTED","reused_after_change":"REJECTED","forgot_get":200})
        print("PASSWORD RESET INTEGRITY OK")
    finally:
        db.close()

if __name__=="__main__":
    run()
