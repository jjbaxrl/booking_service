from httpx import AsyncClient
import pytest


@pytest.mark.parametrize("location, date_from, date_to, status_code", [
    ("Алтай", "2020-01-02", "2020-02-02", 400),
])
async def test_get_hotels_by_loc(location, date_from, date_to, status_code,
                                 ac: AsyncClient):
    response = await ac.get(f"/hotels/{location}", params={
        "date_from": date_from,
        "date_to": date_to
    })
    assert response.status_code == status_code
