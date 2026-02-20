"""
CV Builder Flask Application Factory.
Creates and configures the Flask application with all extensions and blueprints.
"""
import os
import logging
from flask import Flask, render_template, jsonify
from app.config import config
from app.extensions import db, migrate, login_manager, csrf, talisman, limiter, cache


def create_app(config_name=None):
    """
    Application factory pattern.

    Args:
        config_name: Configuration to use ('development', 'testing', 'production')
                    Defaults to FLASK_ENV environment variable or 'development'

    Returns:
        Configured Flask application instance
    """
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize logging
    configure_logging(app)

    # Initialize extensions
    initialize_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Register CLI commands
    register_cli_commands(app)

    # Initialize Sentry (if configured)
    initialize_sentry(app)

    # Log startup info
    app.logger.info(
        f"CV Builder starting in {config_name} mode - {app.config['APP_BASE_URL']}"
    )

    return app


def configure_logging(app):
    """Configure application logging."""
    import logging
    import logging.config

    if app.config.get("FLASK_ENV") == "production":
        # Production: JSON structured logging
        logging.config.dictConfig(
            {
                "version": 1,
                "formatters": {
                    "default": {
                        "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "default",
                        "stream": "ext://sys.stdout",
                    }
                },
                "root": {"level": "INFO", "handlers": ["console"]},
            }
        )
    else:
        # Development: Simple console logging
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        )


def initialize_extensions(app):
    """Initialize Flask extensions."""
    # Database
    db.init_app(app)
    migrate.init_app(app, db)

    # Authentication
    login_manager.init_app(app)

    # OAuth
    from app.auth.oauth import init_oauth
    init_oauth(app)

    # Security
    csrf.init_app(app)

    # Only enable Talisman in production or if explicitly requested
    if app.config.get("TALISMAN_FORCE_HTTPS"):
        talisman.init_app(
            app,
            content_security_policy=app.config["TALISMAN_CONTENT_SECURITY_POLICY"],
            force_https=True,
        )

    # Rate limiting
    limiter.init_app(app)

    # Caching
    cache.init_app(app)

    # User loader for Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)


def register_blueprints(app):
    """Register Flask blueprints."""
    # Import blueprints
    from app.auth import bp as auth_bp
    from app.cv import bp as cv_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cv_bp, url_prefix="/cv")

    # Root route - SEO optimized landing page
    @app.route("/")
    def index():
        """SEO-optimized landing page for search engines."""
        return render_template("landing/index.html")

    # Sitemap for SEO
    @app.route("/sitemap.xml")
    def sitemap():
        """Generate dynamic sitemap for search engines."""
        from flask import make_response
        from datetime import datetime

        pages = [
            {"loc": "/", "changefreq": "daily", "priority": "1.0"},
            {"loc": "/cv/dashboard", "changefreq": "daily", "priority": "0.9"},
            {"loc": "/auth/google", "changefreq": "monthly", "priority": "0.7"},
        ]

        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

        for page in pages:
            sitemap_xml += "  <url>\n"
            sitemap_xml += f"    <loc>{app.config['APP_BASE_URL']}{page['loc']}</loc>\n"
            sitemap_xml += f"    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>\n"
            sitemap_xml += f"    <changefreq>{page['changefreq']}</changefreq>\n"
            sitemap_xml += f"    <priority>{page['priority']}</priority>\n"
            sitemap_xml += "  </url>\n"

        sitemap_xml += "</urlset>"

        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response

    # Robots.txt for SEO
    @app.route("/robots.txt")
    def robots():
        """Generate robots.txt for search engine crawlers."""
        from flask import make_response

        robots_txt = f"""User-agent: *
Allow: /
Allow: /cv/dashboard
Disallow: /cv/*/edit
Disallow: /cv/*/preview
Disallow: /cv/*/download
Disallow: /auth/
Disallow: /api/

Sitemap: {app.config['APP_BASE_URL']}/sitemap.xml
"""
        response = make_response(robots_txt)
        response.headers["Content-Type"] = "text/plain"
        return response

    # ads.txt for Google AdSense
    @app.route("/ads.txt")
    def ads_txt():
        """Serve ads.txt for Google AdSense verification."""
        from flask import make_response

        content = "google.com, pub-9172775909086222, DIRECT, f08c47fec0942fa0\n"
        response = make_response(content)
        response.headers["Content-Type"] = "text/plain"
        return response

    # Health check endpoint (for Docker/Render)
    @app.route("/health")
    @limiter.exempt
    def health():
        """Health check endpoint for monitoring."""
        from sqlalchemy import text

        try:
            # Check database connection
            db.session.execute(text("SELECT 1"))
            db_status = "ok"
        except Exception as e:
            app.logger.error(f"Database health check failed: {e}")
            db_status = "error"

        try:
            # Check Redis connection
            cache.set("health_check", "ok", timeout=5)
            redis_status = "ok" if cache.get("health_check") == "ok" else "error"
        except Exception as e:
            app.logger.error(f"Redis health check failed: {e}")
            redis_status = "error"

        status_code = 200 if db_status == "ok" and redis_status == "ok" else 503

        return (
            jsonify(
                {
                    "status": "ok" if status_code == 200 else "degraded",
                    "database": db_status,
                    "redis": redis_status,
                }
            ),
            status_code,
        )


def register_error_handlers(app):
    """Register custom error handlers."""

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Internal error: {error}")
        return render_template("errors/500.html"), 500

    @app.errorhandler(429)
    def ratelimit_handler(error):
        return render_template("errors/429.html"), 429


def register_cli_commands(app):
    """Register custom Flask CLI commands."""

    @app.cli.command()
    def seed_templates():
        """Seed the database with CV templates."""
        from scripts.seed_templates import seed

        seed()
        app.logger.info("Templates seeded successfully!")

    @app.cli.command()
    def create_db():
        """Create database tables."""
        db.create_all()
        app.logger.info("Database tables created!")


def initialize_sentry(app):
    """Initialize Sentry error tracking if configured."""
    sentry_dsn = app.config.get("SENTRY_DSN")
    if sentry_dsn and app.config.get("FLASK_ENV") == "production":
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration

            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[FlaskIntegration()],
                traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
                environment=app.config.get("FLASK_ENV", "development"),
            )
            app.logger.info("Sentry initialized successfully")
        except ImportError:
            app.logger.warning("Sentry SDK not installed, skipping initialization")
