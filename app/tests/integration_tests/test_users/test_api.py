from httpx import AsyncClient
import pytest


@pytest.mark.parametrize("email, password, status_code", [
    ("kot@pes.com", "kotopes", 200),
    ("kot@pes.com", "kot0pes", 409),
    ("neemail", "pass", 422),

])
async def test_register_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post("/auth/register", json={
        "email": email,
        "password": password
    })

    assert response.status_code == status_code


@pytest.mark.parametrize("email, password, status_code", [
    ("user@example.com", "string", 200),
    ("bij@example.com", "pass", 200),
    ("wrong@exy.com", "passsss", 401)
])
async def test_login_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post("auth/login", json={
        "email": email,
        "password": password,
    })

    assert response.status_code == status_code
