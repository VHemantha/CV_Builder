"""
CV model.
"""
from datetime import datetime
from app.extensions import db
import uuid


class CV(db.Model):
    """User's CV/Resume."""

    __tablename__ = "cvs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    template_slug = db.Column(db.String(50), nullable=False, default="ats_clean")
    primary_color = db.Column(db.String(7))  # Hex color code
    font_pair = db.Column(db.String(50))
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="cvs")
    sections = db.relationship("CVSection", back_populates="cv", lazy="dynamic", cascade="all, delete-orphan", order_by="CVSection.display_order")

    def __repr__(self):
        return f"<CV {self.title}>"

    def soft_delete(self):
        """Soft delete the CV."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        """Serialize CV to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "template_slug": self.template_slug,
            "primary_color": self.primary_color,
            "font_pair": self.font_pair,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "sections": [section.to_dict() for section in self.sections],
        }
