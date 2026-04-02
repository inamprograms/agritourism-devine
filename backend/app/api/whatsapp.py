from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from app.services.ai_chat_service import chat_service

whatsapp_bp = Blueprint("whatsapp", __name__)

@whatsapp_bp.route("/whatsapp/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "anonymous")
    
    try:
        response_text = chat_service.chat(
            message=incoming_msg,
            history=[],
            language="en",
            session_id=sender,
            source="whatsapp"
        )
    except ValueError as e:
        response_text = str(e)
    except Exception:
        response_text = "Sorry, something went wrong. Please try again."
    
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp), 200, {"Content-Type": "text/xml"}