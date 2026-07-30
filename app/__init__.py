import os
from flask import Flask

from app import database
from app.routes import auth, dashboard, ussd


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    # SECRET_KEY signs session cookies; override in instance/config.py or the
    # SECRET_KEY env var for anything beyond local dev.
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
    app.config.from_pyfile(os.path.join(app.instance_path, "config.py"), silent=True)
    database.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(ussd.bp)
    return app
