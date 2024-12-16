
from app.bookings.dao import BookingDAO
from datetime import datetime


async def test_CRUD_booking():
    new_booking = await BookingDAO.add(
        user_id=2,
        room_id=2,
        date_from=datetime.strptime("2023-02-03", "%Y-%m-%d"),
        date_to=datetime.strptime("2023-05-24", "%Y-%m-%d")
    )

    assert new_booking.user_id == 2
    assert new_booking.room_id == 2

    get_new_booking = await BookingDAO.find_by_id(new_booking.id)
    assert get_new_booking
    assert get_new_booking.room_id == new_booking.room_id

    delete_booking = await BookingDAO.delete(user_id=2, booking_id=new_booking.id)
    assert delete_booking

    find_booking = await BookingDAO.find_one_or_none(id=new_booking.id)
    assert find_booking is None
