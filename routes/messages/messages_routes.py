import os
import uuid
from datetime import datetime
from config.helpers import mail

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_cors import cross_origin
from models.messages.MessagesModel import MessageModel
from config.constants import (
    MESSAGES_COLLECTION_NAME,
    MESSAGES_DOCUMENT_ID,
    MESSAGES_REFERENCE_NAME,
)
from config.firestore.firestore_config import (
    add_document_array,
    get_document_array,
)
from config.constants import FRONT_END_URLS
from flask_mail import Message  # Import the Message class for sending emails
from flask import render_template  # Import render_template for email content


bp = Blueprint("messages", __name__)
GMAIL_DEFAULT_SENDER = os.getenv("GMAIL_DEFAULT_SENDER")



@jwt_required()
@bp.route("/api/create_message", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def create_message():
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        data = request.json

        message_data = {
            "message_id": str(uuid.uuid4()),
            "subject": data.get("subject"),
            "message": data.get("message"),
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "email": data.get("email"),
            "response": None,
        }

        message = MessageModel(**message_data).model_dump()

        success, message = add_document_array(
            MESSAGES_COLLECTION_NAME,
            MESSAGES_DOCUMENT_ID,
            MESSAGES_REFERENCE_NAME,
            message,
        )

        # New code to send an email after saving the message
        if success:
            msg = Message(
                "New Message - OSCE Buddy!",
                sender=GMAIL_DEFAULT_SENDER,
                recipients=["hello@fourintegers.com"],  # Send to the email provided in the message
            )
            msg.html = render_template(
                "new_message_email.html",  # Assuming you have an email template
                subject=data.get("subject"),
                message=data.get("message"),
                email=data.get("email"),
                received_at=datetime.utcnow().isoformat(),
            )
            mail.send(msg)  # Send the email

        return jsonify({"message": "Message created successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@jwt_required()
@bp.route("/api/get_messages", methods=["GET", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def get_messages():
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        success, messages = get_document_array(
            MESSAGES_COLLECTION_NAME,
            MESSAGES_DOCUMENT_ID,
            MESSAGES_REFERENCE_NAME,
            filters={"created_by": user_id},
        )
        if not success:
            return jsonify({"error": messages}), 404
        return jsonify({"messages": messages}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
