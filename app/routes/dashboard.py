import re
from datetime import datetime

from flask import Blueprint, jsonify, render_template, request

from app.data.mock_data import MOCK_ANOMALIES  # anomaly data itself is still mocked
from app.routes.auth import current_user as load_current_user
from app.routes.auth import login_required

bp = Blueprint("dashboard", __name__)

RECEIPT_PATTERN = re.compile(r"^RCP-\d{4}-\d{3}$")


@bp.route("/dashboard")
@login_required
def dashboard():
    user_row = load_current_user()
    current_user = {
        "full_name": user_row["fullName"],
        "email": user_row["email"],
        "role": user_row["role"],
        "assignedZone": user_row["assignedZone"],
    }

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
@login_required
def update_anomaly_status(anomaly_id):
    user_row = load_current_user()
    if user_row["role"] != "TerminalManager":
        return jsonify(error="Only a Terminal Manager can update anomaly status."), 403

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
    anomaly["updated_by_email"] = user_row["email"]
    anomaly["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    return jsonify(anomaly)
