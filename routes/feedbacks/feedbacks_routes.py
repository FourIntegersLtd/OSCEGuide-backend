from datetime import datetime
import uuid
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from config.constants import (
    FRONT_END_URLS,
    FEEDBACKS_COLLECTION_NAME,
    FEEDBACKS_DOCUMENT_ID,
    FEEDBACKS_REFERENCE_NAME,
    USERS_COLLECTION_NAME,
    USERS_DOCUMENT_ID,
    USERS_REFERENCE_NAME,   
)
from config.prompts import FEEDBACK_PROMPT
from config.helpers import format_transcript
from models.users.UserModel import StationProgress
from models.feedbacks.FeedbackModel import FeedbackResponse, ExtendedFeedbackResponse
from config.ai_clients.aiclients_config import (
    instructor_anthropic_ai_client,
    instructor_open_ai_client,
)
from config.firestore.firestore_config import add_document_array, get_document_array, update_document_array
from flask_jwt_extended import jwt_required

bp = Blueprint("feedbacks", __name__)

@jwt_required()
@bp.route("/api/generate_feedback", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def feedback_api():
    try:
        data = request.get_json()
        if not data or "transcript" not in data:
            return jsonify({"error": "Missing transcript in request body"}), 400

        transcript = data["transcript"]
        formatted_transcript = format_transcript(transcript)

        formatted_prompt = FEEDBACK_PROMPT.format(transcript=formatted_transcript)
        messages = [
            {
                "role": "system",
                "content": """You are an expert medical examination evaluator assessing doctor-patient interactions.""",
            },
            {"role": "user", "content": formatted_prompt},
        ]

        response = instructor_anthropic_ai_client.messages.create(
            response_model=FeedbackResponse,
            model="claude-3-5-sonnet-latest",
            messages=messages,
            max_tokens=5000,
            temperature=0,
            max_retries=3,
        )

        return jsonify({"feedback": response.model_dump()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

  # This ensures only authenticated users can access this endpoint


@jwt_required()
@bp.route("/api/add_feedback_to_db", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def add_feedback():
    try:
        data = request.get_json()

        feedback = data["feedback"]
        feedback_id = f"feedback_{str(uuid.uuid4())}"
        user_id = data["user_id"]
        station_id = data["station_id"]

        # Create and add feedback
        feedback_response = ExtendedFeedbackResponse(
            **feedback,
            feedback_id=feedback_id,
            user_id=user_id,
            mock_id=data["mock_id"],
            station_id=station_id,
            evaluated_by=data["evaluated_by"],
            created_at=datetime.now().isoformat(),
        )

        feedback_dict = feedback_response.model_dump()

        # Add feedback to database
        success, feedback_result = add_document_array(
            collection_name=FEEDBACKS_COLLECTION_NAME,
            document_id=FEEDBACKS_DOCUMENT_ID,
            reference_name=FEEDBACKS_REFERENCE_NAME,
            new_item=feedback_dict,
        )

        if not success:
            return jsonify({"error": feedback_result}), 400

        # Fetch user by user_id
        user_result = get_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            filters={"user_id": user_id},
        )

        # Proper error handling for user fetch
        if not user_result[0] or not user_result[1]:
            return jsonify({"error": "User not found"}), 404

        user_object = user_result[1][0]  # Get the user object

        # Create new station progress
        new_progress = StationProgress(
            station_id=station_id,
            completed=True
        ).model_dump()

        # Initialize station_progress if it doesn't exist
        if "station_progress" not in user_object:
            user_object["station_progress"] = []

        # Check if station already exists and update if needed
        station_exists = False
        for progress in user_object["station_progress"]:
            if progress["station_id"] == station_id:
                progress["completed"] = True
                station_exists = True
                break

        # Add new progress if station doesn't exist
        if not station_exists:
            user_object["station_progress"].append(new_progress)

        # Update user document with proper error handling
        update_success, update_message = update_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            user_object,
            unique_fields=["user_id"]
        )

        if not update_success:
            return jsonify({
                "error": "Failed to update user progress",
                "details": update_message
            }), 500

        return jsonify({
            "message": "Feedback added and user progress updated successfully",
            "feedback_id": feedback_id,
            "station_progress": user_object["station_progress"]
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An error occurred while processing the feedback",
            "details": str(e)
        }), 500

@jwt_required()
@bp.route(
    "/api/get_feedbacks/<mock_id>/<station_id>/<user_id>", methods=["GET", "OPTIONS"]
)
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def get_feedbacks(mock_id, station_id, user_id):
    try:
        # Create filters dictionary
        filters = {"user_id": user_id, "mock_id": mock_id, "station_id": station_id}

        success, result = get_document_array(
            collection_name=FEEDBACKS_COLLECTION_NAME,
            document_id=FEEDBACKS_DOCUMENT_ID,
            reference_name=FEEDBACKS_REFERENCE_NAME,
            filters=filters,
        )

        if not success:
            return jsonify({"error": result}), 400

        return jsonify({"feedbacks": result}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while retrieving feedbacks."}), 500
