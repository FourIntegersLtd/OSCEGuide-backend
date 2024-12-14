import re
from config.firestore.firestore_config import get_document_array
from config.constants import (
    STATIONS_COLLECTION_NAME,
    STATIONS_DOCUMENT_ID,
    STATIONS_REFERENCE_NAME,
)
from flask_mail import Mail

mail = Mail()


def validate_email(email: str) -> bool:
    """Validate the email format using a regular expression."""
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email) is not None


def format_transcript(transcript: list | str) -> str:
    """
    Format the transcript to be more readable for the LLM by:
    1. Clearly separating speakers
    2. Adding proper spacing
    3. Removing unnecessary whitespace
    4. Converting timestamps if present
    """
    # Handle list-type transcripts (from the original function)
    if isinstance(transcript, list):
        formatted_conversation = ""
        for entry in transcript:
            role = "DOCTOR" if entry["role"] == "user" else "PATIENT"
            formatted_conversation += f"<{role}>\n{entry['message']}\n</{role}>\n\n"
        return formatted_conversation.strip()

    # Handle string-type transcripts
    lines = transcript.strip().split("\n")
    formatted_lines = []

    for line in lines:
        # Remove extra whitespace
        line = " ".join(line.split())

        # Check if line contains speaker designation (assuming format "Speaker: text")
        if ":" in line:
            speaker, content = line.split(":", 1)
            speaker = speaker.strip().upper()
            # Add XML-like tags around each speaker's content
            formatted_line = f"<{speaker}>\n{content.strip()}\n</{speaker}>"
        else:
            formatted_line = line

        formatted_lines.append(formatted_line)

    # Join with double newlines for better readability
    return "\n\n".join(formatted_lines)


def get_station_by_id(station_id):
    try:
        # Fetch the station details from the database
        success, station = get_document_array(
            STATIONS_COLLECTION_NAME,
            STATIONS_DOCUMENT_ID,
            STATIONS_REFERENCE_NAME,
            filters={"station_id": station_id},
        )

        if not success:
            return {"error": station}  # Return error as a dictionary for consistency

        # Assuming station is a list and we want the first item
        station_details = station[0] if station else None

        if station_details:
            return station_details  # Return the station details
        else:
            return {"error": "Station not found."}  # Return error if not found

    except Exception as e:
        return {
            "error": "An error occurred while retrieving station."
        }  # Return error as a dictionary
