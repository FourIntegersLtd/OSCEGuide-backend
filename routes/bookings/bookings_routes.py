from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt
from flask_cors import cross_origin
from config.constants import FRONT_END_URLS
from config.firestore.firestore_config import (
    get_document_array,
    update_document_array,
    add_document_array,
    delete_document_array_item,
)
from datetime import datetime
from config.constants import (
    BOOKINGS_COLLECTION_NAME,
    BOOKINGS_DOCUMENT_ID,
    BOOKINGS_REFERENCE_NAME,
    USERS_COLLECTION_NAME,
    USERS_DOCUMENT_ID,
    USERS_REFERENCE_NAME,
)


bp = Blueprint("bookings", __name__)


@jwt_required()
@bp.route("/api/create_bookings", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def create_bookings():
    try:
        data = request.json
        verify_jwt_in_request()
        claims = get_jwt()
        current_user_email = claims.get("email")
        max_users = 5
        bookings = data.get("bookings", [])

        for booking in bookings:
            booking_id = f"{booking['mock_id']}_{booking['mock_datetime']}"

            # First check if booking exists
            success, result = get_document_array(
                collection_name=BOOKINGS_COLLECTION_NAME,
                document_id=BOOKINGS_DOCUMENT_ID,
                reference_name=BOOKINGS_REFERENCE_NAME,
                filters={"booking_id": booking_id},
            )

            if success and result:
                # Booking exists - add user to existing booking
                existing_booking = result[0]
                if current_user_email in existing_booking["booked_users"]:
                    return (
                        jsonify({"message": "You have already booked this mock"}),
                        400,
                    )

                if len(existing_booking["booked_users"]) >= max_users:
                    return (
                        jsonify(
                            {
                                "message": "This booking is now full, please try another time slot"
                            }
                        ),
                        400,
                    )

                existing_booking["booked_users"].append(current_user_email)
                success, message = update_document_array(
                    collection_name=BOOKINGS_COLLECTION_NAME,
                    document_id=BOOKINGS_DOCUMENT_ID,
                    reference_name=BOOKINGS_REFERENCE_NAME,
                    updated_item=existing_booking,
                    unique_fields=["booking_id"],
                )
                if not success:
                    raise Exception(message)

            else:
                # Check if there are existing bookings for this mock_id and datetime
                success, all_bookings = get_document_array(
                    collection_name=BOOKINGS_COLLECTION_NAME,
                    document_id=BOOKINGS_DOCUMENT_ID,
                    reference_name=BOOKINGS_REFERENCE_NAME,
                    filters={
                        "mock_id": booking["mock_id"],
                        "booking_datetime": booking["mock_datetime"],
                    },
                )

                if success and all_bookings:
                    total_booked_users = sum(
                        len(b["booked_users"]) for b in all_bookings
                    )
                    # You might want to make this configurable
                    if total_booked_users >= max_users:
                        raise Exception(
                            f"Maximum users ({max_users}) exceeded for this time slot"
                        )

                # Create new booking
                new_booking = {
                    "booking_id": booking_id,
                    "mock_id": booking["mock_id"],
                    "mock_name": booking["mock_name"],
                    "booking_datetime": booking["mock_datetime"],
                    "booked_users": [current_user_email],
                    "max_users": 4,
                }

                success, message = add_document_array(
                    collection_name=BOOKINGS_COLLECTION_NAME,
                    document_id=BOOKINGS_DOCUMENT_ID,
                    reference_name=BOOKINGS_REFERENCE_NAME,
                    new_item=new_booking,
                    unique_fields=["booking_id"],
                )
                if not success:
                    raise Exception(message)

            # First get the user's current booked_mocks
            success, user_result = get_document_array(
                collection_name=USERS_COLLECTION_NAME,
                document_id=USERS_DOCUMENT_ID,
                reference_name=USERS_REFERENCE_NAME,
                filters={"email": current_user_email},
            )

            if not success or not user_result:
                raise Exception("User not found")

            current_user = user_result[0]
            current_booked_mocks = current_user.get("booked_mocks", [])

            new_booked_mock = {
                "mock_name": booking["mock_name"],
                "mock_id": booking["mock_id"],
                "mock_datetime": booking["mock_datetime"],
                "booking_datetime": datetime.utcnow().isoformat(),
            }

            # Append the new booking to existing booked_mocks
            updated_booked_mocks = current_booked_mocks + [new_booked_mock]

            success, message = update_document_array(
                collection_name=USERS_COLLECTION_NAME,
                document_id=USERS_DOCUMENT_ID,
                reference_name=USERS_REFERENCE_NAME,
                updated_item={
                    "email": current_user_email,
                    "booked_mocks": updated_booked_mocks,
                },
                unique_fields=["email"],
            )
            if not success:
                raise Exception(f"Failed to update user's booked mocks: {message}")

        return jsonify({"message": "Bookings created successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@jwt_required()
@bp.route("/api/update_booking/<mock_id>/<user_id>", methods=["PUT", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def update_booking_date(mock_id, user_id):
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        current_user_email = claims.get("email")
        new_date = request.json.get("new_date")
        mock_name = request.json.get("mock_name")

        # Get all bookings for this mock
        success, bookings = get_document_array(
            collection_name=BOOKINGS_COLLECTION_NAME,
            document_id=BOOKINGS_DOCUMENT_ID,
            reference_name=BOOKINGS_REFERENCE_NAME,
            filters={"mock_id": mock_id},
        )
        print(
            f"[DEBUG] Found bookings: {success}, count: {len(bookings) if bookings else 0}"
        )

        if not success or not bookings:
            return jsonify({"error": "Booking not found"}), 404

        # Find the booking containing the current user
        old_booking = None
        for booking in bookings:
            if current_user_email in booking["booked_users"]:
                old_booking = booking
                print(f"[DEBUG] Found user's current booking: {old_booking}")
                break

        if not old_booking:
            return jsonify({"error": "User not found in this booking"}), 404

        # Check if new date is different from current date
        if old_booking["booking_datetime"] == new_date:
            return (
                jsonify(
                    {
                        "message": "You have selected the same date as your current booking"
                    }
                ),
                400,
            )

        print(
            f"[DEBUG] Removing user from old booking. Users before: {old_booking['booked_users']}"
        )
        old_booking["booked_users"].remove(current_user_email)
        print(f"[DEBUG] Users after removal: {old_booking['booked_users']}")

        # Update old booking (or delete if empty)
        if old_booking["booked_users"]:
            print("[DEBUG] Updating old booking with remaining users")
            success, message = update_document_array(
                collection_name=BOOKINGS_COLLECTION_NAME,
                document_id=BOOKINGS_DOCUMENT_ID,
                reference_name=BOOKINGS_REFERENCE_NAME,
                updated_item=old_booking,
                unique_fields=["booking_id"],
            )
        else:
            print("[DEBUG] Deleting empty old booking")
            success, message = delete_document_array_item(
                collection_name=BOOKINGS_COLLECTION_NAME,
                document_id=BOOKINGS_DOCUMENT_ID,
                reference_name=BOOKINGS_REFERENCE_NAME,
                unique_fields=["booking_id"],
                unique_values=[old_booking["booking_id"]],
            )

        if not success:
            raise Exception(f"Failed to update old booking: {message}")

        # Add user to new booking or create one
        new_booking_id = f"{mock_id}_{new_date}"
        print(f"[DEBUG] Checking for existing booking at new time: {new_booking_id}")
        success, existing_bookings = get_document_array(
            collection_name=BOOKINGS_COLLECTION_NAME,
            document_id=BOOKINGS_DOCUMENT_ID,
            reference_name=BOOKINGS_REFERENCE_NAME,
            filters={"booking_id": new_booking_id},
        )
        print(
            f"[DEBUG] Existing booking found: {success}, count: {len(existing_bookings) if existing_bookings else 0}"
        )

        if success and existing_bookings:
            # Add to existing booking
            existing_booking = existing_bookings[0]
            if len(existing_booking["booked_users"]) >= existing_booking["max_users"]:
                return jsonify({"error": "New time slot is full"}), 400

            existing_booking["booked_users"].append(current_user_email)
            success, message = update_document_array(
                collection_name=BOOKINGS_COLLECTION_NAME,
                document_id=BOOKINGS_DOCUMENT_ID,
                reference_name=BOOKINGS_REFERENCE_NAME,
                updated_item=existing_booking,
                unique_fields=["booking_id"],
            )
        else:
            # Create new booking
            new_booking = {
                "booking_id": new_booking_id,
                "mock_id": mock_id,
                "booking_datetime": new_date,
                "booked_users": [current_user_email],
                "max_users": 4,
            }
            success, message = add_document_array(
                collection_name=BOOKINGS_COLLECTION_NAME,
                document_id=BOOKINGS_DOCUMENT_ID,
                reference_name=BOOKINGS_REFERENCE_NAME,
                new_item=new_booking,
                unique_fields=["booking_id"],
            )

        if not success:
            raise Exception(f"Failed to create/update new booking: {message}")

        # Update user's booked_mocks
        success, user_result = get_document_array(
            collection_name=USERS_COLLECTION_NAME,
            document_id=USERS_DOCUMENT_ID,
            reference_name=USERS_REFERENCE_NAME,
            filters={"email": current_user_email},
        )

        if not success or not user_result:
            raise Exception("User not found")

        current_user = user_result[0]
        booked_mocks = current_user.get("booked_mocks", [])

        # Remove old booking
        booked_mocks = [bm for bm in booked_mocks if not (bm["mock_id"] == mock_id)]

        # Add new booking
        new_booked_mock = {
            "mock_name": mock_name,
            "mock_id": mock_id,
            "mock_datetime": new_date,
            "booking_datetime": datetime.utcnow().isoformat(),
        }
        booked_mocks.append(new_booked_mock)

        success, message = update_document_array(
            collection_name=USERS_COLLECTION_NAME,
            document_id=USERS_DOCUMENT_ID,
            reference_name=USERS_REFERENCE_NAME,
            updated_item={"email": current_user_email, "booked_mocks": booked_mocks},
            unique_fields=["email"],
        )

        if not success:
            raise Exception(f"Failed to update user's booked mocks: {message}")

        print(f"[DEBUG] New booked_mocks count: {len(booked_mocks)}")

        return jsonify({"message": "Booking updated successfully"}), 200

    except Exception as e:
        print(f"[DEBUG] Error in update_booking_date: {str(e)}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        return jsonify({"error": str(e)}), 500


@jwt_required()
@bp.route("/api/get_all_bookings", methods=["GET", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def get_bookings():
    try:
        # Get all bookings
        success, bookings = get_document_array(
            collection_name=BOOKINGS_COLLECTION_NAME,
            document_id=BOOKINGS_DOCUMENT_ID,
            reference_name=BOOKINGS_REFERENCE_NAME,
        )

        if not success:
            return jsonify({"error": "Failed to fetch bookings"}), 500

        return jsonify({"bookings": bookings or []}), 200

    except Exception as e:
        print(f"Error in get_bookings: {str(e)}")
        return jsonify({"error": str(e)}), 500
