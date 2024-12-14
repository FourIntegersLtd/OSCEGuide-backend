from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class MockProgress(BaseModel):
    mock_id: str
    completed: bool


class StationProgress(BaseModel):
    station_id: str
    completed: bool


class FlaggedStation(BaseModel):
    station_id: str
    flagged: bool
    mock_id: str


class UserModel(BaseModel):
    user_id: str = Field(description="Unique identifier for the user")
    email: str = Field(description="User's email address")
    hashed_password: str = Field(description="User's hashed password")
    role: str = Field(description="User's role")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the user was created",
    )
    last_login: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the user last logged in",
    )
    mock_progress: List[MockProgress] = Field(
        default_factory=list, description="List of mock progress for the user"
    )
    station_progress: List[StationProgress] = Field(
        default_factory=list, description="List of station progress for the user"
    )
    flagged_stations: List[FlaggedStation] = Field(
        default_factory=list, description="List of flagged stations for the user"
    )
    has_paid: bool = Field(description="Whether the user has paid for the service")
    is_currently_logged_in: Optional[bool] = Field(description="Whether the user is currently logged in")
 

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "john@example.com",
                "hashed_password": "hashed_password_example",
                "role": "user",
                "created_at": "2023-10-01T12:00:00Z",
                "last_login": "2023-10-01T12:00:00Z",
                "mock_progress": [
                    {"station_id": "station_1", "mock_id": "mock_1", "completed": True}
                ],
                "flagged_stations": [
                    {"station_id": "station_1", "mock_id": "mock_1", "flagged": True}
                ],  
                "station_progress": [
                    {"station_id": "station_1", "completed": True}
                ],
                "has_paid": True,
                "is_currently_logged_in": True,
              
            }
        }
