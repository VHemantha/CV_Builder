"""
Application configuration classes.
Supports Development, Testing, and Production environments.
"""
import os
from datetime import timedelta


class Config:
    """Base configuration with common settings."""

    # Flask core
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    FLASK_APP = os.environ.get("FLASK_APP", "app:create_app")
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")

    # Application settings
    APP_NAME = "CV Builder"
    APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5000")

    # Flask URL generation settings
    # Extract domain from APP_BASE_URL for SERVER_NAME
    from urllib.parse import urlparse
    _parsed_url = urlparse(APP_BASE_URL)
    SERVER_NAME = _parsed_url.netloc if _parsed_url.netloc else None
    PREFERRED_URL_SCHEME = _parsed_url.scheme or 'https'

    # Database - Force SQLite (override PostgreSQL if present)
    db_url = os.environ.get("DATABASE_URL", "sqlite:///cv_builder.db")

    # Force SQLite: Replace any PostgreSQL URL with SQLite
    if db_url and "postgres" in db_url:
        db_url = "sqlite:///cv_builder.db"
        print("⚠️ PostgreSQL URL detected - forcing SQLite for compatibility")

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Engine options - only use pooling for PostgreSQL
    if "sqlite" not in db_url:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_size": 10,
            "max_overflow": 20,
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": False,
        }

    # Redis (for caching and rate limiting)
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Session configuration
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_REFRESH_EACH_REQUEST = True

    # WTForms / CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # CSRF tokens don't expire

    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

    # File upload limits (not used in v1, but good to have)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size

    # Rate limiting (use in-memory if Redis not available)
    RATELIMIT_STORAGE_URL = REDIS_URL if REDIS_URL else "memory://"
    RATELIMIT_STRATEGY = "fixed-window"
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_ENABLED = bool(REDIS_URL)  # Disable if no Redis

    # Flask-Caching (use simple cache if Redis not available)
    CACHE_TYPE = "RedisCache" if REDIS_URL else "SimpleCache"
    CACHE_REDIS_URL = REDIS_URL if REDIS_URL else None
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes

    # Feature flags
    MAX_CVS_PER_USER = int(os.environ.get("MAX_CVS_PER_USER", "10"))
    DOWNLOAD_RATE_LIMIT = os.environ.get("DOWNLOAD_RATE_LIMIT", "5/hour")
    AI_ASSIST_ENABLED = os.environ.get("AI_ASSIST_ENABLED", "false").lower() == "true"
    AI_CALLS_PER_DAY = int(os.environ.get("AI_CALLS_PER_DAY", "10"))

    # OpenAI (optional)
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    # Security
    IP_HASH_SALT = os.environ.get("IP_HASH_SALT", "dev-salt-change-me")

    # Monitoring
    SENTRY_DSN = os.environ.get("SENTRY_DSN")

    # Flask-Talisman (CSP and security headers)
    TALISMAN_FORCE_HTTPS = os.environ.get("FLASK_ENV") == "production"
    TALISMAN_CONTENT_SECURITY_POLICY = {
        "default-src": "'self'",
        "script-src": ["'self'", "'unsafe-inline'"],  # For inline preview scripts
        "style-src": ["'self'", "'unsafe-inline'"],  # For dynamic styles
        "img-src": ["'self'", "data:", "https://lh3.googleusercontent.com"],  # Google profile pics
        "font-src": "'self'",
        "connect-src": "'self'",
        "frame-ancestors": "'none'",
    }


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO", "false").lower() == "true"

    # Disable HTTPS requirement for local development
    TALISMAN_FORCE_HTTPS = False

    # Allow OAuth over HTTP in development
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = os.environ.get(
        "OAUTHLIB_INSECURE_TRANSPORT", "1"
    )


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False  # Disable CSRF in tests

    # Use in-memory SQLite for fast tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # Use simple cache for testing
    CACHE_TYPE = "SimpleCache"

    # Disable rate limiting in tests
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False

    # Enforce HTTPS
    TALISMAN_FORCE_HTTPS = True
    SESSION_COOKIE_SECURE = True

    # Ensure critical env vars are set
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Assert critical production settings
        assert os.environ.get("SECRET_KEY"), "SECRET_KEY must be set in production!"
        assert os.environ.get(
            "DATABASE_URL"
        ), "DATABASE_URL must be set in production!"
        assert os.environ.get(
            "GOOGLE_CLIENT_ID"
        ), "GOOGLE_CLIENT_ID must be set in production!"
        assert os.environ.get(
            "GOOGLE_CLIENT_SECRET"
        ), "GOOGLE_CLIENT_SECRET must be set in production!"

        # Ensure OAUTHLIB_INSECURE_TRANSPORT is not set
        if os.environ.get("OAUTHLIB_INSECURE_TRANSPORT") == "1":
            raise RuntimeError(
                "OAUTHLIB_INSECURE_TRANSPORT=1 is not allowed in production!"
            )


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
