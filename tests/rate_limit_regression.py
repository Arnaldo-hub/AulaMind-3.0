"""Regresión funcional del límite de intentos de login."""
import re
from app import app


TOKEN_RE = re.compile(
    rb'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']'
)


def csrf_token(client):
    response = client.get("/auth/login")
    assert response.status_code == 200, response.status_code
    match = TOKEN_RE.search(response.data)
    assert match is not None, "No se encontró csrf_token en login.html"
    return match.group(1).decode("utf-8")


def run():
    client = app.test_client()
    statuses = []

    # Login permite 10 POST por minuto; el siguiente debe ser 429.
    for index in range(11):
        token = csrf_token(client)
        response = client.post(
            "/auth/login",
            data={
                "email": f"rate-limit-{index}@example.invalid",
                "password": "Invalid12345",
                "csrf_token": token,
            },
            follow_redirects=False,
        )
        statuses.append(response.status_code)

    assert all(code == 200 for code in statuses[:10]), statuses
    assert statuses[10] == 429, statuses

    print({"login_attempts": statuses})
    print("RATE LIMIT REGRESSION OK")


if __name__ == "__main__":
    run()
