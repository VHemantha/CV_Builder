"""
CV Section model.
Flexible JSONB storage for different section types.
"""
from datetime import datetime
from app.extensions import db
import uuid


class CVSection(db.Model):
    """CV section with flexible JSON content."""

    __tablename__ = "cv_sections"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cv_id = db.Column(db.String(36), db.ForeignKey("cvs.id"), nullable=False, index=True)
    section_type = db.Column(db.String(50), nullable=False)  # 'experience', 'education', etc.
    label = db.Column(db.String(255))  # Custom label override
    content = db.Column(db.JSON, nullable=False)  # Flexible section data
    display_order = db.Column(db.Integer, default=0, nullable=False)
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    cv = db.relationship("CV", back_populates="sections")

    def __repr__(self):
        return f"<CVSection {self.section_type}>"

    def to_dict(self):
        """Serialize section to dictionary."""
        return {
            "id": self.id,
            "section_type": self.section_type,
            "label": self.label,
            "content": self.content,
            "display_order": self.display_order,
            "is_visible": self.is_visible,
        }
