# app/routes/share.py – Public share view (no login required).

from flask import Blueprint, render_template, abort
from app.models import SharedLink, ChatHistory
import json
from datetime import datetime

share_bp = Blueprint("share", __name__, template_folder="../templates")

@share_bp.route("/<token>")
def view_shared(token):
    """
    Publicly view a shared Q&A set using its unique token.
    If the link is expired, show an error.
    """
    link = SharedLink.query.filter_by(token=token).first_or_404()
    # Check expiration
    if link.is_expired():
        return render_template("view_shared.html", expired=True), 410  # Gone
    chat = ChatHistory.query.get(link.chat_history_id)
    if not chat:
        abort(404)
    qa_data = json.loads(chat.full_generated_output)
    return render_template("view_shared.html", qa_data=qa_data, chat=chat, expired=False)