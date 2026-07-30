from flask import Blueprint, jsonify, render_template, request

from app.routes.auth import current_user as load_current_user
from app.routes.auth import login_required
from app.services import anomaly_service

bp = Blueprint("dashboard", __name__)


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

    zone = request.args.get("zone")
    # a Terminal Manager is scoped to their own zone regardless of the URL
    if current_user["role"] == "TerminalManager" and current_user["assignedZone"]:
        zone = current_user["assignedZone"]

    # UI's Status dropdown defaults to Pending; "All" must be requested explicitly
    status = request.args.get("status", "Pending")
    search = request.args.get("search")
    time_slot = request.args.get("time_slot", "")
    date_preset = request.args.get("date_preset", "")
    page = request.args.get("page", 1, type=int)

    preset_from, preset_to = anomaly_service.resolve_date_preset(date_preset)
    date_from = preset_from or request.args.get("date_from")
    date_to = preset_to or request.args.get("date_to")

    anomalies, total_anomalies_count, total_pages, current_page = (
        anomaly_service.get_anomalies(
            zone=zone,
            status=status,
            search=search,
            date_from=date_from,
            date_to=date_to,
            time_slot=time_slot,
            page=page,
        )
    )

    return render_template(
        "pages/dashboard.html",
        anomalies=anomalies,
        current_user=current_user,
        total_anomalies_count=total_anomalies_count,
        current_page=current_page,
        total_pages=total_pages,
        has_previous=current_page > 1,
        has_next=current_page < total_pages,
        per_page=anomaly_service.PER_PAGE,
        today=anomaly_service.addis_today_iso(),
        filters={
            "zone": zone or "All",
            "status": status,
            "search": search or "",
            "date_from": date_from or "",
            "date_to": date_to or "",
            "time_slot": time_slot,
            "date_preset": date_preset,
        },
    )


@bp.route("/dashboard/anomalies/<int:anomaly_id>/status", methods=["POST"])
@login_required
def update_anomaly_status(anomaly_id):
    user_row = load_current_user()
    if user_row["role"] != "TerminalManager":
        return jsonify(error="Only a Terminal Manager can update anomaly status."), 403

    payload = request.get_json(silent=True) or {}
    success, error = anomaly_service.update_status(
        anomaly_id,
        payload.get("status"),
        (payload.get("penaltyReceiptRef") or "").strip(),
        user_row["userId"],
        manager_zone=user_row["assignedZone"],
    )

    if not success:
        status_code = 404 if error == "Anomaly not found." else 400
        return jsonify(error=error), status_code

    return jsonify(success=True)
