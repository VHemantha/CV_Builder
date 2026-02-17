"""
Download log model for audit trail.
"""
from datetime import datetime
from app.extensions import db
import uuid
import hashlib


class DownloadLog(db.Model):
    """Audit log for CV downloads."""

    __tablename__ = "download_logs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cv_id = db.Column(db.String(36), db.ForeignKey("cvs.id"), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    ip_hash = db.Column(db.String(64), nullable=False)  # SHA-256 hash of IP
    cv_title = db.Column(db.String(255), nullable=False)  # Snapshot of title
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<DownloadLog {self.cv_title} at {self.downloaded_at}>"

    @staticmethod
    def hash_ip(ip_address, salt):
        """Hash IP address for privacy."""
        return hashlib.sha256(f"{ip_address}{salt}".encode()).hexdigest()

    @classmethod
    def create_log(cls, cv, user, ip_address, salt):
        """Create a download log entry."""
        log = cls(
            cv_id=cv.id,
            user_id=user.id,
            ip_hash=cls.hash_ip(ip_address, salt),
            cv_title=cv.title,
        )
        db.session.add(log)
        db.session.commit()
        return log
