from datetime import date
from typing import List, Optional

from app.dao.base import BaseDAO
from app.database import async_session_maker
from sqlalchemy import and_, func, or_, select
from app.bookings.models import Bookings
from app.hotels.rooms.models import Rooms


class RoomsDAO(BaseDAO):
    model = Rooms

    @staticmethod
    async def _get_rooms_left(
        date_from: date,
        date_to: date,
        room_id: Optional[int] = None,
        hotel_ids: Optional[List[int]] = None
    ):
        if not room_id and not hotel_ids:
            raise ValueError("Необходимо предоставить id комнаты или отеля")

        async with async_session_maker() as session:
            # Подзапрос для бронированных комнат
            booked_rooms = (
                select(Bookings.room_id, func.count(Bookings.id).label("booked_count"))
                .where(
                    and_(
                        Bookings.date_from <= date_to,  # Пересечение с диапазоном
                        Bookings.date_to >= date_from,  # Пересечение с диапазоном
                        or_(
                            room_id is not None and Bookings.room_id == room_id,
                            hotel_ids is not None and Bookings.room_id.in_(
                                select(Rooms.id).where(Rooms.hotel_id.in_(hotel_ids))
                            ),
                        ),
                    )
                )
                .group_by(Bookings.room_id)
                .cte("booked_rooms")
            )

            # Основной запрос
            query = (
                select(
                    Rooms.hotel_id,
                    Rooms.id.label("room_id"),
                    func.sum(Rooms.quantity).label("total_rooms"),
                    func.coalesce(func.sum(booked_rooms.c.booked_count), 0).label("booked_count"),
                )
                .select_from(Rooms)
                .outerjoin(booked_rooms, booked_rooms.c.room_id == Rooms.id)
                .group_by(Rooms.hotel_id, Rooms.id, Rooms.quantity)
            )

            if room_id:
                query = query.where(Rooms.id == room_id)

            if hotel_ids:
                query = query.where(Rooms.hotel_id.in_(hotel_ids))

            result = await session.execute(query)
            rooms = result.fetchall()

            return [
                {
                    "room_id": room.room_id,
                    "hotel_id": room.hotel_id,
                    "rooms_left": room.total_rooms - room.booked_count
                }
                for room in rooms
            ]

    @staticmethod
    async def get_rooms_left_by_room(
        room_id: int,
        date_from: date,
        date_to: date
    ):
        result = await RoomsDAO._get_rooms_left(
            room_id=room_id,
            date_from=date_from,
            date_to=date_to
        )
        return result[0] if result else {"room_id": room_id, "rooms_left": 0}

    @staticmethod
    async def get_rooms_left_by_hotel(
        hotel_id: int,
        date_from: date,
        date_to: date
    ):
        return await RoomsDAO._get_rooms_left(
            hotel_ids=[hotel_id],
            date_from=date_from,
            date_to=date_to
        )

    @staticmethod
    async def get_rooms_left_by_hotels(
        hotel_ids: List[int],
        date_from: date,
        date_to: date
    ):
        return await RoomsDAO._get_rooms_left(
            hotel_ids=hotel_ids,
            date_from=date_from,
            date_to=date_to
        )
