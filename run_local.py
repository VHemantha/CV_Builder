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
        print("   2. Set Google OAuth credentials in .env")
        print("\n✋  Press Ctrl+C to stop the server\n")

    # Run the development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
