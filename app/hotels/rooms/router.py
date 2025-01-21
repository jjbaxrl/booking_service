from datetime import date
from typing import List

from fastapi import UploadFile
from app.exceptions import RoomNotFoundException, NoFileUploadedException
from app.hotels.rooms.dao import RoomsDAO
from app.hotels.rooms.schemas import SRooms
from app.hotels.router import router


@router.get("/{hotel_id}/rooms")
async def get_rooms(hotel_id: int, date_from: date, date_to: date) -> List[SRooms]:
    rooms = await RoomsDAO.get_rooms_list_by_hotel(
        hotel_id=hotel_id, date_from=date_from, date_to=date_to
    )
    if not rooms:
        raise RoomNotFoundException
    return rooms


@router.post("hotels/rooms/data")
async def add_rooms_data(file: UploadFile):
    if not file:
        raise NoFileUploadedException
    await RoomsDAO.add_rooms(file)
    return {"{message}": "Комнаты успешно добавлены"}
