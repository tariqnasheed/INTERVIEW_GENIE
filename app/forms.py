# app/forms.py – WTForm definitions with validators and CSRF protection.

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")

class SignupForm(FlaskForm):
    """Form for new user registration."""
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long.")
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(),
        EqualTo("password", message="Passwords must match.")
    ])
    submit = SubmitField("Sign Up")

    # Custom validator to ensure email is not already registered
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is already in use. Please choose a different one.")

class ChangePasswordForm(FlaskForm):
    """Form for changing password in account settings."""
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[
        DataRequired(),
        Length(min=8, message="New password must be at least 8 characters.")
    ])
    confirm_new_password = PasswordField("Confirm New Password", validators=[
        DataRequired(),
        EqualTo("new_password", message="Passwords must match.")
    ])
    submit = SubmitField("Update Password")

class DeleteAccountForm(FlaskForm):
    """Simple confirmation form for account deletion."""
    submit = SubmitField("Delete My Account")

class SaveChatForm(FlaskForm):
    """Form to save a generated chat (CSRF only, no visible fields)."""
    # Hidden fields are not needed because we will send JSON via AJAX.
    pass