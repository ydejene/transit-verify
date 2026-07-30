from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from app.database import get_db

bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def current_user():
    db = get_db()
    return db.execute(
        "SELECT userId, fullName, email, role, assignedZone FROM users WHERE userId = ?",
        (session["user_id"],),
    ).fetchone()


@bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None or not check_password_hash(user["passwordHash"], password):
            flash("Invalid email or password.")
            return render_template("pages/login.html")

        session.clear()
        session["user_id"] = user["userId"]
        db.execute(
            "UPDATE users SET lastLogin = CURRENT_TIMESTAMP WHERE userId = ?",
            (user["userId"],),
        )
        db.commit()
        return redirect(url_for("dashboard.dashboard"))

    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("pages/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
