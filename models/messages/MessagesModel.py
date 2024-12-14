from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MessageModel(BaseModel):
    message_id: str = Field(description="Message ID")
    email: str = Field(description="Email of the user")
    subject: str = Field(description="Subject of the message")
    message: str = Field(description="Message content")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the message was created",
    )
    created_by: str = Field(description="User id of the creator of the message")
    response: Optional[str] = Field(default=None, description="Response to the message")

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "12345",
                "subject": "Sample Message",
                "message": "This is a sample message",
                "created_at": "2023-10-01T12:00:00Z",
                "created_by": "user123",
                "response": "This is a sample response",
                "email": "user@example.com",
            }
        }
