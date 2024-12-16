# data access object / service.py / repo.py
from datetime import date
from sqlalchemy import and_, delete, func, insert, select, update

from app.bookings.schemas import SBookingWithRoomDetails
from app.dao.base import BaseDAO
from app.bookings.models import Bookings
from app.exceptions import RoomCannotBeBooked
from app.hotels.rooms.models import Rooms
from app.database import async_session_maker
from app.hotels.rooms.schemas import SBooking_Rooms


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date
    ):
        async with async_session_maker() as session:
            booked_rooms = select(
                Bookings.room_id, func.count(Bookings.id).label("booked_count")
                    ).where(
                        and_(
                            Bookings.date_from <= date_to,
                            Bookings.date_to >= date_from,
                            Bookings.room_id == room_id
                        )
                ).group_by(Bookings.room_id).cte("booked_rooms")
            query = (
                select(
                    Rooms.quantity - booked_rooms.c.booked_count
                )
                .select_from(Rooms)
                .join(booked_rooms, Rooms.id == booked_rooms.c.room_id, isouter=True)
                .filter(Rooms.id == room_id)
            )

            rooms_left = await session.execute(query)
            rooms_left = rooms_left.scalar()
            print(rooms_left)

            if rooms_left == 0:
                raise RoomCannotBeBooked

            if not rooms_left or rooms_left > 0:
                get_price = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(get_price)
                price: int = price.scalar()
                add_booking = insert(Bookings).values(
                    room_id=room_id,
                    user_id=user_id,
                    date_from=date_from,
                    date_to=date_to,
                    price=price,
                ).returning(Bookings)

                new_booking = await session.execute(add_booking)
                await session.commit()
                return new_booking.scalar()
            else:
                return None

    @classmethod
    async def delete(cls, user_id: int, booking_id: int):
        async with async_session_maker() as session:
            # Проверка принадлежности брони пользователю
            query = select(Bookings).where(
                Bookings.id == booking_id,
                Bookings.user_id == user_id
            )
            result = await session.execute(query)
            booking = result.scalar_one_or_none()
            if not booking:
                return None
            result = select(Bookings.room_id).where(Bookings.id == booking_id)
            room_id = await session.execute(result)
            room_id = room_id.scalar()
            rooms_quantity_decrease = (
                update(Rooms)
                .where(Rooms.id == room_id)
                .values(quantity=Rooms.quantity + 1)
            )
            await session.execute(rooms_quantity_decrease)
            delete_booking = delete(Bookings).where(
                    Bookings.id == booking_id,
                    Bookings.user_id == user_id
            )
            result = await session.execute(delete_booking)
            await session.commit()
            return result.rowcount

    @classmethod
    async def find_all(cls, user_id: int):
        async with async_session_maker() as session:
            query = (
                select(Bookings, Rooms)
                .join(Rooms, Rooms.id == Bookings.room_id)
                .filter(Bookings.user_id == user_id)
            )
            result = await session.execute(query)
            bookings = result.fetchall()
            bookings_with_rooms = [
                SBookingWithRoomDetails(
                    id=booking.id,
                    room_id=booking.room_id,
                    user_id=booking.user_id,
                    date_from=booking.date_from,
                    date_to=booking.date_to,
                    price=booking.price,
                    total_days=booking.total_days,
                    total_cost=booking.total_cost,
                    room_details=SBooking_Rooms(
                        name=room.name,
                        description=room.description,
                        services=room.services,
                        image_id=room.image_id
                    )
                )
                for booking, room in bookings
            ]

            return bookings_with_rooms
