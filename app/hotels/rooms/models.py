from sqlalchemy import Integer, String, ForeignKey, JSON, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Rooms(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    services: Mapped[list] = mapped_column(JSON)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    image_id: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        CheckConstraint("price > 0", name="check_price_positive"),
        CheckConstraint("quantity >= 0", name="check_quantity_nonnegative")
    )
