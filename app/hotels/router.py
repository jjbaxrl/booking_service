from datetime import date
from typing import List
from fastapi import APIRouter

from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotels

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"]
)


@router.get("/{location}")
async def get_hotels(location: str, date_from: date, date_to: date) -> List[SHotels]:
    return await HotelDAO.find_all(location=location, date_from=date_from, date_to=date_to)
