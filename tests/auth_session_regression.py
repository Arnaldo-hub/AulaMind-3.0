"""Regresión de autenticación y ciclo de sesión."""
from app import app


def run():
    client = app.test_client()

    # Ruta protegida administrativa: anónimo debe ir a login.
    response = client.get("/admin/security-check", follow_redirects=False)
    assert response.status_code == 302, response.status_code
    assert "/auth/login" in response.headers.get("Location", "")

    # Una sesión con usuario inexistente debe invalidarse y volver a login.
    with client.session_transaction() as sess:
        sess["user_id"] = "00000000-0000-0000-0000-000000000000"
        sess["role"] = "admin"

    response = client.get("/admin/security-check", follow_redirects=False)
    assert response.status_code == 302, response.status_code
    assert "/auth/login" in response.headers.get("Location", "")

    with client.session_transaction() as sess:
        assert "user_id" not in sess
        assert "role" not in sess

    # Logout debe limpiar una sesión existente.
    with client.session_transaction() as sess:
        sess["user_id"] = "test-user"
        sess["role"] = "teacher"
        sess["user_email"] = "test@example.invalid"

    response = client.get("/auth/logout", follow_redirects=False)
    assert response.status_code == 302, response.status_code
    assert "/auth/login" in response.headers.get("Location", "")

    with client.session_transaction() as sess:
        assert "user_id" not in sess
        assert "role" not in sess
        assert "user_email" not in sess

    print({
        "anonymous_admin": 302,
        "invalid_session": "CLEARED",
        "logout_session": "CLEARED",
    })
    print("AUTH SESSION REGRESSION OK")


if __name__ == "__main__":
    run()
