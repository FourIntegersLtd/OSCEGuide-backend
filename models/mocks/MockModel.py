from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class MockModel(BaseModel):
    mock_id: str = Field(description="Mock ID")
    duration: int = Field(description="Duration of the mock in minutes")
    name: str = Field(description="Mock name")
    stations: List[str] = Field(description="List of stations by id in the mock")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the mock was created",
    )
    created_by: str = Field(description="User id of the creator of the mock")
    available_slots: List[str] = Field(description="List of available time slots for the mock")

    class Config:
        json_schema_extra = {
            "example": {
                "mock_id": "12345",
                "duration": 30,
                "name": "Sample Mock",
                "stations": ["station1", "station2"],
                "created_at": "2023-10-01T12:00:00Z",
                "created_by": "user123"
            }
        }
