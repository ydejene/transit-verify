"""Temporary stand-in for anomaly_service/DB layer — shape matches the anomalies table (docs/erd.md)."""

MOCK_ANOMALIES = [
    {
        "vehiclePlate": "AA-4592",
        "terminalZone": "Megenagna",
        "routeSegment": "Meg-Bole 01",
        "violationType": "Route Chopping",
        "reportCount": 6,
        "windowStart": "2026-07-28 08:10",
        "status": "Resolved",
        "penaltyReceiptRef": "RCP-2026-014",
        "updated_by_full_name": "Abebe Kebede",
        "updated_at": "2026-07-28 08:25",
    },
    {
        "vehiclePlate": "AA-2184",
        "terminalZone": "Bole",
        "routeSegment": "Bole-Megenagna 02",
        "violationType": "Fare Overcharge",
        "reportCount": 5,
        "windowStart": "2026-07-28 09:20",
        "status": "Reviewed",
        "penaltyReceiptRef": "",
        "updated_by_full_name": "Meron Tesfaye",
        "updated_at": "2026-07-28 09:35",
    },
    {
        "vehiclePlate": "AA-7731",
        "terminalZone": "Saris",
        "routeSegment": "Saris-Asko 01",
        "violationType": "Route Chopping",
        "reportCount": 5,
        "windowStart": "2026-07-28 10:05",
        "status": "Pending",
        "penaltyReceiptRef": "",
        "updated_by_full_name": None,
        "updated_at": None,
    },
    {
        "vehiclePlate": "AA-1102",
        "terminalZone": "Tor Hailoch",
        "routeSegment": "Tor Hailoch-Asko 03",
        "violationType": "Fare Overcharge",
        "reportCount": 7,
        "windowStart": "2026-07-28 11:10",
        "status": "Resolved",
        "penaltyReceiptRef": "RCP-2026-015",
        "updated_by_full_name": "Abebe Kebede",
        "updated_at": "2026-07-28 11:30",
    },
]

MOCK_CURRENT_USER = {
    "full_name": "Abebe Kebede",
    "role": "Supervisor",
}
