"""
Pytest configuration and fixtures.
"""
import pytest
from app import create_app
from app.extensions import db as _db
from app.models import User, CV, CVSection


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    app = create_app("testing")
    return app


@pytest.fixture(scope="session")
def _database(app):
    """Create database for testing."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(scope="function")
def db(_database, app):
    """Create a new database session for each test."""
    with app.app_context():
        # Begin a nested transaction
        connection = _database.engine.connect()
        transaction = connection.begin()

        # Bind session to connection
        options = dict(bind=connection, binds={})
        session = _database.create_scoped_session(options=options)
        _database.session = session

        yield _database

        # Rollback transaction and close connection
        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture
def client(app, db):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def user(db):
    """Create a test user."""
    user = User(
        google_id="test-google-id-123",
        email="test@example.com",
        display_name="Test User",
        photo_url="https://example.com/photo.jpg",
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def cv(db, user):
    """Create a test CV."""
    cv = CV(
        user_id=user.id,
        title="Test CV",
        template_slug="ats_clean",
        primary_color="#4285f4",
    )
    db.session.add(cv)
    db.session.commit()
    return cv


@pytest.fixture
def authenticated_client(client, user):
    """Create an authenticated test client."""
    with client.session_transaction() as session:
        session["user_id"] = user.id
    return client
