
from json import loads
from sqlalchemy import String, func, select

from app.dao.base import BaseDAO
from app.exceptions import HotelNotFoundException
from app.hotels.models import Hotels
from app.hotels.rooms.dao import RoomsDAO
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all(cls, location: str, date_from: str, date_to: str):
        async with async_session_maker() as session:
            query = (
                    select(
                        Hotels.id,
                        Hotels.name,
                        Hotels.location,
                        Hotels.services.cast(String),
                        Hotels.rooms_quantity,
                        Hotels.image_id,
                        func.count(Rooms.id).label("rooms_quantity")
                    )
                    .join(Rooms, Rooms.hotel_id == Hotels.id)
                    .where(Hotels.location.like(f'%{location}%'))
                    .group_by(
                        Hotels.id,
                        Hotels.name,
                        Hotels.location,
                        Hotels.services.cast(String),
                        Hotels.rooms_quantity,
                        Hotels.image_id
                    )
            )
            result = await session.execute(query)
            hotels = result.mappings().all()

            if not hotels:
                raise HotelNotFoundException

            # Преобразуем RowMapping в dict
            hotels = [dict(hotel) for hotel in hotels]

            # Преобразуем services из строки в список
            for hotel in hotels:
                hotel["services"] = loads(hotel["services"])

            hotel_ids = [hotel["id"] for hotel in hotels]

            rooms_left_data = await RoomsDAO.get_rooms_left_by_hotels(
                hotel_ids=hotel_ids,
                date_from=date_from,
                date_to=date_to
            )
            print(rooms_left_data)
            rooms_left_by_hotel = {}

            # Считаем количество свободных комнат для каждого отеля
            for room in rooms_left_data:
                hotel_id = room["hotel_id"]
                if hotel_id not in rooms_left_by_hotel:
                    rooms_left_by_hotel[hotel_id] = 0
                if room["rooms_left"] > 0:
                    rooms_left_by_hotel[hotel_id] += 1  # Cчетчик свободных комнат

            # Фильтрация и добавление данных о количестве свободных комнат
            hotels_with_rooms_left = []
            for hotel in hotels:
                hotel_id = hotel["id"]
                rooms_left = hotel["rooms_quantity"] - rooms_left_by_hotel.get(hotel_id, 0)
                if rooms_left > 0:  # Добавляем отель только если есть свободные комнаты
                    hotels_with_rooms_left.append({
                        **hotel,
                        "rooms_left": rooms_left
                    })

            return hotels_with_rooms_left
