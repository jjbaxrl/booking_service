
from json import loads
from sqlalchemy import String, select

from app.dao.base import BaseDAO
from app.exceptions import HotelNotFoundException
from app.hotels.models import Hotels
from app.hotels.rooms.dao import RoomsDAO
from app.database import async_session_maker


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
                        )
                    .where(Hotels.location.like(f'%{location}%'))
            )
            result = await session.execute(query)
            hotels = result.mappings().all()

            if not hotels:
                raise HotelNotFoundException

            # Преобразуем RowMapping в dict
            hotels_dict = [dict(hotel) for hotel in hotels]

            # Преобразуем services из строки в список
            for hotel in hotels_dict:
                hotel["services"] = loads(hotel["services"])

            hotel_ids = [hotel["id"] for hotel in hotels_dict]

            rooms_left_data = await RoomsDAO.get_booked_count_by_hotel(
                hotel_ids=hotel_ids,
                date_from=date_from,
                date_to=date_to
            )

            # Преобразуем rooms_left_data в словарь для быстрого доступа по hotel_id
            rooms_left_dict = {room["hotel_id"]: int(room["rooms_booked"]) for room in rooms_left_data}  # noqa F401

            # Добавляем данные о rooms_left к каждому отелю
            for hotel in hotels_dict:
                hotel_id = hotel["id"]
                hotel["rooms_left"] = int(hotel["rooms_quantity"]) - rooms_left_dict.get(hotel_id, hotel["rooms_quantity"])  # noqa F401

            hotels_dict = [hotel for hotel in hotels_dict if hotel["rooms_left"] != 0]
            return hotels_dict
