from datetime import date
from pydantic import BaseModel

from app.hotels.rooms.schemas import SBooking_Rooms


class SBooking(BaseModel):
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_days: int
    total_cost: int
    room_details: SBooking_Rooms

    class Config:
        orm_mode = True
