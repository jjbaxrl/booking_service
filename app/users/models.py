from sqlalchemy import Integer, String, Column, ForeignKey, Date, Computed   # noqa F401
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import EmailStr
from app.database import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    @staticmethod
    def validate_email(email: str) -> EmailStr:
        return EmailStr(email)
