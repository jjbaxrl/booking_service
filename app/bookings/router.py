from datetime import date
from fastapi import APIRouter, Depends
from pydantic import TypeAdapter

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBookingWithoutRoomsDetails
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.exceptions import NotFoundException
from fastapi import BackgroundTasks

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирование"]
)


@router.get("", response_model=list[SBookingWithoutRoomsDetails])
async def get_bookings(user: Users = Depends(get_current_user)):
    bookings = await BookingDAO.find_all(user_id=user.id)
    if not bookings:
        raise NotFoundException
    return bookings


@router.post("")
async def add_booking(
    background_tasks: BackgroundTasks,
    room_id: int, date_from: date, date_to: date,
    user: Users = Depends(get_current_user)
):
    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)

    # Преобразуем объект Booking в словарь, исключая служебные атрибуты SQLAlchemy
    booking_dict = {k: v for k, v in booking.__dict__.items() if not k.startswith('_')}

    # Создаем TypeAdapter для SBooking и провалидаем данные
    validated_booking_dict = TypeAdapter(SBookingWithoutRoomsDetails).validate_python(booking_dict).model_dump()  # noqa

    # Celery
    send_booking_confirmation_email.delay(booking_dict, user.email)

    # Background tasks
    # background_tasks.add_task(send_booking_confirmation_email, booking_dict, user.email)

    return validated_booking_dict


@router.delete("/{booking_id}")
async def delete_booking(booking_id: int, user: Users = Depends(get_current_user)):
    booking_delete = await BookingDAO.delete(user_id=user.id, booking_id=booking_id)
    if not booking_delete:
        raise NotFoundException
