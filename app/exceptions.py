from fastapi import HTTPException, status


class BookingException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"


class IncorrectEmailOrPasswordException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверная почта или пароль"


class TokenExpiredException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен истек"


class TokenAbsentException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class IncorrectTokenFormatException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена"


class UserIsNotPresentException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED


class RoomCannotBeBooked(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Не осталось свободных номеров"


class NotFoundException(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Не найдено бронирование"


class HotelException(HTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class HotelNotFoundException(HotelException):
    detail = "Не найден отель с такими параметрами"


class RoomNotFoundException(HotelException):
    detail = "Не найдено комнат с данным id"


class IncorrectDatesException(HotelException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Дата заезда должна быть раньше, чем дата выезда"


class BigDateIntervalException(HotelException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Слишком большой срок бронирования"
