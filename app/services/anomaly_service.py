import math
import re
from datetime import datetime, timedelta, timezone

from app.config import (
    ANOMALY_THRESHOLD,
    ANOMALY_WINDOW_MINUTES,
    SPAM_CEILING,
    SPAM_WINDOW_MINUTES,
)
from app.database import get_db

TS_FORMAT = "%Y-%m-%d %H:%M:%S"
RECEIPT_PATTERN = re.compile(r"^RCP-\d{4}-\d{3}$")
PER_PAGE = 10
ADDIS_ABABA_UTC_OFFSET = timedelta(hours=3)  # no DST in Ethiopia


def _minutes_ago_str(minutes):
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    return cutoff.strftime(TS_FORMAT)


def _addis_date_to_utc_bound(date_str, end_of_day=False):
    """Converts an Addis-local calendar date into a UTC timestamp bound."""
    local_midnight = datetime.strptime(date_str, "%Y-%m-%d")
    local_bound = local_midnight + timedelta(hours=23, minutes=59, seconds=59) if end_of_day else local_midnight
    utc_bound = local_bound - ADDIS_ABABA_UTC_OFFSET
    return utc_bound.strftime(TS_FORMAT)


def addis_today_iso():
    """Today's calendar date in Addis Ababa, independent of server timezone."""
    return (datetime.now(timezone.utc) + ADDIS_ABABA_UTC_OFFSET).strftime("%Y-%m-%d")


def _utc_str_to_addis_str(utc_str):
    if not utc_str:
        return utc_str
    return (datetime.strptime(utc_str, TS_FORMAT) + ADDIS_ABABA_UTC_OFFSET).strftime(TS_FORMAT)


def record_report(vehicle_plate, terminal_zone, route_segment, violation_type):
    """Spam filter then anomaly aggregation. Returns False if discarded as spam."""
    db = get_db()

    spam_count = db.execute(
        """SELECT COUNT(*) FROM raw_reports
           WHERE vehiclePlate = ? AND violationType = ? AND timestamp >= ?""",
        (vehicle_plate, violation_type, _minutes_ago_str(SPAM_WINDOW_MINUTES)),
    ).fetchone()[0]

    if spam_count >= SPAM_CEILING:
        db.execute(
            """INSERT INTO spam_log (vehiclePlate, violationType, terminalZone, routeSegment)
               VALUES (?, ?, ?, ?)""",
            (vehicle_plate, violation_type, terminal_zone, route_segment),
        )
        db.commit()
        return False

    report_id = db.execute(
        """INSERT INTO raw_reports (vehiclePlate, terminalZone, routeSegment, violationType)
           VALUES (?, ?, ?, ?)""",
        (vehicle_plate, terminal_zone, route_segment, violation_type),
    ).lastrowid

    _aggregate(db, vehicle_plate, terminal_zone, route_segment, violation_type, report_id)
    db.commit()
    return True


def _aggregate(db, vehicle_plate, terminal_zone, route_segment, violation_type, report_id):
    window_start_cutoff = _minutes_ago_str(ANOMALY_WINDOW_MINUTES)

    existing = db.execute(
        """SELECT anomalyId, windowStart FROM anomalies
           WHERE vehiclePlate = ? AND terminalZone = ? AND routeSegment = ? AND violationType = ?
           AND windowStart >= ?""",
        (vehicle_plate, terminal_zone, route_segment, violation_type, window_start_cutoff),
    ).fetchone()

    if existing:
        # count reports already tagged to this anomaly plus any not yet tagged,
        # not just untagged ones, or a later report would reset the total
        new_count = db.execute(
            """SELECT COUNT(*) FROM raw_reports
               WHERE vehiclePlate = ? AND terminalZone = ? AND routeSegment = ? AND violationType = ?
               AND (anomaly_id = ? OR anomaly_id IS NULL) AND timestamp >= ?""",
            (vehicle_plate, terminal_zone, route_segment, violation_type, existing["anomalyId"], existing["windowStart"]),
        ).fetchone()[0]

        db.execute(
            "UPDATE anomalies SET reportCount = ?, updated_at = CURRENT_TIMESTAMP WHERE anomalyId = ?",
            (new_count, existing["anomalyId"]),
        )
        db.execute("UPDATE raw_reports SET anomaly_id = ? WHERE reportId = ?", (existing["anomalyId"], report_id))
        return

    count, window_start = db.execute(
        """SELECT COUNT(*), MIN(timestamp) FROM raw_reports
           WHERE vehiclePlate = ? AND terminalZone = ? AND routeSegment = ? AND violationType = ?
           AND anomaly_id IS NULL AND timestamp >= ?""",
        (vehicle_plate, terminal_zone, route_segment, violation_type, window_start_cutoff),
    ).fetchone()

    if count < ANOMALY_THRESHOLD:
        return

    new_anomaly_id = db.execute(
        """INSERT INTO anomalies
           (vehiclePlate, terminalZone, routeSegment, violationType, reportCount, windowStart, status, penaltyReceiptRef)
           VALUES (?, ?, ?, ?, ?, ?, 'Pending', '')""",
        (vehicle_plate, terminal_zone, route_segment, violation_type, count, window_start),
    ).lastrowid

    db.execute(
        """UPDATE raw_reports SET anomaly_id = ?
           WHERE vehiclePlate = ? AND terminalZone = ? AND routeSegment = ? AND violationType = ?
           AND anomaly_id IS NULL AND timestamp >= ?""",
        (new_anomaly_id, vehicle_plate, terminal_zone, route_segment, violation_type, window_start),
    )


def get_anomalies(zone=None, status=None, search=None, date_from=None, date_to=None, page=1, per_page=PER_PAGE):
    """Returns (rows, total_count, total_pages, page) for the given filters."""
    db = get_db()
    conditions = []
    params = []

    if zone and zone != "All":
        conditions.append("a.terminalZone = ?")
        params.append(zone)
    if status and status != "All":
        conditions.append("a.status = ?")
        params.append(status)
    if search:
        conditions.append("a.vehiclePlate LIKE ?")
        params.append(f"%{search}%")
    if date_from:
        conditions.append("a.windowStart >= ?")
        params.append(_addis_date_to_utc_bound(date_from))
    if date_to:
        conditions.append("a.windowStart <= ?")
        params.append(_addis_date_to_utc_bound(date_to, end_of_day=True))

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    total = db.execute(f"SELECT COUNT(*) FROM anomalies a {where_clause}", params).fetchone()[0]
    total_pages = max(1, math.ceil(total / per_page))
    page = min(max(1, page), total_pages)
    offset = (page - 1) * per_page

    rows = db.execute(
        f"""SELECT a.*, u.email AS updated_by_email
            FROM anomalies a
            LEFT JOIN users u ON a.updated_by_user_id = u.userId
            {where_clause}
            ORDER BY a.windowStart DESC
            LIMIT ? OFFSET ?""",
        [*params, per_page, offset],
    ).fetchall()

    # displayed to users in Addis time; stored/compared as UTC everywhere else
    anomalies = []
    for row in rows:
        anomaly = dict(row)
        anomaly["windowStart"] = _utc_str_to_addis_str(anomaly["windowStart"])
        anomaly["updated_at"] = _utc_str_to_addis_str(anomaly["updated_at"])
        anomalies.append(anomaly)

    return anomalies, total, total_pages, page


def update_status(anomaly_id, new_status, receipt, updated_by_user_id):
    """Forward-only status update. Returns (success, error_message)."""
    db = get_db()
    anomaly = db.execute("SELECT status FROM anomalies WHERE anomalyId = ?", (anomaly_id,)).fetchone()

    if anomaly is None:
        return False, "Anomaly not found."
    if anomaly["status"] != "Pending":
        return False, "Status is forward-only; this anomaly is already locked."
    if new_status not in ("Reviewed", "Resolved"):
        return False, "Status must be Reviewed or Resolved."
    if new_status == "Resolved" and not RECEIPT_PATTERN.match(receipt or ""):
        return False, "Receipt must match RCP-YYYY-NNN."

    db.execute(
        """UPDATE anomalies
           SET status = ?, penaltyReceiptRef = ?, updated_by_user_id = ?, updated_at = CURRENT_TIMESTAMP
           WHERE anomalyId = ?""",
        (new_status, receipt if new_status == "Resolved" else "", updated_by_user_id, anomaly_id),
    )
    db.commit()
    return True, None
