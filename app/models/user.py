"""
User model for authentication.
"""
from datetime import datetime
from flask_login import UserMixin
from app.extensions import db
import uuid


class User(UserMixin, db.Model):
    """User account from Google OAuth."""

    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    google_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(255))
    photo_url = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

    # Relationships
    cvs = db.relationship("CV", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def cv_count(self):
        """Get count of active (non-deleted) CVs."""
        return self.cvs.filter_by(is_deleted=False).count()

    def can_create_cv(self, max_limit):
        """Check if user can create more CVs."""
        return self.cv_count < max_limit
