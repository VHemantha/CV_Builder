#!/usr/bin/env python
"""
Local development server runner.
Run this instead of docker-compose for local development.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app
from app.extensions import db

# Create the Flask app
app = create_app('development')

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database initialized!")

        # Create anonymous user for public access
        print("\nCreating anonymous system user...")
        try:
            from app.models.user import User
            import uuid
            from datetime import datetime

            # Check if anonymous user exists
            existing_user = User.query.filter_by(email='anonymous@system.internal').first()
            if not existing_user:
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
                print("✓ Anonymous user created!")
            else:
                print("✓ Anonymous user already exists!")
        except Exception as e:
            print(f"Note: Anonymous user creation skipped ({e})")

        # Run seed script
        print("\nSeeding templates...")
        try:
            from scripts.seed_templates import seed
            seed()
            print("✓ Templates seeded!")
        except Exception as e:
            print(f"Note: Template seeding skipped ({e})")

        print("\n" + "="*50)
        print("🚀 CV Builder is starting!")
        print("="*50)
        print("\n📍 Open your browser to: http://localhost:5000")
        print("\n⚠️  Make sure you've:")
        print("   1. Activated virtual environment: .\\venv\\Scripts\\activate")
        print("\n🎉 No sign-in required! Start building CVs immediately.")
        print("\n✋  Press Ctrl+C to stop the server\n")

    # Run the development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
