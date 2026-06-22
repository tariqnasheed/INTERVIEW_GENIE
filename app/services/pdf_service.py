# app/services/pdf_service.py – Generate PDF from ChatHistory using WeasyPrint.

from flask import render_template, abort
from weasyprint import HTML
import logging

logger = logging.getLogger(__name__)

def generate_pdf(chat_history, user_full_name):
    """
    Renders an HTML template with Q&A data and converts it to PDF bytes.
    Returns bytes of PDF content.
    """
    import json
    try:
        qa_data = json.loads(chat_history.full_generated_output)
    except Exception as e:
        logger.error(f"Invalid JSON in chat_history {chat_history.id}: {e}")
        qa_data = []

    try:
        html_content = render_template(
            "pdf_template.html",
            title=chat_history.title or "Interview Q&A",
            user_name=user_full_name,
            date=chat_history.created_at.strftime("%Y-%m-%d"),
            questions=qa_data
        )
        # Generate PDF using WeasyPrint
        pdf = HTML(string=html_content).write_pdf()
        return pdf
    except Exception as e:
        logger.exception("PDF generation failed")
        # Fallback: abort with a clear error message
        from flask import make_response
        error_msg = f"PDF generation error: {str(e)}"
        response = make_response(error_msg, 500)
        response.headers["Content-Type"] = "text/plain"
        return response