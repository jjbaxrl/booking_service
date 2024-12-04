from typing import List
from pydantic import BaseModel


class SRooms(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: str
    price: int
    services: List[str]
    quantity: int
    image_id: int

    class Config:
        orm_mode = True


class SBooking_Rooms(BaseModel):
    name: str
    description: str
    services: List[str]
    image_id: int

    class Config:
        orm_mode = True
