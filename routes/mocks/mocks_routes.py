import uuid
from datetime import datetime
from flask_cors import cross_origin
from flask import Blueprint, request, jsonify
from config.constants import (
    FRONT_END_URLS,
    MOCKS_COLLECTION_NAME,
    MOCKS_DOCUMENT_ID,
    MOCKS_REFERENCE_NAME,
    USERS_COLLECTION_NAME,
    USERS_DOCUMENT_ID,
    USERS_REFERENCE_NAME,
)
from config.firestore.firestore_config import (
    add_document_array,
    get_document_array,
    update_document_array,
    delete_document_array_item,
)
from models.mocks.MockModel import MockModel
from config.helpers import get_station_by_id
from models.users.UserModel import MockProgress
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

bp = Blueprint("mocks", __name__)  #


@jwt_required()
@bp.route("/api/create_mock", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def create_mock():
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()

        data = request.json

        mock_data = {
            "mock_id": str(uuid.uuid4()),
            "name": data.get("name"),
            "duration": data.get("duration"),
            "stations": data.get("stationIds"),
            "created_by": user_id,
            "created_at": datetime.now().isoformat(),
        }

        new_mock = MockModel(**mock_data).model_dump()

        success, message = add_document_array(
            MOCKS_COLLECTION_NAME,
            MOCKS_DOCUMENT_ID,
            MOCKS_REFERENCE_NAME,
            new_mock,
        )

        if not success:
            return jsonify({"error": message}), 500

        return jsonify({"message": "Mock created successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/get_mocks", methods=["GET", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def get_mocks():
    try:
        success, mocks = get_document_array(
            MOCKS_COLLECTION_NAME,
            MOCKS_DOCUMENT_ID,
            MOCKS_REFERENCE_NAME,
        )

        if not success:
            return jsonify({"error": mocks}), 404

        # Fetch station details for each mock
        for mock in mocks:
            mock["stations"] = [
                get_station_by_id(station_id) for station_id in mock["stations"]
            ]

        return jsonify({"mocks": mocks}), 200

    except Exception as e:
        return (
            jsonify({"error": "An error occurred while retrieving mocks."}),
            500,
        )


@jwt_required()
@bp.route("/api/update_mock/<mock_id>", methods=["PUT", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def update_mock(mock_id):
    try:
        data = request.json

        verify_jwt_in_request()
        user_id = get_jwt_identity()

        # Validate input data
        if not data.get("name") or not isinstance(data["name"], str):
            return jsonify({"error": "Valid name is required"}), 400
        if not data.get("duration") or not isinstance(data["duration"], (int, float)):
            return jsonify({"error": "Valid duration is required"}), 400
        if not data.get("stationIds") or not isinstance(data["stationIds"], list):
            return jsonify({"error": "Valid stationIds are required"}), 400

        mock_data = {
            "mock_id": mock_id,
            "name": data.get("name"),
            "duration": data.get("duration"),
            "stations": data.get("stationIds"),
            "created_by": user_id,
            "created_at": datetime.now().isoformat(),
        }

        # Validate with MockModel
        validated_mock = MockModel(**mock_data).model_dump()

        success, message = update_document_array(
            MOCKS_COLLECTION_NAME,
            MOCKS_DOCUMENT_ID,
            MOCKS_REFERENCE_NAME,
            validated_mock,
            unique_fields=["mock_id"],
        )

        if not success:
            return jsonify({"error": message}), 500

        return (
            jsonify({"message": "Mock updated successfully", "mock": validated_mock}),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/delete_mock/<mock_id>", methods=["DELETE", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def delete_mock(mock_id):
    try:
        # Validate mock_id
        if not mock_id:
            return jsonify({"error": "Mock ID is required"}), 400

        # First check if the mock exists
        success, mocks = get_document_array(
            MOCKS_COLLECTION_NAME,
            MOCKS_DOCUMENT_ID,
            MOCKS_REFERENCE_NAME,
            filters={"mock_id": mock_id},
        )

        if not success or not mocks:
            return jsonify({"error": "Mock not found"}), 404

        # Proceed with deletion
        success, message = delete_document_array_item(
            MOCKS_COLLECTION_NAME,
            MOCKS_DOCUMENT_ID,
            MOCKS_REFERENCE_NAME,
            unique_fields=["mock_id"],
            unique_values=[mock_id],
        )

        if not success:
            return jsonify({"error": message}), 500

        return (
            jsonify(
                {"message": "Mock deleted successfully", "deleted_mock_id": mock_id}
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/complete_mock", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def complete_mock():
    try:
        data = request.json
        mock_id = data.get("mock_id")
        user_id = data.get("user_id")

        if not all([mock_id, user_id]):
            return jsonify({"error": "Missing required fields"}), 400

        # Get the user document
        success, users = get_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            filters={"user_id": user_id},
        )

        if not success or not users or len(users) == 0:
            return jsonify({"error": "User not found"}), 404

        user = users[0]  # Get the first (and should be only) matching user

        # Create new mock progress entry
        new_progress = MockProgress(mock_id=mock_id, completed=True).model_dump()

        # Update the user's existing data with the new mock progress
        user_data = user.copy()
        if "mock_progress" not in user_data:
            user_data["mock_progress"] = []
        user_data["mock_progress"].append(new_progress)

        # Update user document
        success, message = update_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            user_data,
            unique_fields=["user_id"],
        )

        if not success:
            return jsonify({"error": message}), 500

        return jsonify({"message": "Mock progress updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500