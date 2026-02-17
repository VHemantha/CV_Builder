"""
Authentication blueprint.
Handles Google OAuth login, logout, and user session management.
"""
from flask import Blueprint

bp = Blueprint("auth", __name__)

from app.auth import routes  # noqa: E402, F401
