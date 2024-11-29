from sqlalchemy import JSON, Integer, String
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Hotels(Base):
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    services: Mapped[dict] = mapped_column(JSON)
    rooms_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    image_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
