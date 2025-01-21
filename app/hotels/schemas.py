from typing import List, Optional
from pydantic import field_validator
from pydantic import BaseModel


class SHotels(BaseModel):
    id: int
    name: str
    location: str
    services: List[str]
    rooms_quantity: int
    image_id: Optional[int]


class SHotelsWithRooms(SHotels):
    rooms_left: int


class SHotelsWithoutRooms(SHotels):
    pass


class SHotelsImport(BaseModel):
    name: str
    location: str
    services: List[str]
    rooms_quantity: int

    @field_validator("rooms_quantity")
    def check_rooms_quantity(cls, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Количество комнат должно быть целым числом больше нуля")
        return value
