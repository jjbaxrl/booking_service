from datetime import date
from fastapi import APIRouter, Depends

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.exceptions import NotFoundException, RoomCannotBeBooked

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирование"]
)


@router.get("", response_model=list[SBooking])
async def get_bookings(user: Users = Depends(get_current_user)):
    return await BookingDAO.find_all(user_id=user.id)


@router.post("")
async def add_booking(
    room_id: int, date_from: date, date_to: date,
    user: Users = Depends(get_current_user)
):
    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBooked


@router.delete("/{booking_id}")
async def delete_booking(booking_id: int, user: Users = Depends(get_current_user)):
    booking_delete = await BookingDAO.delete(user_id=user.id, booking_id=booking_id)
    if not booking_delete:
        raise NotFoundException
