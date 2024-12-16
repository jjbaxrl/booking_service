from datetime import date
from pydantic import BaseModel, ConfigDict

from app.hotels.rooms.schemas import SBooking_Rooms


class SBooking(BaseModel):
    id: int
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_days: int
    total_cost: int

    model_config = ConfigDict(env_file=".env")


class SBookingWithoutRoomsDetails(SBooking):
    pass


class SBookingWithRoomDetails(SBooking):
    room_details: SBooking_Rooms
