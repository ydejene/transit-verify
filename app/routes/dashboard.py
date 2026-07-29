from flask import Blueprint, render_template

from app.data.mock_data import MOCK_ANOMALIES, MOCK_CURRENT_USER

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
def dashboard():
    return render_template(
        "pages/dashboard.html",
        anomalies=MOCK_ANOMALIES,
        current_user=MOCK_CURRENT_USER,
    )
