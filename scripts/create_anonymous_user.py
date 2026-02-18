#!/usr/bin/env python
"""
Create the anonymous system user for public CV access.
Run this script after database initialization.
"""
import os
import sys
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models.user import User

def create_anonymous_user():
    """Create or verify the anonymous system user exists."""
    app = create_app(os.environ.get('FLASK_ENV', 'development'))

    with app.app_context():
        # Check if anonymous user already exists
        existing_user = User.query.filter_by(email='anonymous@system.internal').first()

        if existing_user:
            print("✓ Anonymous user already exists:")
            print(f"  ID: {existing_user.id}")
            print(f"  Email: {existing_user.email}")
            print(f"  Display Name: {existing_user.display_name}")
            return

        # Create anonymous user
        anonymous_user = User(
            id=str(uuid.uuid4()),
            google_id='anonymous-system',
            email='anonymous@system.internal',
            display_name='Anonymous User',
            is_active=True,
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )

        db.session.add(anonymous_user)
        db.session.commit()

        print("✓ Anonymous system user created successfully!")
        print(f"  ID: {anonymous_user.id}")
        print(f"  Email: {anonymous_user.email}")
        print(f"  Display Name: {anonymous_user.display_name}")

if __name__ == '__main__':
    create_anonymous_user()
