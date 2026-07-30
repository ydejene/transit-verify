"""USSD 6-screen menu state machine.

No server-side session state: Africa's Talking's `text` field already
accumulates every prior selection for the session, separated by '*', so
each step is derived by re-parsing it.
"""

import re

from app.database import get_db
from app.services import anomaly_service

VIOLATION_TYPES = ["Route Chopping", "Fare Overcharge"]
# not a strict format match (real plates vary too much for one pattern) —
# just rejects obviously-not-a-plate input like "hello" or a single char
PLATE_PATTERN = re.compile(r"^(?=.*\d)[A-Z0-9\- ]{4,15}$")


def _zones(db):
    return db.execute(
        "SELECT zoneId, assignedZoneName FROM zones ORDER BY zoneId"
    ).fetchall()


def _routes_for_zone(db, zone_id):
    return db.execute(
        "SELECT routeId, routeName FROM route_segments WHERE zoneId = ? ORDER BY routeId",
        (zone_id,),
    ).fetchall()


def _menu_index(raw_choice, option_count):
    if not raw_choice.isdigit():
        return None
    choice = int(raw_choice)
    return choice - 1 if 1 <= choice <= option_count else None


def handle_ussd(text):
    """Returns the full 'CON ...' / 'END ...' response for this step."""
    db = get_db()
    steps = text.split("*") if text else []

    if not steps:
        return "CON Welcome to Transit Verify\n1. Report a Violation"

    if steps[0] != "1":
        return "END Invalid selection."

    if len(steps) == 1:
        return "CON Enter the vehicle's license plate number:"

    plate = steps[1].strip().upper()
    if not PLATE_PATTERN.match(plate):
        return "END Invalid plate number. Use letters, numbers, and hyphens only."

    zones = _zones(db)
    if len(steps) == 2:
        menu = "\n".join(
            f"{i + 1}. {z['assignedZoneName']}" for i, z in enumerate(zones)
        )
        return f"CON Select the zone:\n{menu}"

    zone_choice = _menu_index(steps[2], len(zones))
    if zone_choice is None:
        return "END Invalid zone selection."
    zone = zones[zone_choice]

    routes = _routes_for_zone(db, zone["zoneId"])
    if len(steps) == 3:
        if not routes:
            return "END No routes configured for this zone."
        menu = "\n".join(f"{i + 1}. {r['routeName']}" for i, r in enumerate(routes))
        return f"CON Select the route:\n{menu}"

    route_choice = _menu_index(steps[3], len(routes))
    if route_choice is None:
        return "END Invalid route selection."
    route = routes[route_choice]

    if len(steps) == 4:
        menu = "\n".join(f"{i + 1}. {v}" for i, v in enumerate(VIOLATION_TYPES))
        return f"CON Select the violation:\n{menu}"

    violation_choice = _menu_index(steps[4], len(VIOLATION_TYPES))
    if violation_choice is None:
        return "END Invalid violation selection."
    violation = VIOLATION_TYPES[violation_choice]

    if len(steps) == 5:
        return (
            "CON Confirm report:\n"
            f"Plate: {plate}\nZone: {zone['assignedZoneName']}\n"
            f"Route: {route['routeName']}\nViolation: {violation}\n"
            "1. Confirm\n2. Cancel"
        )

    if steps[5] == "2":
        return "END Report cancelled."
    if steps[5] != "1":
        return "END Invalid selection."

    anomaly_service.record_report(
        plate, zone["assignedZoneName"], route["routeName"], violation
    )
    return "END Thank you. Your report has been submitted."
