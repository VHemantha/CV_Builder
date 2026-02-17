"""
Google OAuth2 configuration using Authlib.
"""
from authlib.integrations.flask_client import OAuth

oauth = OAuth()


def init_oauth(app):
    """Initialize OAuth with Google configuration."""
    oauth.init_app(app)

    # Register Google OAuth provider
    oauth.register(
        name='google',
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile',
            'prompt': 'select_account'  # Allow user to select which Google account
        }
    )

    return oauth
