from flask import Blueprint, render_template

from app.data.mock_data import MOCK_ANOMALIES, MOCK_CURRENT_USER

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
def dashboard():
    current_page = 1
    total_pages = 1
    return render_template(
        "pages/dashboard.html",
        anomalies=MOCK_ANOMALIES,
        current_user=MOCK_CURRENT_USER,
        # kept separate from anomalies|length for when pagination lands
        total_anomalies_count=len(MOCK_ANOMALIES),
        current_page=current_page,
        total_pages=total_pages,
        has_previous=current_page > 1,
        has_next=current_page < total_pages,
    )
