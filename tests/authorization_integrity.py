"""Pruebas de integridad para autorización centralizada."""

from app import app
from database.session import SessionLocal
from models.user import User


def run():
    db = SessionLocal()
    try:
        teacher = db.query(User).filter(User.role == "teacher", User.is_active.is_(True)).first()
        admin = db.query(User).filter(User.role == "admin", User.is_active.is_(True)).first()
    finally:
        db.close()

    client = app.test_client()

    response = client.get("/admin/security-check", follow_redirects=False)
    assert response.status_code == 302, response.status_code
    assert "/auth/login" in response.headers.get("Location", "")

    if teacher:
        with client.session_transaction() as sess:
            sess["user_id"] = str(teacher.id)
        response = client.get("/admin/security-check", follow_redirects=False)
        assert response.status_code == 403, response.status_code

    if admin:
        with client.session_transaction() as sess:
            sess["user_id"] = str(admin.id)
        response = client.get("/admin/security-check", follow_redirects=False)
        assert response.status_code == 200, response.status_code

    print({
        "anonymous": 302,
        "teacher": 403 if teacher else "SKIP_NO_TEACHER",
        "admin": 200 if admin else "SKIP_NO_ADMIN",
    })
    print("AUTHORIZATION INTEGRITY OK")


if __name__ == "__main__":
    run()
