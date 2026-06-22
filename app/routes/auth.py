# app/routes/auth.py – Authentication routes (login, signup, logout).
# Uses Flask Blueprint, Flask-WTF forms, and Werkzeug password hashing.

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app.forms import LoginForm, SignupForm

auth_bp = Blueprint("auth", __name__, template_folder="../templates")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Log in an existing user."""
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        # Look up the user by email
        user = User.query.filter_by(email=form.email.data).first()
        # Check password hash
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Logged in successfully!", "success")
            # Redirect to the page the user originally wanted (if any)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.dashboard"))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Register a new user account."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = SignupForm()
    if form.validate_on_submit():
        # Hash the password before storing
        hashed_pw = generate_password_hash(form.password.data)
        user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            password_hash=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("signup.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current user and clear session."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.landing"))