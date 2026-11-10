import os
import tempfile
from pathlib import Path

_tmp = tempfile.mkdtemp(prefix="darmate_test_")
os.environ.update({
    "JWT_SECRET_KEY": "test-secret-key-test-secret-key-0123456789",
    "DATABASE_URL": f"sqlite:///{_tmp}/test.db",
    "RATE_LIMIT_ENABLED": "false",
    "UPLOAD_DIR": f"{_tmp}/uploads",
    "ADMIN_EMAIL": "admin@test.tn",
    "ADMIN_PASSWORD": "AdminPass123",
    "MAX_FAILED_LOGINS": "3",
})

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.infrastructure.database.base import Base  # noqa: E402
from app.infrastructure.database.connection import engine  # noqa: E402
import app.infrastructure.models  # noqa: E402,F401
from app.main import app  # noqa: E402
from app.scripts import seed  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    seed.run()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class Api:
    """Petit utilitaire de test : crée des utilisateurs et envoie des requêtes authentifiées."""

    def __init__(self, client: TestClient) -> None:
        self.c = client

    def register(self, email, roles=("SEEKER",), password="Passw0rdOK", first="Test", last="User"):
        r = self.c.post("/api/v1/auth/register", json={"email": email, "password": password, "first_name": first,
                                                         "last_name": last, "roles": list(roles)})
        assert r.status_code == 201, r.text
        return r.json()

    def login(self, email, password="Passw0rdOK"):
        r = self.c.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    def user(self, email, roles=("SEEKER",), **kw):
        data = self.register(email, roles, **kw)
        return data["id"], self.login(email, kw.get("password", "Passw0rdOK"))


@pytest.fixture
def api(client):
    return Api(client)


@pytest.fixture
def city_id(client):
    return client.get("/api/v1/reference/cities").json()[0]["id"]


@pytest.fixture
def category_id(client):
    return client.get("/api/v1/reference/categories").json()[0]["id"]
