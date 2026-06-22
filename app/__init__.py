# app/__init__.py – Application factory for InterviewGenie.
# This file creates and configures the Flask app, initialises extensions,
# and registers blueprints.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

# Load environment variables from .env file (if present)
load_dotenv()

# Initialise extensions (will be bound to app later)
db = SQLAlchemy()                     # SQLAlchemy for database ORM
login_manager = LoginManager()        # Flask-Login for user sessions
csrf = CSRFProtect()                  # CSRF protection for all forms

def create_app():
    """
    Factory function that creates and configures the Flask application.
    Returns a fully configured Flask app instance.
    """
    app = Flask(__name__)  # Create the Flask instance

    # ---- Configuration ----
    # Secret key for sessions and CSRF (from environment, with fallback)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    # Database URI; default to SQLite in the instance folder
    basedir = os.path.abspath(os.path.dirname(__file__))
    # Ensure the instance folder exists so SQLite can create the DB file
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(instance_path, 'app.db')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Silence warning

    # ---- Initialise extensions with the app ----
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = "auth.login"       # Redirect unauthenticated users to login page
    login_manager.login_message_category = "info"  # Bootstrap alert category for flash messages

    # Import models so that SQLAlchemy can see them before creating tables
    from app import models  # noqa: F401

    # Create all database tables if they do not exist (for development simplicity)
    with app.app_context():
        db.create_all()

    # ---- Register Blueprints ----
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.history import history_bp
    from app.routes.share import share_bp
    from app.routes.account import account_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")    # /auth/login, /auth/signup, /auth/logout
    app.register_blueprint(main_bp)                        # /, /dashboard, /generate, etc.
    app.register_blueprint(history_bp, url_prefix="/history")
    app.register_blueprint(share_bp, url_prefix="/share")
    app.register_blueprint(account_bp, url_prefix="/account")

    return app