import csv
from datetime import date
import io
from json import loads
from typing import List

from fastapi import UploadFile
from pydantic import ValidationError
from sqlalchemy import String, and_, func, insert, select

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.dependencies import convert_services_to_list
from app.hotels.rooms.models import Rooms
from app.hotels.rooms.schemas import SRoomsImport


class RoomsDAO(BaseDAO):
    model = Rooms

    @staticmethod
    async def get_booked_count_by_hotel(
        date_from: date, date_to: date, hotel_ids: List[int]
    ):
        async with async_session_maker() as session:
            booked_rooms = (
                select(Bookings.room_id, func.count(Bookings.id).label("booked_count"))
                .where(
                    and_(
                        Bookings.date_from <= date_to,
                        Bookings.date_to >= date_from,
                        Bookings.room_id.in_(
                            select(Rooms.id).where(Rooms.hotel_id.in_(hotel_ids))
                        ),
                    )
                )
                .group_by(Bookings.room_id)
                .cte("booked_rooms")
            )
            hotels_and_rooms = (select(
                    Rooms.hotel_id,
                    Rooms.id.label("room_id"),
                    func.coalesce(
                        func.sum(booked_rooms.c.booked_count), 0
                    ).label("booked_count"),
                ).select_from(Rooms)
                .outerjoin(booked_rooms, booked_rooms.c.room_id == Rooms.id)
                .group_by(Rooms.hotel_id, Rooms.id)
            ).cte("hotels_and_rooms")
            query = select(
                hotels_and_rooms.c.hotel_id.label("hotel_id"),
                func.sum(hotels_and_rooms.c.booked_count).label("total_booked"),
            ).group_by(hotels_and_rooms.c.hotel_id)

            result = await session.execute(query)
            rooms = result.fetchall()

            return [
                {"hotel_id": room.hotel_id, "rooms_booked": room.total_booked}
                for room in rooms
            ]

    @staticmethod
    async def get_rooms_list_by_hotel(hotel_id: int, date_from: date, date_to: date):
        async with async_session_maker() as session:
            booked_rooms = (
                select(Bookings.room_id, func.count(Bookings.id).label("booked_count"))
                .where(
                    and_(Bookings.date_from <= date_to, Bookings.date_to >= date_from)
                )
                .group_by(Bookings.room_id)
                .cte("booked_rooms")
            )
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
                    (
                        Rooms.quantity - func.coalesce(booked_rooms.c.booked_count, 0)
                    ).label("rooms_left"),
                )
                .select_from(Rooms)
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

    @classmethod
    async def add_rooms(cls, file: UploadFile):
        contents = await file.read()
        file_obj = io.StringIO(contents.decode('utf-8'))
        reader = list(csv.DictReader(file_obj))
        if not reader:
            print("Ошибка: CSV-файл не содержит заголовков.")
            return None
        print(f"Количество строк в csv-файле: {sum(1 for _ in reader)}")
        for i, room in enumerate(reader):
            if i == 5:
                break
            print(f"Строка {i+1}: {room}")
        async with async_session_maker() as session:
            for room in reader:
                try:
                    try:
                        # hotel_id,name,description,price,quantity,services,image_id
                        room['services'] = convert_services_to_list(room['services'])
                        valid_room = SRoomsImport.model_validate(room)
                        print(f"Проверены данные для комнаты {valid_room.name}")
                    except ValidationError as e:
                        print(f"Ошибка валидации для комнаты {room}: {e}")
                    query = insert(Rooms).values(
                        hotel_id=valid_room.hotel_id,
                        name=valid_room.name,
                        description=valid_room.description,
                        price=valid_room.price,
                        quantity=valid_room.quantity,
                        services=valid_room.services,
                        image_id=valid_room.image_id
                    )
                    await session.execute(query)
                    print(f"Добавлена комната {valid_room.name}")

                except ValidationError as e:
                    print(f"Некорретные данные для комнаты {room['name']}: {e}")
            await session.commit()
