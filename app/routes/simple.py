from flask import Blueprint, render_template

bp = Blueprint('simple', __name__)

@bp.route('/')
def home():
    return render_template('pages/login.html')

@bp.route('/dashboard')
def dashboard():
    return render_template('pages/dashboard.html')