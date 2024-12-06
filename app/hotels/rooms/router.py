from datetime import date
from typing import List
from app.exceptions import RoomNotFoundException
from app.hotels.rooms.dao import RoomsDAO
from app.hotels.rooms.schemas import SRooms
from app.hotels.router import router


@router.get("/{hotel_id}/rooms")
async def get_rooms(hotel_id: int, date_from: date, date_to: date) -> List[SRooms]:
    rooms = await RoomsDAO.get_rooms_list_by_hotel(hotel_id=hotel_id, date_from=date_from, date_to=date_to)  # noqa F401
    if not rooms:
        raise RoomNotFoundException
    return rooms
