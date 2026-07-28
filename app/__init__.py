import os
from flask import Flask
from app.routes import auth, dashboard, mobile, ussd, simple

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_pyfile(os.path.join(app.instance_path, 'config.py'), silent=True)
    # app.register_blueprint(auth.bp)
    # app.register_blueprint(dashboard.bp)
    # app.register_blueprint(mobile.bp)
    # app.register_blueprint(ussd.bp)
    app.register_blueprint(simple.bp)
    return app
