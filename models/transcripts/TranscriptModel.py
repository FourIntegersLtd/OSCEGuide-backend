from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class TranscriptMessage(BaseModel):
    role: str = Field(..., description="Role of the speaker (e.g., 'user', 'interviewer')")
    message: str = Field(..., description="Content of the message")
    # time_in_call_secs: int = Field(..., description="Time in seconds when message was spoken")

class Transcript(BaseModel):
    transcript_id: str = Field(..., description="Unique identifier for the transcript")
    user_id: str = Field(..., description="User ID")
    mock_id: str = Field(..., description="Mock ID")
    station_id: str = Field(..., description="Station ID")
    transcript_message: List[TranscriptMessage] = Field(..., description="List of transcript messages")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Time of the transcript"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "transcript_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "mock_id": "mock123",
                "station_id": "station456",
                "transcript_message": [
                    {
                        "role": "interviewer",
                        "message": "Tell me about your experience with Python",
                        "time_in_call_secs": 0
                    },
                    {
                        "role": "user",
                        "message": "I have 5 years of experience with Python",
                        "time_in_call_secs": 3
                    }
                ],
                "created_at": datetime.utcnow().isoformat()
            }
        }
    }


 