from app.auth import hash_password
from app.models import KlevaUser
from tests.conftest import USER_PASSWORD


def login(client, email, password):
    return client.post("/api/auth/login", data={"username": email, "password": password})


def test_login_returns_bearer_token(client, kleva_user):
    response = login(client, kleva_user.email, USER_PASSWORD)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_email_is_case_insensitive(client, kleva_user):
    assert login(client, "ANA@Kleva.Demo", USER_PASSWORD).status_code == 200


def test_login_wrong_password(client, kleva_user):
    response = login(client, kleva_user.email, "Wrong12345")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_unknown_user_gets_same_message(client, kleva_user):
    response = login(client, "nadie@kleva.demo", USER_PASSWORD)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_inactive_user(client, db_add):
    db_add(
        KlevaUser(
            first_name="Ex",
            last_name="User",
            email="ex@kleva.demo",
            password_hash=hash_password(USER_PASSWORD),
            is_active=False,
        )
    )
    assert login(client, "ex@kleva.demo", USER_PASSWORD).status_code == 401


def test_me_returns_user_without_password(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "ana@kleva.demo"
    assert "password_hash" not in body


def test_me_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_rejects_invalid_token(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401
