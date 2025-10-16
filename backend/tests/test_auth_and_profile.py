from fastapi.testclient import TestClient
from app.main import create_app


def get_client():
    app = create_app()
    return TestClient(app)


def register_and_login(client: TestClient, email: str, password: str) -> str:
    r = client.post("/auth/register", json={
        "email": email,
        "password": password,
        "location_lat": 45.5,
        "location_lng": -73.6
    })
    assert r.status_code == 200, r.text

    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return token


def test_register_login_profile_flow():
    client = get_client()
    token = register_and_login(client, "alice@example.com", "password123")

    r = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    me = r.json()
    assert me["email"] == "alice@example.com"

    # Update only location fields now
    r = client.put("/users/me", json={"location_lat": 46.0}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
