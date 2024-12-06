from datetime import date
from typing import List
from fastapi import APIRouter

from app.exceptions import HotelNotFoundException
from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotelsWithRooms, SHotelsWithoutRooms

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"]
)


@router.get("/{location}")
async def get_hotels(location: str, date_from: date, date_to: date) -> List[SHotelsWithRooms]:
    return await HotelDAO.find_all(location=location, date_from=date_from, date_to=date_to)


@router.get("/id/{hotel_id}")
async def get_certain_hotel(hotel_id: int) -> SHotelsWithoutRooms:
    hotel = await HotelDAO.find_by_id(hotel_id)
    if not hotel:
        raise HotelNotFoundException
    return hotel
