from pydantic import BaseModel
from typing import List

class BookingModel(BaseModel):
    booking_id: str
    mock_id: str
    mock_name: str
    booking_datetime: str
    booked_users: List[str]
    max_users: int



