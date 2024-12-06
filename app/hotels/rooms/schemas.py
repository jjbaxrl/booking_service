from typing import List, Optional
from pydantic import BaseModel


class SRooms(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: str
    services: Optional[List[str]]
    price: int
    quantity: int
    image_id: Optional[int]
    total_cost: int
    rooms_left: int

    class Config:
        orm_mode = True


class SBooking_Rooms(BaseModel):
    name: str
    description: str
    services: List[str]
    image_id: int

    class Config:
        orm_mode = True
