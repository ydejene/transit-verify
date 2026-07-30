from flask import Blueprint, request

from app.services.ussd_service import handle_ussd

bp = Blueprint("ussd", __name__)


@bp.route("/ussd", methods=["POST"])
def ussd():
    # phoneNumber arrives per Africa's Talking's API spec but is never
    # read, stored, or logged
    text = request.form.get("text", "")
    return handle_ussd(text), 200, {"Content-Type": "text/plain"}
