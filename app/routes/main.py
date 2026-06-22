# app/routes/main.py – Core routes: landing page, dashboard, generation, saving, sharing, PDF.

from flask import Blueprint, render_template, request, jsonify, current_app, url_for, flash, redirect
from flask_login import login_required, current_user
from app import db
from app.models import ChatHistory, SharedLink
from app.services.ai_service import generate_interview_questions
from app.services.pdf_service import generate_pdf
from app.forms import SaveChatForm
import json
import logging
from datetime import datetime, timedelta
import uuid

main_bp = Blueprint("main", __name__, template_folder="../templates")
logger = logging.getLogger(__name__)

@main_bp.route("/")
def landing():
    """Landing/hero page for unauthenticated users."""
    return render_template("landing.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard where users can input job details and generate Q&A."""
    # Provide an empty form for CSRF protection (used by AJAX save later)
    form = SaveChatForm()
    return render_template("dashboard.html", form=form)

@main_bp.route("/generate", methods=["POST"])
@login_required
def generate():
    """
    AJAX endpoint that receives job details and returns generated Q&A JSON.
    Expected JSON payload:
        job_description, company_profile, responsibilities, requirements
    Returns JSON object with 'success' and 'data' (the Q&A array) or 'error'.
    """
    # Parse JSON data from the request
    req_data = request.get_json()
    if not req_data:
        return jsonify({"success": False, "error": "No data provided."}), 400

    job_desc = req_data.get("job_description", "")
    company = req_data.get("company_profile", "")
    resp = req_data.get("responsibilities", "")
    reqs = req_data.get("requirements", "")

    # Basic validation: at least one field should be filled
    if not any([job_desc, company, resp, reqs]):
        return jsonify({"success": False, "error": "Please fill at least one field."}), 400

    try:
        # Call the AI service to generate questions
        qa_data = generate_interview_questions(job_desc, company, resp, reqs)
        # Return the structured JSON to the frontend
        return jsonify({"success": True, "data": qa_data})
    except ValueError as e:
        # Handle JSON parsing / validation errors from the AI service
        logger.exception("Generation value error")
        return jsonify({"success": False, "error": f"AI response invalid: {str(e)}"}), 500
    except Exception as e:
        # Catch API errors, token limits, etc. and return the real message
        logger.exception("Generation error")
        msg = str(e)
        # If it’s an OpenAI/Groq API error, extract the meaningful message from the response body
        if hasattr(e, 'body'):
            try:
                msg = e.body.get('error', {}).get('message', msg)
            except:
                pass
        return jsonify({"success": False, "error": f"AI generation failed: {msg}"}), 500

@main_bp.route("/save_chat", methods=["POST"])
@login_required
def save_chat():
    """
    Save the currently generated Q&A (sent as JSON) along with input fields
    to the user's history. Returns the new chat ID.
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data."}), 400

    qa_data = data.get("qa_data")   # the array of Q&A objects
    if not qa_data:
        return jsonify({"success": False, "error": "No Q&A data to save."}), 400

    # Create a new ChatHistory record
    chat = ChatHistory(
        user_id=current_user.id,
        job_description=data.get("job_description", ""),
        company_profile=data.get("company_profile", ""),
        responsibilities=data.get("responsibilities", ""),
        requirements=data.get("requirements", ""),
        full_generated_output=json.dumps(qa_data),  # store as JSON string
        title=data.get("title", "")  # optional title
    )
    db.session.add(chat)
    db.session.commit()

    return jsonify({"success": True, "chat_id": chat.id})

@main_bp.route("/share_chat/<int:chat_id>", methods=["POST"])
@login_required
def share_chat(chat_id):
    """
    Create a public share link for a saved chat.
    Returns the share URL.
    """
    chat = ChatHistory.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
    # Create a new SharedLink with a unique token and 7-day expiry
    token = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(days=7)
    link = SharedLink(chat_history_id=chat.id, token=token, expires_at=expires)
    db.session.add(link)
    db.session.commit()
    share_url = url_for("share.view_shared", token=token, _external=True)
    return jsonify({"success": True, "share_url": share_url})

@main_bp.route("/download_pdf/<int:chat_id>")
@login_required
def download_pdf(chat_id):
    """
    Generate and return a PDF for a saved chat.
    """
    chat = ChatHistory.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
    pdf_bytes = generate_pdf(chat, current_user.full_name)
    # Create response with PDF content
    from flask import make_response
    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=interview_qa_{chat_id}.pdf"
    return response