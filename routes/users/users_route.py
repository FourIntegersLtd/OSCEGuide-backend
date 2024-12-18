import os
import uuid
from flask_bcrypt import Bcrypt
from config.helpers import validate_email
from models.users.UserModel import UserModel
from flask_cors import cross_origin
from config.constants import (
    FRONT_END_URLS,
    USERS_COLLECTION_NAME,
    USERS_DOCUMENT_ID,
    USERS_REFERENCE_NAME,
    ADMIN_USER_EMAILS,
)
from flask import Blueprint, request, jsonify
from config.firestore.firestore_config import (
    add_document_array,
    get_document_array,
    update_document_array,
    get_paginated_users_array,
    delete_document_array_item,
)
from datetime import datetime
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    verify_jwt_in_request,
    get_jwt,
)
from flask import jsonify, request, make_response
from flask_mail import Message
from flask import render_template
from datetime import timedelta
from itsdangerous import URLSafeTimedSerializer
from config.helpers import mail
from config.constants import APP_NAME


bcrypt = Bcrypt()
bp = Blueprint("users", __name__)  #


PASSWORD_PEPPER = os.getenv("PASSWORD_PEPPER")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
GMAIL_DEFAULT_SENDER = os.getenv("GMAIL_DEFAULT_SENDER")


def generate_unique_id(email: str) -> str:
    clean_email = email.lower().replace("@", "-").replace(".", "-")
    unique_uuid = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    unique_id = f"{clean_email}-{timestamp}-{unique_uuid}"
    return unique_id


def generate_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(JWT_SECRET_KEY)
    return serializer.dumps(email, salt="password-reset-salt")


@bp.route("/api/register", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def register():
    data = request.json
    user_email = data.get("email").lower()
    user_role = data.get("role", "user")
    has_paid = data.get("has_paid", False)
    is_active = data.get("is_active", True)

    try:
        # Check for existing user
        existing_user = get_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            filters={"email": user_email},
        )

        # If user exists, return error
        if existing_user[0] and existing_user[1]:
            return jsonify({"message": "Email already registered"}), 409

        user_id = generate_unique_id(user_email)
        peppered_password = PASSWORD_PEPPER + data.get("password")
        hashed_password = bcrypt.generate_password_hash(peppered_password).decode(
            "utf-8"
        )
        current_time = datetime.utcnow().isoformat()

        user_data = {
            "user_id": user_id,
            "email": user_email,
            "hashed_password": hashed_password,
            "role": user_role,
            "created_at": current_time,
            "last_login": current_time,
            "mock_progress": [],
            "has_paid": has_paid,
            "is_active": is_active,
            "is_currently_logged_in": False,
        }

        new_user = UserModel(**user_data)
        new_user_dict = new_user.dict()

        add_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            new_user_dict,
            ["user_id", "email"],
        )

        return (
            jsonify(
                {
                    "message": "Account created successfully! Please login to continue.",
                    "user_id": user_id,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"message": "Error during registration!", "error": str(e)}), 500


@bp.route("/api/logout", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
@jwt_required()
def logout():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user_result = get_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            filters={"user_id": current_user_id},
        )

        if not user_result[0] or not user_result[1]:
            return jsonify({"message": "User not found"}), 404

        user_object = user_result[1][0]

        user_object["is_currently_logged_in"] = False

        # Save updated user object back to the database
        update_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            user_object,
            unique_fields=["user_id"],
        )

        response = make_response(jsonify({"message": "Logout successful"}), 200)

        cookies_to_clear = [
            "access_token_cookie",
            "refresh_token_cookie",
            "session_id",
        ]

        for cookie_name in cookies_to_clear:
            response.set_cookie(
                cookie_name,
                value="",
                httponly=True,
                secure=True,  # TODO: Change to True
                samesite="None",
                expires=0,
               
            )

        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response

    except Exception as e:
        return jsonify({"message": "Error during logout!", "error": str(e)}), 500


@bp.route("/api/get_user_by_id/<user_id>", methods=["GET", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
@jwt_required()
def get_user_by_id(user_id: str):
    try:

        # Get user data
        user_result = get_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            filters={"user_id": user_id},
        )

        if not user_result[0] or not user_result[1]:
            return jsonify({"status": "error", "message": "User not found"}), 404

        user_data = user_result[1][0]

        print("user_data", user_data)

        # Sanitize user data - only return necessary fields
        sanitized_user_data = {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "role": user_data.get("role"),
            "created_at": user_data.get("created_at"),
            "is_active": user_data.get("is_active"),
            "has_paid": user_data.get("has_paid"),
            "mock_progress": user_data.get("mock_progress", []),
            "station_progress": user_data.get("station_progress", []),
        }

        return jsonify({"status": "success", "user": sanitized_user_data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": "Error fetching user data"}), 500


@bp.route("/api/login", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def login():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

       

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        user = get_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            filters={"email": email.lower()},
        )

        if not user[0] or not user[1]:
            return jsonify({"message": "Invalid credentials"}), 401

        user_data = user[1]
        user_object = user_data[0]

        # print("user_object", user_object)

        # if user_object.get("has_paid") == False:
        #     return (
        #         jsonify(
        #             {
        #                 "message": "Your payment details are still being processed, please contact support if you have paid."
        #             }
        #         ),
        #         401,
        #     )

        peppered_password = PASSWORD_PEPPER + password
        if not bcrypt.check_password_hash(
            user_object.get("hashed_password"), peppered_password
        ):
            return jsonify({"message": "Invalid credentials"}), 401

        # Update last_login and is_currently_logged_in
        user_object["last_login"] = (
            datetime.utcnow().isoformat()
        )  # Update last login time
        user_object["is_currently_logged_in"] = True  # Set current login status

        # Save updated user object back to the database
        update_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            user_object,
            unique_fields=["user_id"],
        )

        # Create access token with role information
        access_token = create_access_token(
            identity=user_object.get("user_id"),
            expires_delta=timedelta(minutes=240),
            additional_claims={
                "email": user_object.get("email"),
                "role": user_object.get("role"),
            },
        )

        # Create response
        response = make_response(
            jsonify(
                {
                    "status": "success",
                    "message": "Login successful",
                    "user": {
                        "userId": user_object.get("user_id"),
                        "email": user_object.get("email"),
                        "role": user_object.get("role"),
                        "station_progress": user_object.get("station_progress", []),
                        "mock_progress": user_object.get("mock_progress", []),
                    },
                }
            )
        )

        response.set_cookie(
            "access_token_cookie",
            access_token,
            secure=True,
            httponly=True,
            samesite="None",
         
        )

        return response

    except Exception as e:
        return jsonify({"message": "An error occurred during login"}), 500


@jwt_required()
@bp.route("/api/check_auth", methods=["GET", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def check_auth():
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()

        if not current_user_id:
            return (
                jsonify({"status": "error", "message": "No user ID found in token"}),
                400,
            )

        user_result = get_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            filters={"user_id": current_user_id},
        )

        if not user_result[0] or not user_result[1]:
            return jsonify({"status": "error", "message": "User not found"}), 404

        user_data = user_result[1][0]

        # Only return essential user information
        relevant_user_data = {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "role": user_data.get("role"),
            "is_active": user_data.get("is_active"),
            "has_paid": user_data.get("has_paid"),
            "mock_progress": user_data.get("mock_progress", []),
            "station_progress": user_data.get("station_progress", []),
            "flagged_stations": user_data.get("flagged_stations", []),
        }

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Authentication successful",
                    "user": relevant_user_data,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@bp.route("/api/forgot_password", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def forgot_password():
    data = request.json
    email = data.get("email")

    # Validate email
    if not email or not validate_email(email):
        return make_response(jsonify({"message": "Invalid email address"}), 400)

    # Fetch user by email
    user = get_document_array(
        USERS_COLLECTION_NAME,
        USERS_DOCUMENT_ID,
        USERS_REFERENCE_NAME,
        filters={"email": email},
    )

    # Check if user exists
    if user is None or not user[0]:
        return make_response(
            jsonify({"message": "Your account does not exist, Please try again!"}), 404
        )

    access_token = generate_token(email)  # Generate a secure token for password reset

    try:
        # Create the email message
        msg = Message(
            "Password Reset Request",
            sender=GMAIL_DEFAULT_SENDER,
            recipients=[email],
        )

        # Render the email template with user details and token
        msg.html = render_template(
            "reset_password_email.html",
            access_token=access_token,
            app_name=APP_NAME,
        )

        try:
            # Send the email
            mail.send(msg)
            return (
                jsonify(
                    {
                        "message": "Password reset access code sent successfully",
                    }
                ),
                200,
            )
            return (
                jsonify({"message": "Password reset access code sent successfully"}),
                200,
            )

        except Exception as e:
            return jsonify({"message": "Error sending email"}), 500

    except Exception as e:
        return jsonify({"message": "Error processing request"}), 500


@bp.route("/api/reset_password", methods=["POST", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def reset_password():
    data = request.json
    token = data.get("token")  # Get the token from the request
    new_password = data.get("password")  # Get the new password

    # Validate the token
    try:
        serializer = URLSafeTimedSerializer(JWT_SECRET_KEY)
        email = serializer.loads(
            token, salt="password-reset-salt", max_age=3600
        )  # Token valid for 1 hour
    except Exception as e:
        return jsonify({"message": "Invalid or expired token"}), 400

    # Fetch user by email
    user = get_document_array(
        USERS_COLLECTION_NAME,
        USERS_DOCUMENT_ID,
        USERS_REFERENCE_NAME,
        filters={"email": email},
    )

    # Check if user exists
    if user is None or not user[0]:
        return make_response(
            jsonify({"message": "Your account does not exist, Please try again!"}), 404
        )

    # Update the user's password
    peppered_password = PASSWORD_PEPPER + new_password
    hashed_password = bcrypt.generate_password_hash(peppered_password).decode("utf-8")

    user_object = user[1][0]
    user_object["hashed_password"] = hashed_password  # Update the hashed password

    # Save updated user object back to the database
    update_document_array(
        USERS_COLLECTION_NAME,
        USERS_DOCUMENT_ID,
        USERS_REFERENCE_NAME,
        user_object,
        unique_fields=["user_id"],
    )

    return jsonify({"message": "Password reset successful"}), 200


@bp.route("/api/get_all_users", methods=["GET", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def get_all_users():
    try:
        # Step 1: Get pagination parameters from query string
        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=20, type=int)

        offset = (page - 1) * limit

        # Step 3: Get total count of stations
        total_success, total_users = get_document_array(
            USERS_COLLECTION_NAME, USERS_DOCUMENT_ID, USERS_REFERENCE_NAME
        )

        if not total_success:
            return jsonify({"error": total_users}), 404

        success, users = get_paginated_users_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            limit=limit,
            offset=offset,
        )

        if not success:
            return jsonify({"error": users}), 404

        return (
            jsonify(
                {
                    "users": users,
                    "page": page,
                    "limit": limit,
                    "total": len(total_users),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "An error occurred while retrieving users."}), 500


@jwt_required()
@bp.route("/api/update_user/<user_id>", methods=["PUT", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
def update_user(user_id: str):
    try:

        verify_jwt_in_request()
        claims = get_jwt()
        current_user_email = claims.get("email")

        if current_user_email not in ADMIN_USER_EMAILS:
            return (
                jsonify({"message": "You are not authorized to update this user"}),
                403,
            )

        data = request.json

        # First, get the existing user data
        user_result = get_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            filters={"user_id": user_id},
        )

        if not user_result[0] or not user_result[1]:
            return jsonify({"message": "User not found"}), 404

        user_data = user_result[1][0]

        # Update only the fields that were sent in the request
        if "mock_progress" in data:
            user_data["mock_progress"] = data["mock_progress"]

        if "station_progress" in data:
            user_data["station_progress"] = data["station_progress"]

        if "has_paid" in data:
            user_data["has_paid"] = data["has_paid"]

        # Update the document in Firestore
        update_document_array(
            USERS_COLLECTION_NAME,
            USERS_DOCUMENT_ID,
            USERS_REFERENCE_NAME,
            user_data,
            unique_fields=["user_id"],
        )

        return jsonify({"message": "User updated successfully", "user": user_data}), 200

    except Exception as e:
        return jsonify({"message": "Error updating user", "error": str(e)}), 500


@bp.route("/api/delete_user/<user_id>", methods=["DELETE", "OPTIONS"])
@cross_origin(origins=FRONT_END_URLS, supports_credentials=True)
@jwt_required()
def delete_user(user_id):
    try:
        # Get the claims from the JWT token which includes the email
        claims = get_jwt()
        current_user_email = claims.get('email')  # Get email from token claims

        if current_user_email not in ADMIN_USER_EMAILS:
            return jsonify({"message": "Unauthorized to delete users"}), 403

        # Use delete_document_array to remove the user
        success, message = delete_document_array_item(
            collection_name=USERS_COLLECTION_NAME,
            document_id=USERS_DOCUMENT_ID,
            reference_name=USERS_REFERENCE_NAME,
            unique_fields=["user_id"],
            unique_values=[user_id]
        )

        if not success:
            return jsonify({"error": message}), 500

        return jsonify({"message": "User deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while deleting the user."}), 500    