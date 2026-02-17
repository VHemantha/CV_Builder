"""
Authentication routes.
Google OAuth2 login flow and logout.
"""
from datetime import datetime
from flask import redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user
from app.auth import bp
from app.auth.oauth import oauth
from app.extensions import db
from app.models.user import User


@bp.route("/login")
def login():
    """Display login page with Google OAuth button."""
    if current_user.is_authenticated:
        return redirect(url_for("cv.dashboard"))

    # Redirect to index which shows the login template
    return redirect(url_for("index"))


@bp.route("/google")
def google_login():
    """Redirect to Google OAuth2 authorization."""
    # Generate redirect URI
    redirect_uri = url_for("auth.google_callback", _external=True)

    # Redirect to Google OAuth
    return oauth.google.authorize_redirect(redirect_uri)


@bp.route("/callback")
def google_callback():
    """Handle Google OAuth2 callback."""
    try:
        # Exchange authorization code for access token
        token = oauth.google.authorize_access_token()

        # Get user info from Google
        user_info = token.get('userinfo')

        if not user_info:
            flash("Failed to get user information from Google.", "error")
            return redirect(url_for("index"))

        # Extract user data
        google_id = user_info.get('sub')
        email = user_info.get('email')
        display_name = user_info.get('name')
        photo_url = user_info.get('picture')

        if not google_id or not email:
            flash("Incomplete user information from Google.", "error")
            return redirect(url_for("index"))

        # Find or create user
        user = User.query.filter_by(google_id=google_id).first()

        if user:
            # Update existing user
            user.email = email
            user.display_name = display_name
            user.photo_url = photo_url
            user.last_login = datetime.utcnow()
        else:
            # Create new user
            user = User(
                google_id=google_id,
                email=email,
                display_name=display_name,
                photo_url=photo_url,
                last_login=datetime.utcnow()
            )
            db.session.add(user)

        db.session.commit()

        # Log the user in
        login_user(user, remember=True)

        flash(f"Welcome, {user.display_name}!", "success")

        # Redirect to intended page or dashboard
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for("cv.dashboard"))

    except Exception as e:
        db.session.rollback()
        flash(f"Authentication failed: {str(e)}", "error")
        return redirect(url_for("index"))


@bp.route("/logout")
def logout():
    """Log out the current user."""
    user_name = current_user.display_name if current_user.is_authenticated else "User"
    logout_user()
    flash(f"Goodbye, {user_name}! You have been logged out successfully.", "success")
    return redirect(url_for("index"))
