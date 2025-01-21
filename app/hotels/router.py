from datetime import date, datetime, timedelta
from typing import List
from fastapi import APIRouter, Path, Query, UploadFile
from fastapi_cache.decorator import cache

from app.exceptions import (
    BigDateIntervalException,
    HotelNotFoundException,
    IncorrectDatesException,
    NoFileUploadedException
)
from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotelsWithRooms, SHotelsWithoutRooms

router = APIRouter(prefix="/hotels", tags=["Отели"])


@cache(expire=30)
@router.get("/{location}", name="get_hotels_by_location")
async def get_hotels(
    location: str = Path(..., description="Например, Алтай"),
    date_from: date = Query(..., description=f"Например, {datetime.now().date()}"),
    date_to: date = Query(..., description=f"Например, {datetime.now().date()}"),
) -> List[SHotelsWithRooms]:
    if date_to <= date_from:
        raise IncorrectDatesException
    if date_to - date_from > timedelta(days=30):
        raise BigDateIntervalException
    return await HotelDAO.find_by_loc(
        location=location, date_from=date_from, date_to=date_to
    )


@router.get("/id/{hotel_id}", name="get_certain_hotel_by_id")
async def get_certain_hotel(hotel_id: int) -> SHotelsWithoutRooms:
    hotel = await HotelDAO.find_by_id(hotel_id)
    if not hotel:
        raise HotelNotFoundException
    return hotel


@router.post("/data")
async def add_hotels_data(file: UploadFile):
    if not file:
        raise NoFileUploadedException
    await HotelDAO.add_hotels(file)
    return {"{message}": "Hotels added successfully"}
