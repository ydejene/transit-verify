from flask import Blueprint, render_template

bp = Blueprint("auth", __name__)


@bp.route("/")
def login():
    return render_template("pages/login.html")
