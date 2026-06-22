# app/routes/account.py – User account settings (change password, delete account).

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.forms import ChangePasswordForm, DeleteAccountForm

account_bp = Blueprint("account", __name__, template_folder="../templates")

@account_bp.route("/", methods=["GET", "POST"])
@login_required
def account_settings():
    """Display and handle account settings forms."""
    pw_form = ChangePasswordForm()
    del_form = DeleteAccountForm()

    if pw_form.validate_on_submit() and "update_password" in request.form:
        # Verify current password
        if not check_password_hash(current_user.password_hash, pw_form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.password_hash = generate_password_hash(pw_form.new_password.data)
            db.session.commit()
            flash("Password updated successfully.", "success")
        return redirect(url_for("account.account_settings"))

    if del_form.validate_on_submit() and "delete_account" in request.form:
        # Delete the user and all associated data
        user = current_user._get_current_object()
        logout_user()  # log out before deletion
        db.session.delete(user)
        db.session.commit()
        flash("Your account has been permanently deleted.", "info")
        return redirect(url_for("main.landing"))

    return render_template("account.html", pw_form=pw_form, del_form=del_form)