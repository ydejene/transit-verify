import pytest
from werkzeug.security import generate_password_hash

from app import create_app, database

TEST_PASSWORD = "Test123!"


@pytest.fixture
def app(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DATABASE_PATH", str(tmp_path / "test.sqlite3"))
    flask_app = create_app()
    flask_app.config.update(TESTING=True, SECRET_KEY="test-secret")

    with flask_app.app_context():
        database.init_db()
        _seed(database.get_db())

    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def _seed(db):
    zone_id = db.execute(
        "INSERT INTO zones (assignedZoneName, physicalHubLocation) VALUES (?, ?)",
        ("Megenagna", "Megenagna Hub"),
    ).lastrowid
    db.execute(
        "INSERT INTO route_segments (routeCode, routeName, zoneId) VALUES (?, ?, ?)",
        ("Meg-01", "Meg-Bole 01", zone_id),
    )
    for name in ("Route Chopping", "Fare Overcharge"):
        db.execute(
            "INSERT INTO violation_types (violationName, description) VALUES (?, ?)",
            (name, ""),
        )

    users = [
        ("Test Manager", "manager@test.et", "TerminalManager", "Megenagna"),
        ("Test Supervisor", "supervisor@test.et", "Supervisor", None),
        ("Test Officer", "officer@test.et", "Officer", None),
    ]
    for full_name, email, role, zone in users:
        db.execute(
            "INSERT INTO users (fullName, email, passwordHash, role, assignedZone) VALUES (?, ?, ?, ?, ?)",
            (full_name, email, generate_password_hash(TEST_PASSWORD), role, zone),
        )
    db.commit()


def login(client, email):
    return client.post("/", data={"email": email, "password": TEST_PASSWORD})
