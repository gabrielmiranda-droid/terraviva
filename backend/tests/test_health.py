import os

os.environ["AUTO_SEED"] = "false"
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from fastapi.testclient import TestClient

from app.main import app


def test_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
