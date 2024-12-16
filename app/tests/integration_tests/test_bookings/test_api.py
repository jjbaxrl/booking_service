from datetime import date, datetime
from httpx import AsyncClient
import pytest


@pytest.mark.parametrize("room_id, date_from, date_to, booked_rooms, status_code", [
    (4, "2030-05-01", "2030-05-15", 3, 200),
    (4, "2030-05-01", "2030-05-15", 4, 200),
    (4, "2030-05-01", "2030-05-15", 5, 200),
    (4, "2030-05-01", "2030-05-15", 6, 200),
    (4, "2030-05-01", "2030-05-15", 7, 200),
    (4, "2030-05-01", "2030-05-15", 8, 200),
    (4, "2030-05-01", "2030-05-15", 9, 200),
    (4, "2030-05-01", "2030-05-15", 10, 200),
    (4, "2030-05-01", "2030-05-15", 10, 409),
    (4, "2030-05-01", "2030-05-15", 10, 409),
])
async def test_add_and_get_booking(room_id: int, date_from: date, date_to: date,
                                   status_code: int, booked_rooms: int,
                                   authenticated_ac: AsyncClient):
    response = await authenticated_ac.post("/bookings", params={
        "room_id": room_id,
        "date_from": datetime.strptime(date_from, "%Y-%m-%d"),
        "date_to": datetime.strptime(date_to, "%Y-%m-%d"),
    })

    assert response.status_code == status_code

    assert response.json()

    response = await authenticated_ac.get("/bookings")

    assert len(response.json()) == booked_rooms


async def test_get_and_delete_bookings(authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/bookings")
    assert response.status_code == 200

    list_of_ids = [i["id"] for i in response.json()]
    for id in list_of_ids:
        response = await authenticated_ac.delete(f"bookings/{id}")
        assert response.status_code == 200

    response = await authenticated_ac.get("/bookings")
    assert response.status_code == 409

    response = await authenticated_ac.delete(f"bookings/{1}")
    assert response.status_code == 409
