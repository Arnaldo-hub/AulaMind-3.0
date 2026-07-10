"""Smoke test sin mutaciones para arranque y endpoints públicos."""
from app import app


def run():
    client = app.test_client()

    health = client.get("/health", follow_redirects=False)
    assert health.status_code == 200, health.status_code
    payload = health.get_json()
    assert payload and payload.get("status") == "ok", payload

    status = client.get("/status", follow_redirects=False)
    assert status.status_code == 200, status.status_code
    payload = status.get_json()
    assert payload and payload.get("status") == "running", payload

    login = client.get("/auth/login", follow_redirects=False)
    assert login.status_code == 200, login.status_code

    admin = client.get("/admin/security-check", follow_redirects=False)
    assert admin.status_code == 302, admin.status_code

    print({
        "health": 200,
        "status": 200,
        "login": 200,
        "anonymous_admin": 302,
    })
    print("STAGING SMOKE OK")


if __name__ == "__main__":
    run()
