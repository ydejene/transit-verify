"""Optional: generates ~60 anomalies with varied statuses, for testing
pagination/filtering at realistic scale. Run after seed.py.

Run with: python seed_demo_anomalies.py
"""

import random

from app import create_app
from app.database import get_db
from app.services import anomaly_service

ZONE_ROUTES = [
    ("Megenagna", "Meg-Bole 01"),
    ("Bole", "Bole-Megenagna 02"),
    ("Saris", "Saris-Asko 01"),
    ("Asko", "Asko-Saris 02"),
    ("Tor Hailoch", "Tor Hailoch-Asko 03"),
]
VIOLATIONS = ["Route Chopping", "Fare Overcharge"]
PLATE_COUNT = 60


def generate():
    app = create_app()
    with app.app_context():
        db = get_db()
        manager_id = db.execute(
            "SELECT userId FROM users WHERE email = ?", ("a.kebede@transit.gov.et",)
        ).fetchone()["userId"]

        for i in range(PLATE_COUNT):
            plate = f"AA-{1000 + i}"
            zone, route = random.choice(ZONE_ROUTES)
            violation = random.choice(VIOLATIONS)
            for _ in range(anomaly_service.ANOMALY_THRESHOLD + random.randint(0, 3)):
                anomaly_service.record_report(plate, zone, route, violation)

        anomalies, total, _, _ = anomaly_service.get_anomalies(
            status="All", per_page=1000
        )
        for anomaly in anomalies:
            roll = random.random()
            if roll < 0.5:
                anomaly_service.update_status(
                    anomaly["anomalyId"],
                    "Resolved",
                    f"RCP-2026-{anomaly['anomalyId']:03d}",
                    manager_id,
                )
            elif roll < 0.7:
                anomaly_service.update_status(
                    anomaly["anomalyId"], "Reviewed", "", manager_id
                )

        print(f"Generated {total} demo anomalies.")


if __name__ == "__main__":
    generate()
