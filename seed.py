"""Populates a fresh database with reference data and demo accounts.

Run with: flask --app app init-db  (creates the schema)
Then:     python seed.py            (populates it)
"""

from werkzeug.security import generate_password_hash

from app import create_app
from app.database import get_db

ZONES = [
    ("Megenagna", "Megenagna Terminal Hub"),
    ("Bole", "Bole Terminal Hub"),
    ("Saris", "Saris Terminal Hub"),
    ("Asko", "Asko Terminal Hub"),
    ("Tor Hailoch", "Tor Hailoch Terminal Hub"),
]

# (routeCode, routeName, zoneName)
ROUTE_SEGMENTS = [
    ("Meg-Bole-01", "Meg-Bole 01", "Megenagna"),
    ("Bole-Meg-02", "Bole-Megenagna 02", "Bole"),
    ("Saris-Asko-01", "Saris-Asko 01", "Saris"),
    ("TorHailoch-Asko-03", "Tor Hailoch-Asko 03", "Tor Hailoch"),
]

VIOLATION_TYPES = [
    ("Route Chopping", "Vehicle terminates the route early, short-changing commuters."),
    ("Fare Overcharge", "Vehicle charges more than the regulated fare for the route."),
]

# (fullName, email, password, role, assignedZone)
DEMO_USERS = [
    ("Abebe Kebede", "a.kebede@transit.gov.et", "Manager123!", "TerminalManager", "Megenagna"),
    ("Meron Tesfaye", "m.tesfaye@transit.gov.et", "Supervisor123!", "Supervisor", None),
    ("Dawit Alemu", "officer@transit.gov.et", "Officer123!", "Officer", None),
]


def seed():
    app = create_app()
    with app.app_context():
        db = get_db()

        zone_ids = {}
        for name, hub in ZONES:
            cur = db.execute(
                "INSERT INTO zones (assignedZoneName, physicalHubLocation) VALUES (?, ?)",
                (name, hub),
            )
            zone_ids[name] = cur.lastrowid

        for code, name, zone_name in ROUTE_SEGMENTS:
            db.execute(
                "INSERT INTO route_segments (routeCode, routeName, zoneId) VALUES (?, ?, ?)",
                (code, name, zone_ids[zone_name]),
            )

        for name, description in VIOLATION_TYPES:
            db.execute(
                "INSERT INTO violation_types (violationName, description) VALUES (?, ?)",
                (name, description),
            )

        for full_name, email, password, role, assigned_zone in DEMO_USERS:
            db.execute(
                "INSERT INTO users (fullName, email, passwordHash, role, assignedZone) VALUES (?, ?, ?, ?, ?)",
                (full_name, email, generate_password_hash(password), role, assigned_zone),
            )

        db.commit()
        print("Database seeded.")


if __name__ == "__main__":
    seed()
