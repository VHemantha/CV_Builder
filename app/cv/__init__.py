"""
CV management blueprint.
Handles dashboard, CV CRUD, builder interface, preview, and PDF export.
"""
from flask import Blueprint

bp = Blueprint("cv", __name__)

from app.cv import routes  # noqa: E402, F401
