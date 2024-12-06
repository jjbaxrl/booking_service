from datetime import date
from json import loads
from typing import List

from app.dao.base import BaseDAO
from app.database import async_session_maker
from sqlalchemy import String, and_, func, select
from app.bookings.models import Bookings
from app.hotels.rooms.models import Rooms


class RoomsDAO(BaseDAO):
    model = Rooms

    @staticmethod
    async def get_booked_count_by_hotel(
        date_from: date,
        date_to: date,
        hotel_ids: List[int]
    ):
        async with async_session_maker() as session:
            booked_rooms = select(
                Bookings.room_id, func.count(Bookings.id).label("booked_count")
            ).where(
                and_(
                    Bookings.date_from <= date_to,
                    Bookings.date_to >= date_from,
                    Bookings.room_id.in_(
                        select(Rooms.id).where(Rooms.hotel_id.in_(hotel_ids))
                    )
                )
            ).group_by(Bookings.room_id).cte("booked_rooms")
            hotels_and_rooms = (
                select(
                    Rooms.hotel_id,
                    Rooms.id.label("room_id"),
                    func.coalesce(func.sum(booked_rooms.c.booked_count), 0).label("booked_count"),
                )
                .select_from(Rooms)
                .outerjoin(booked_rooms, booked_rooms.c.room_id == Rooms.id)
                .group_by(Rooms.hotel_id, Rooms.id)
            ).cte("hotels_and_rooms")
            query = (
                select(
                    hotels_and_rooms.c.hotel_id.label("hotel_id"),
                    func.sum(hotels_and_rooms.c.booked_count).label("total_booked")
                )
                .group_by(hotels_and_rooms.c.hotel_id)
            )

            result = await session.execute(query)
            rooms = result.fetchall()

            return [
                {
                    "hotel_id": room.hotel_id,
                    "rooms_booked": room.total_booked
                }
                for room in rooms
            ]

    @staticmethod
    async def get_rooms_list_by_hotel(hotel_id: int, date_from: date, date_to: date):
        async with async_session_maker() as session:
            booked_rooms = select(
                Bookings.room_id, func.count(Bookings.id).label("booked_count")
            ).where(
                and_(
                    Bookings.date_from <= date_to,
                    Bookings.date_to >= date_from
                    )
                ).group_by(Bookings.room_id).cte("booked_rooms")
            query = (
                select(
                    Rooms.id,
                    Rooms.hotel_id,
                    Rooms.name,
                    Rooms.description,
                    Rooms.services.cast(String),
                    Rooms.price,
                    Rooms.quantity,
                    Rooms.image_id,
                    (Rooms.quantity * (date_to - date_from).days).label("total_cost"),
                    (Rooms.quantity - func.coalesce(booked_rooms.c.booked_count, 0)).label("rooms_left")  # noqa F401
                ).select_from(Rooms)
                .outerjoin(booked_rooms, Rooms.id == booked_rooms.c.room_id)
                .where(Rooms.hotel_id == hotel_id)
            )

            result = await session.execute(query)
            rooms = result.mappings().all()

            rooms_dict = [dict(room) for room in rooms]
            # Преобразуем services из строки в список
            for room in rooms_dict:
                room["services"] = loads(room["services"])

            return rooms_dict
