import csv
from datetime import date
import io
from json import loads
from fastapi import UploadFile
from pydantic import ValidationError
from sqlalchemy import String, insert, select

from app.dao.base import BaseDAO
from app.exceptions import HotelNotFoundException
from app.hotels.models import Hotels
from app.hotels.rooms.dao import RoomsDAO
from app.database import async_session_maker
from app.hotels.schemas import SHotelsImport
from app.hotels.dependencies import convert_services_to_list


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_by_loc(cls, location: str, date_from: date, date_to: date):
        location = location.strip()
        async with async_session_maker() as session:
            query = select(
                Hotels.id,
                Hotels.name,
                Hotels.location,
                Hotels.services.cast(String),
                Hotels.rooms_quantity,
                Hotels.image_id,
            ).where(Hotels.location.like(f"%{location}%"))
            result = await session.execute(query)
            hotels = result.mappings().all()
            print("Hotels Query Result:", hotels)  # Добавьте это

            if not hotels:
                raise HotelNotFoundException

            # Преобразуем RowMapping в dict
            hotels_dict = [dict(hotel) for hotel in hotels]

            # Преобразуем services из строки в список
            for hotel in hotels_dict:
                try:
                    hotel["services"] = loads(hotel["services"])
                except Exception as e:
                    print(f"Ошибка форматирования сервисов {hotel['id']}: {e}")

            hotel_ids = [hotel["id"] for hotel in hotels_dict]

            rooms_left_data = await RoomsDAO.get_booked_count_by_hotel(
                hotel_ids=hotel_ids, date_from=date_from, date_to=date_to
            )

            # Преобразуем rooms_left_data в словарь для быстрого доступа по hotel_id
            rooms_left_dict = {
                room["hotel_id"]: int(room["rooms_booked"]) for room in rooms_left_data
            }
            print("Rooms_left_dict", rooms_left_dict)
            # Добавляем данные о rooms_left к каждому отелю
            for hotel in hotels_dict:
                print(f"Hotel ID: {hotel['id']}, Rooms quantity: {hotel['rooms_quantity']}")  # noqa
                hotel_id = hotel["id"]
                # Если отеля нет в rooms_left_dict, то у него нет забронированных комнат
                hotel["rooms_left"] = int(
                    hotel["rooms_quantity"]
                ) - rooms_left_dict.get(hotel_id, 0)

            print("Semi-Final hotels dict:", hotels_dict)
            hotels_dict = [hotel for hotel in hotels_dict if hotel["rooms_left"] != 0]
            print("Final hotels dict:", hotels_dict)
            return hotels_dict

    @classmethod
    async def add_hotels(cls, file: UploadFile):
        contents = await file.read()
        file_obj = io.StringIO(contents.decode('utf-8'))
        reader = list(csv.DictReader(file_obj))
        if not reader:
            print("Ошибка: CSV-файл не содержит заголовков.")
            return None
        print(f"Количество строк в CSV-файле: {sum(1 for _ in reader)}")
        # Выводим первые несколько строк для отладки
        for i, hotel in enumerate(reader):
            print(f"Строка {i+1}: {hotel}")
            if i == 5:
                break
        async with async_session_maker() as session:
            for hotel in reader:
                try:
                    # Проверка соответствия схемы
                    try:
                        hotel["services"] = convert_services_to_list(hotel["services"])
                        valid_hotel = SHotelsImport.model_validate(hotel)
                        print(f"Проверены данные отеля: {valid_hotel}")
                    except ValidationError as e:
                        print(f"Ошибка валидации для отеля {hotel['name']}: {e}")
                    query = insert(Hotels).values(
                        name=valid_hotel.name,
                        location=valid_hotel.location,
                        services=valid_hotel.services,
                        rooms_quantity=valid_hotel.rooms_quantity
                    )
                    await session.execute(query)
                    print(f"Отель {valid_hotel.name} успешно добавлен в базу.")

                    select_query = select(Hotels).filter(
                        Hotels.name == valid_hotel.name
                    )
                    result = await session.execute(select_query)
                    inserted_hotel = result.scalars().first()

                    if not inserted_hotel:
                        print(f"Отель {valid_hotel.name} не был вставлен в базу.")
                except ValidationError as e:
                    print(f"Некорректные данные для отеля {hotel['name']}: {e}")
            await session.commit()
