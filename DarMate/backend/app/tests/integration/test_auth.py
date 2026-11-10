from app.core.exceptions import AppError  # noqa: F401


def test_register_login_me(api, client):
    api.register("a@test.tn")
    h = api.login("a@test.tn")
    me = client.get("/api/v1/users/me", headers=h).json()
    assert me["email"] == "a@test.tn" and me["roles"] == ["SEEKER"]


def test_weak_password_rejected(client):
    r = client.post("/api/v1/auth/register", json={"email": "w@test.tn", "password": "weakpassword", "first_name": "a", "last_name": "b"})
    assert r.status_code == 422


def test_duplicate_email(api, client):
    api.register("d@test.tn")
    r = client.post("/api/v1/auth/register", json={"email": "d@test.tn", "password": "Passw0rdOK", "first_name": "a", "last_name": "b", "role": "SEEKER"})
    assert r.status_code == 409


def test_cannot_self_register_admin(client):
    r = client.post("/api/v1/auth/register", json={"email": "x@test.tn", "password": "Passw0rdOK", "first_name": "a",
                                                    "last_name": "b", "role": ["ADMIN"]})
    assert r.status_code == 422


def test_wrong_password_and_lockout(api, client):
    api.register("l@test.tn")
    for _ in range(3):
        assert client.post("/api/v1/auth/login", json={"email": "l@test.tn", "password": "bad"}).status_code == 401
    r = client.post("/api/v1/auth/login", json={"email": "l@test.tn", "password": "Passw0rdOK"})
    assert r.status_code == 429  # compte verrouillé même avec le bon mot de passe


def test_protected_route_requires_token(client):
    assert client.get("/api/v1/users/me").status_code == 401
    assert client.get("/api/v1/users/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_refresh_rotation_and_reuse_detection(api, client):
    api.register("r@test.tn")
    r = client.post("/api/v1/auth/login", json={"email": "r@test.tn", "password": "Passw0rdOK"})
    old = r.cookies.get("refresh_token")
    assert old
    new = client.post("/api/v1/auth/refresh")
    assert new.status_code == 200 and new.json()["access_token"]
    # réutilisation de l'ancien jeton => refus + révocation de toutes les sessions
    client.cookies.set("refresh_token", old, path="/api/v1/auth")
    assert client.post("/api/v1/auth/refresh").status_code == 401


def test_logout_revokes_refresh(api, client):
    api.register("o@test.tn")
    client.post("/api/v1/auth/login", json={"email": "o@test.tn", "password": "Passw0rdOK"})
    token = client.cookies.get("refresh_token")
    client.post("/api/v1/auth/logout")
    client.cookies.set("refresh_token", token, path="/api/v1/auth")
    assert client.post("/api/v1/auth/refresh").status_code == 401


def test_password_reset_flow(api, client, caplog):
    import re, logging
    api.register("p@test.tn")
    with caplog.at_level(logging.WARNING, logger="darmate.mail"):
        assert client.post("/api/v1/auth/forgot-password", json={"email": "p@test.tn"}).status_code == 200
    token = re.search(r"token=([\w-]+)", caplog.text).group(1)
    assert client.post("/api/v1/auth/reset-password", json={"token": token, "new_password": "NewPassw0rd1"}).status_code == 200
    assert client.post("/api/v1/auth/reset-password", json={"token": token, "new_password": "Another1Pass"}).status_code == 422  # usage unique
    api.login("p@test.tn", "NewPassw0rd1")


def test_forgot_password_unknown_email_same_answer(client):
    assert client.post("/api/v1/auth/forgot-password", json={"email": "nobody@test.tn"}).status_code == 200


def test_suspended_user_cannot_login_nor_use_token(api, client):
    uid, h = api.user("s@test.tn")
    admin = api.login("admin@test.tn", "AdminPass123")
    assert client.patch(f"/api/v1/admin/users/{uid}/status", json={"status": "SUSPENDED"}, headers=admin).status_code == 200
    assert client.get("/api/v1/users/me", headers=h).status_code == 401
    assert client.post("/api/v1/auth/login", json={"email": "s@test.tn", "password": "Passw0rdOK"}).status_code == 403
