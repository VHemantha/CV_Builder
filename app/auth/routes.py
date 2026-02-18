"""
Authentication routes - login, register, logout.
"""
from datetime import datetime
from flask import redirect, url_for, flash, request, render_template
from flask_login import login_user, logout_user, current_user
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.extensions import db
from app.models.user import User
import uuid


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle login - both GET (show form) and POST (process form)."""
    if current_user.is_authenticated:
        return redirect(url_for("cv.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'error')
            return redirect(url_for('auth.login'))

        # Log user in
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()

        flash(f'Welcome back, {user.display_name}!', 'success')

        # Redirect to intended page or dashboard
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('cv.dashboard'))

    return render_template('auth/login.html', form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for("cv.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=form.email.data.lower(),
            display_name=form.display_name.data,
            is_active=True,
            created_at=datetime.utcnow()
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        # Auto-login after registration
        login_user(user)

        flash(f'Welcome to CV Builder, {user.display_name}!', 'success')
        return redirect(url_for('cv.dashboard'))

    return render_template('auth/register.html', form=form)


@bp.route("/logout")
def logout():
    """Log out the current user."""
    if current_user.is_authenticated:
        user_name = current_user.display_name
        logout_user()
        flash(f'Goodbye, {user_name}! You have been logged out successfully.', 'success')
    return redirect(url_for("index"))


# Google OAuth routes remain disabled
@bp.route("/google")
def google_login():
    """Redirect to regular login (Google OAuth disabled)."""
    flash('Please use email/password to sign in.', 'info')
    return redirect(url_for("auth.login"))


@bp.route("/callback")
def google_callback():
    """Redirect to regular login (Google OAuth disabled)."""
    return redirect(url_for("auth.login"))
