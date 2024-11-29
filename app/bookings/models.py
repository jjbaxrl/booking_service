from sqlalchemy import Integer, ForeignKey, Date, Computed
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from datetime import date


class Bookings(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    total_cost: Mapped[int] = mapped_column(
        Integer,
        Computed("(date_to - date_from) * price"),  # Явное количество дней
        nullable=False
    )
    total_days: Mapped[int] = mapped_column(
        Integer,
        Computed("date_to - date_from"),  # Преобразование в количество дней
        nullable=False
    )
