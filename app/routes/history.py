# app/routes/history.py – Routes for viewing and managing saved chat history.

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import ChatHistory
import json

history_bp = Blueprint("history", __name__, template_folder="../templates")

@history_bp.route("/")
@login_required
def history():
    """Display all saved chats for the current user, with optional search."""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    query = ChatHistory.query.filter_by(user_id=current_user.id)
    if search:
        # Search in title or input fields
        like_expr = f"%{search}%"
        query = query.filter(
            db.or_(
                ChatHistory.title.ilike(like_expr),
                ChatHistory.job_description.ilike(like_expr),
                ChatHistory.company_profile.ilike(like_expr)
            )
        )
    # Order by most recent first and paginate (10 per page)
    chats = query.order_by(ChatHistory.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template("history.html", chats=chats, search=search)

@history_bp.route("/view/<int:chat_id>")
@login_required
def view_chat(chat_id):
    """Load a specific saved chat and display it with full actions."""
    chat = ChatHistory.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
    qa_data = json.loads(chat.full_generated_output)
    return render_template("dashboard.html", chat=chat, qa_data=qa_data, view_only=False)

@history_bp.route("/rename/<int:chat_id>", methods=["POST"])
@login_required
def rename_chat(chat_id):
    """Rename a saved history item."""
    chat = ChatHistory.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
    new_title = request.form.get("title", "").strip()
    if not new_title:
        flash("Title cannot be empty.", "warning")
    else:
        chat.title = new_title
        db.session.commit()
        flash("History renamed successfully.", "success")
    return redirect(url_for("history.history"))

@history_bp.route("/delete/<int:chat_id>", methods=["POST"])
@login_required
def delete_chat(chat_id):
    """Delete a saved history entry."""
    chat = ChatHistory.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
    db.session.delete(chat)
    db.session.commit()
    flash("History item deleted.", "info")
    return redirect(url_for("history.history"))