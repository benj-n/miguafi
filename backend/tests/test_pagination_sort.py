from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import create_app


def reg_login(client: TestClient, email: str) -> str:
    r = client.post("/auth/register", json={"email": email, "password": "password123"})
    assert r.status_code == 200
    r = client.post("/auth/login", data={"username": email, "password": "password123"})
    assert r.status_code == 200
    return r.json()["access_token"]


def auth_hdr(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_offers_pagination_and_sort():
    app = create_app()
    client = TestClient(app)
    token = reg_login(client, "pager@example.com")

    now = datetime.utcnow()
    # Create 5 offers spaced by 1 hour
    for i in range(5):
        start = now + timedelta(hours=1 + i)
        end = start + timedelta(hours=1)
        r = client.post("/availability/offers", json={"start_at": start.isoformat(), "end_at": end.isoformat()}, headers=auth_hdr(token))
        assert r.status_code == 200

    # Desc sort (default): latest first
    r = client.get("/availability/offers/mine?page=1&page_size=2", headers=auth_hdr(token))
    data = r.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    first_page = data["items"]

    r = client.get("/availability/offers/mine?page=2&page_size=2", headers=auth_hdr(token))
    data2 = r.json()
    assert len(data2["items"]) == 2
    # Ensure order is descending by start_at
    assert first_page[0]["start_at"] > data2["items"][0]["start_at"]

    # Asc sort
    r = client.get("/availability/offers/mine?page=1&page_size=1&sort=start_at", headers=auth_hdr(token))
    asc_first = r.json()["items"][0]["start_at"]
    r = client.get("/availability/offers/mine?page=5&page_size=1&sort=start_at", headers=auth_hdr(token))
    asc_last = r.json()["items"][0]["start_at"]
    assert asc_first < asc_last


def test_requests_pagination_and_sort():
    app = create_app()
    client = TestClient(app)
    token = reg_login(client, "pager2@example.com")

    now = datetime.utcnow()
    # Create 3 requests spaced by 2 hours
    for i in range(3):
        start = now + timedelta(hours=2 * i + 1)
        end = start + timedelta(hours=1)
        r = client.post("/availability/requests", json={"start_at": start.isoformat(), "end_at": end.isoformat()}, headers=auth_hdr(token))
        assert r.status_code == 200

    r = client.get("/availability/requests/mine?page=1&page_size=2", headers=auth_hdr(token))
    data = r.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    # Asc
    r = client.get("/availability/requests/mine?page=1&page_size=1&sort=start_at", headers=auth_hdr(token))
    first = r.json()["items"][0]["start_at"]
    r = client.get("/availability/requests/mine?page=3&page_size=1&sort=start_at", headers=auth_hdr(token))
    last = r.json()["items"][0]["start_at"]
    assert first < last
