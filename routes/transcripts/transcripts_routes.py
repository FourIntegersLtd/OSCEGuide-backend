import uuid
from datetime import datetime
from flask_cors import cross_origin
from flask import Blueprint, request, jsonify
from config.constants import (
    FRONT_END_URLS,
    TRANSCRIPT_COLLECTION_NAME,
    TRANSCRIPT_DOCUMENT_ID,
    TRANSCRIPT_REFERENCE_NAME,
)
from config.firestore.firestore_config import add_document_array, get_document_array
from models.transcripts.TranscriptModel import Transcript


bp = Blueprint("transcripts", __name__)  #


@bp.route("/api/add_transcript_to_db", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def add_transcript():
    try:
        data = request.json

        transcript_messages = [
            {
                "role": msg["role"],
                "message": msg["message"],
                "time_in_call_secs": msg["time_in_call_secs"],
            }
            for msg in data.get("transcript_message", [])
        ]

        transcript_data = {
            "transcript_id": data.get("transcript_id"),
            "user_id": data.get("user_id"),
            "mock_id": data.get("mock_id"),
            "station_id": data.get("station_id"),
            "transcript_message": transcript_messages,
            "created_at": datetime.now().isoformat(),  # Convert datetime to ISO format string
        }

        new_transcript = Transcript(**transcript_data).model_dump()

        success, message = add_document_array(
            TRANSCRIPT_COLLECTION_NAME,
            TRANSCRIPT_DOCUMENT_ID,
            TRANSCRIPT_REFERENCE_NAME,
            new_transcript,
        )

        if not success:
            return jsonify({"error": message}), 400

        return (
            jsonify(
                {
                    "message": "Transcript added successfully!",
                    "transcript_id": data.get("transcript_id"),
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route(
    "/api/get_transcripts/<mock_id>/<station_id>/<user_id>", methods=["GET", "OPTIONS"]
)
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def get_transcripts(mock_id, station_id, user_id):
    try:

        success, transcripts = get_document_array(
            TRANSCRIPT_COLLECTION_NAME,
            TRANSCRIPT_DOCUMENT_ID,
            TRANSCRIPT_REFERENCE_NAME,
            filters={"user_id": user_id, "mock_id": mock_id, "station_id": station_id},
        )

        if not success:
            return jsonify({"error": transcripts}), 404

        return jsonify({"transcripts": transcripts}), 200

    except Exception as e:
        return (
            jsonify({"error": "An error occurred while retrieving transcripts."}),
            500,
        )
