# app/models.py – SQLAlchemy database models for InterviewGenie.
# Defines User, ChatHistory, and SharedLink tables.

from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timedelta
import uuid

# Flask-Login user loader – required to reload user from session
@login_manager.user_loader
def load_user(user_id):
    """Load a user from the database given their ID."""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """Represents a registered user."""
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)             # User's full name
    email = db.Column(db.String(150), unique=True, nullable=False)    # Unique email
    password_hash = db.Column(db.String(256), nullable=False)         # Hashed password
    created_at = db.Column(db.DateTime, default=datetime.utcnow)      # Registration timestamp

    # One user can have many chat histories
    chats = db.relationship("ChatHistory", backref="author", lazy=True)

class ChatHistory(db.Model):
    """Stores a set of generated interview Q&A."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    job_description = db.Column(db.Text, nullable=True)
    company_profile = db.Column(db.Text, nullable=True)
    responsibilities = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    # Complete Q&A JSON stored as text
    full_generated_output = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Optional nickname for the saved chat
    title = db.Column(db.String(200), nullable=True)

class SharedLink(db.Model):
    """Public share link that expires after 7 days."""
    id = db.Column(db.Integer, primary_key=True)
    chat_history_id = db.Column(db.Integer, db.ForeignKey("chat_history.id"), nullable=False)
    token = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    expires_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(days=7))
    # Relationship to the original chat
    chat = db.relationship("ChatHistory", backref="shared_links")

    def is_expired(self):
        """Check if the share link has expired."""
        return datetime.utcnow() > self.expires_at