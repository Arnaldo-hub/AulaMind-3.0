"""Regresión CSRF para formularios sensibles."""
from app import app


def run():
    client = app.test_client()

    cases = [
        ("/auth/login", {"email": "nobody@example.invalid", "password": "Invalid12345"}),
        ("/auth/register", {
            "first_name": "Test",
            "last_name": "CSRF",
            "email": "csrf@example.invalid",
            "password": "Invalid12345",
            "confirm_password": "Invalid12345",
        }),
        ("/auth/forgot-password", {"email": "nobody@example.invalid"}),
    ]

    results = {}
    for path, payload in cases:
        response = client.post(path, data=payload, follow_redirects=False)
        assert response.status_code == 400, (path, response.status_code)
        results[path] = response.status_code

    print(results)
    print("CSRF REGRESSION OK")


if __name__ == "__main__":
    run()
