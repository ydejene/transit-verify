import re
from datetime import datetime

from flask import Blueprint, jsonify, render_template, request

from app.data.mock_data import MOCK_ANOMALIES, MOCK_CURRENT_USER

bp = Blueprint("dashboard", __name__)

RECEIPT_PATTERN = re.compile(r"^RCP-\d{4}-\d{3}$")
VALID_ROLES = ("Supervisor", "TerminalManager", "Officer")


@bp.route("/dashboard")
def dashboard():
    # temporary preview switch until real sessions exist (auth.py)
    role = request.args.get("role", MOCK_CURRENT_USER["role"])
    if role not in VALID_ROLES:
        role = MOCK_CURRENT_USER["role"]
    current_user = {**MOCK_CURRENT_USER, "role": role}

    current_page = 1
    total_pages = 1
    return render_template(
        "pages/dashboard.html",
        anomalies=MOCK_ANOMALIES,
        current_user=current_user,
        # kept separate from anomalies|length for when pagination lands
        total_anomalies_count=len(MOCK_ANOMALIES),
        current_page=current_page,
        total_pages=total_pages,
        has_previous=current_page > 1,
        has_next=current_page < total_pages,
    )


@bp.route("/dashboard/anomalies/<int:anomaly_id>/status", methods=["POST"])
def update_anomaly_status(anomaly_id):
    anomaly = next((a for a in MOCK_ANOMALIES if a["anomalyId"] == anomaly_id), None)
    if anomaly is None:
        return jsonify(error="Anomaly not found."), 404

    if anomaly["status"] != "Pending":
        return jsonify(error="Status is forward-only; this anomaly is already locked."), 400

    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    receipt = (payload.get("penaltyReceiptRef") or "").strip()

    if status not in ("Reviewed", "Resolved"):
        return jsonify(error="Status must be Reviewed or Resolved."), 400

    if status == "Resolved" and not RECEIPT_PATTERN.match(receipt):
        return jsonify(error="Receipt must match RCP-YYYY-NNN."), 400

    anomaly["status"] = status
    anomaly["penaltyReceiptRef"] = receipt if status == "Resolved" else ""
    # replaced with the authenticated user's email once real sessions exist
    anomaly["updated_by_email"] = MOCK_CURRENT_USER["email"]
    anomaly["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    return jsonify(anomaly)
