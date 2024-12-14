import uuid
from datetime import datetime
from flask_cors import cross_origin
from models.users.UserModel import StationProgress
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.constants import (
    FRONT_END_URLS,
    STATIONS_COLLECTION_NAME,
    STATIONS_DOCUMENT_ID,
    STATIONS_REFERENCE_NAME,
    USERS_COLLECTION_NAME,
    USERS_DOCUMENT_ID,
    USERS_REFERENCE_NAME,
)
from config.firestore.firestore_config import (
    add_document_array,
    get_document_array,
    update_document_array,
    get_paginated_stations_array,
)

bp = Blueprint("stations", __name__)  #


@jwt_required()
@bp.route("/api/create_station", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def create_station():
    try:
        data = request.json
        user_id = get_jwt_identity()
        station_data = {
            "station_id": str(uuid.uuid4()),
            "station_name": data.get("station_name"),
            "created_by": user_id,
            "created_at": datetime.now().isoformat(),
            "patient_information": {
                "patient_biodata": data["patient_information"]["patient_biodata"],
                "gender": data["patient_information"]["gender"],
                "opening_sentence": data["patient_information"]["opening_sentence"],
                "expanded_history": data["patient_information"]["expanded_history"],
                "family_social_history": data["patient_information"][
                    "family_social_history"
                ],
                "past_med_history_allergies": data["patient_information"][
                    "past_med_history_allergies"
                ],
                "idea": data["patient_information"]["idea"],
                "concerns": data["patient_information"]["concerns"],
                "expectation": data["patient_information"]["expectation"],
                "persona": data["patient_information"]["persona"],
            },
            "doctor_information": {
                "patient_biodata": data["doctor_information"]["patient_biodata"],
                "recent_notes": data["doctor_information"]["recent_notes"],
                "current_medications": data["doctor_information"][
                    "current_medications"
                ],
                "past_medical_history": data["doctor_information"][
                    "past_medical_history"
                ],
                "recent_investigations": data["doctor_information"][
                    "recent_investigations"
                ],
                "social_history": data["doctor_information"]["social_history"],
            },
            "management_plan": {
                "explanation": data["management_plan"]["explanation"],
                "assessment": data["management_plan"]["assessment"],
                "social_concerns": data["management_plan"]["social_concerns"],
                "ice": data["management_plan"]["ice"],
                "immediate_actions": data["management_plan"]["immediate_actions"],
                "pharmacological_treatment": data["management_plan"][
                    "pharmacological_treatment"
                ],
                "non_pharmacological_treatment": data["management_plan"][
                    "non_pharmacological_treatment"
                ],
                "follow_up": data["management_plan"]["follow_up"],
                "health_education": data["management_plan"]["health_education"],
                "safety_netting": data["management_plan"]["safety_netting"],
                "additional_notes": data["management_plan"]["additional_notes"],
            },
            "tags": data.get("tags", []),
        }

        # Add document to Firestore
        add_document_array(
            STATIONS_COLLECTION_NAME,
            STATIONS_DOCUMENT_ID,
            STATIONS_REFERENCE_NAME,
            station_data,
        )

        return (
            jsonify(
                {"message": "Station created successfully", "station": station_data}
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/get_paginated_stations", methods=["GET", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def get_paginated_stations():
    try:
        # Step 1: Get pagination parameters from query string
        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=20, type=int)

        # Step 2: Calculate offset - by how many stations to skip, depedning on the page and limit
        # eg in page 1, offset is 0, in page 2, offset is 20, in page 3, offset is 40
        offset = (page - 1) * limit

        # Step 3: Get total count of stations
        total_success, total_stations = get_document_array(
            STATIONS_COLLECTION_NAME, STATIONS_DOCUMENT_ID, STATIONS_REFERENCE_NAME
        )

        if not total_success:
            return jsonify({"error": total_stations}), 404

        success, stations = get_paginated_stations_array(
            STATIONS_COLLECTION_NAME,
            STATIONS_DOCUMENT_ID,
            STATIONS_REFERENCE_NAME,
            limit=limit,
            offset=offset,
        )

        if not success:
            return jsonify({"error": stations}), 404

        return (
            jsonify(
                {
                    "stations": stations,
                    "page": page,
                    "limit": limit,
                    "total": len(
                        total_stations
                    ),  # Use the total count retrieved from the database
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "An error occurred while retrieving stations."}), 500


@bp.route("/api/get_all_stations", methods=["GET", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def get_all_stations():
    try:
        success, all_stations = get_document_array(
            STATIONS_COLLECTION_NAME, STATIONS_DOCUMENT_ID, STATIONS_REFERENCE_NAME
        )

        if not success:
            return jsonify({"error": all_stations}), 404

        return (
            jsonify(
                {
                    "stations": all_stations,
                    # Use the total count retrieved from the database
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "An error occurred while retrieving stations."}), 500


@bp.route("/api/get_stations/<mock_id>", methods=["GET", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def get_stations(
    mock_id,
):
    try:
        filters = {
            "mock_id": mock_id,
        }
        success, stations = get_document_array(
            STATIONS_COLLECTION_NAME,
            STATIONS_DOCUMENT_ID,
            STATIONS_REFERENCE_NAME,
            filters=filters,
        )

        if not success:
            return jsonify({"error": stations}), 404
        return jsonify({"stations": stations}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while retrieving stations."}), 500


@bp.route("/api/get_station_by_id/<station_id>", methods=["GET", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def get_station_by_id(station_id):
    try:

        success, station = get_document_array(
            STATIONS_COLLECTION_NAME,
            STATIONS_DOCUMENT_ID,
            STATIONS_REFERENCE_NAME,
            filters={"station_id": station_id},
        )

        filtered_station = station[0]

        if not success:
            return jsonify({"error": filtered_station}), 404
        return jsonify({"station": filtered_station}), 200
    except Exception as e:
        return (
            jsonify({"error": "An error occurred while retrieving the station."}),
            500,
        )


@bp.route("/api/complete_station", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def complete_station():
    try:
        data = request.json
        station_id = data.get("station_id")
        user_id = data.get("user_id")

        if not all([station_id, user_id]):
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

        user = users[0]
        new_progress = StationProgress(
            station_id=station_id, completed=True
        ).model_dump()

        # Update the user's existing data with the completed station
        user_data = user.copy()
        if "station_progress" not in user_data:
            user_data["station_progress"] = []
        user_data["station_progress"].append(new_progress)

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

        return jsonify({"message": "Station completed successfully"}), 200
    except Exception as e:
        return (
            jsonify({"error": "An error occurred while completing the station."}),
            500,
        )


@bp.route("/api/flag_station", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def flag_station():
    try:
        data = request.json
        station_id = data.get("station_id")
        user_id = data.get("user_id")
        mock_id = data.get("mock_id")

        if not all([station_id, user_id, mock_id]):
            return jsonify({"error": "Missing required fields"}), 400

        success, users = get_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            filters={"user_id": user_id},
        )

        if not success or not users or len(users) == 0:
            return jsonify({"error": "User not found"}), 404

        user = users[0]
        new_flag = {"station_id": station_id, "mock_id": mock_id, "flagged": True}

        user_data = user.copy()
        if "flagged_stations" not in user_data:
            user_data["flagged_stations"] = []

        if any(
            flag["station_id"] == station_id for flag in user_data["flagged_stations"]
        ):
            return jsonify({"error": "Station is already flagged"}), 400
        user_data["flagged_stations"].append(new_flag)

        success, message = update_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            user_data,
            unique_fields=["user_id"],
        )

        if not success:
            return jsonify({"error": message}), 500

        return jsonify({"message": "Station flagged successfully"}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while flagging the station."}), 500


@bp.route("/api/update_station/<station_id>", methods=["PUT", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
@jwt_required()
def update_station(station_id):
    try:
        data = request.json
        user_id = get_jwt_identity()

        # First, get the existing station
        success, stations = get_document_array(
            STATIONS_COLLECTION_NAME,
            STATIONS_DOCUMENT_ID,
            STATIONS_REFERENCE_NAME,
            filters={"station_id": station_id},
        )

        if not success or not stations:
            return jsonify({"error": "Station not found"}), 404

        existing_station = stations[0]

        # # Check if the user is the creator of the station
        # if existing_station.get("created_by") != user_id:
        #     return jsonify({"error": "Unauthorized to update this station"}), 403

        # Initialize the update dictionary with only changed fields
        updated_fields = {}

        # Helper function to compare and update nested dictionaries
        def update_nested_dict(existing: dict, new: dict, parent_key: str):
            changes = {}
            for key, new_value in new.items():
                existing_value = existing.get(key)
                if existing_value != new_value:
                    changes[key] = new_value
            if changes:
                updated_fields[parent_key] = {**existing, **changes}

        # Check and update station_name if changed
        if "station_name" in data and data["station_name"] != existing_station.get(
            "station_name"
        ):
            updated_fields["station_name"] = data["station_name"]

        # Check and update nested objects only if they exist in the request
        if "patient_information" in data:
            update_nested_dict(
                existing_station["patient_information"],
                data["patient_information"],
                "patient_information",
            )

        if "doctor_information" in data:
            update_nested_dict(
                existing_station["doctor_information"],
                data["doctor_information"],
                "doctor_information",
            )

        if "management_plan" in data:
            update_nested_dict(
                existing_station["management_plan"],
                data["management_plan"],
                "management_plan",
            )

        # Check and update tags if changed
        if "tags" in data and data["tags"] != existing_station.get("tags"):
            updated_fields["tags"] = data["tags"]

        # If no fields have changed, return early
        if not updated_fields:
            return (
                jsonify(
                    {"message": "No changes detected", "station": existing_station}
                ),
                200,
            )

        # Create the updated station with only changed fields
        updated_station = {**existing_station, **updated_fields}

        # Update only if there are changes
        success, message = update_document_array(
            STATIONS_COLLECTION_NAME,
            STATIONS_DOCUMENT_ID,
            STATIONS_REFERENCE_NAME,
            updated_station,
            unique_fields=["station_id"],
        )

        if not success:
            return jsonify({"error": message}), 500

        return (
            jsonify(
                {
                    "message": "Station updated successfully",
                    "station": updated_station,
                    "updated_fields": list(
                        updated_fields.keys()
                    ),  # Show which fields were updated
                }
            ),
            200,
        )

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except Exception as e:
        return (
            jsonify(
                {"error": f"An error occurred while updating the station: {str(e)}"}
            ),
            500,
        )
