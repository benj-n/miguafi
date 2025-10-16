from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import create_app


def setup_users(client: TestClient):
    def reg_login(email):
        r = client.post("/auth/register", json={"email": email, "password": "password123"})
        assert r.status_code == 200
        r = client.post("/auth/login", data={"username": email, "password": "password123"})
        return r.json()["access_token"]

    return reg_login("u1@example.com"), reg_login("u2@example.com")


def test_request_matches_offer_creates_notifications():
    app = create_app()
    client = TestClient(app)
    token1, token2 = setup_users(client)

    now = datetime.utcnow()
    offer = {"start_at": (now + timedelta(hours=1)).isoformat(), "end_at": (now + timedelta(hours=4)).isoformat()}
    req = {"start_at": (now + timedelta(hours=2)).isoformat(), "end_at": (now + timedelta(hours=3)).isoformat()}

    r = client.post("/availability/offers", json=offer, headers={"Authorization": f"Bearer {token1}"})
    assert r.status_code == 200

    r = client.post("/availability/requests", json=req, headers={"Authorization": f"Bearer {token2}"})
    assert r.status_code == 200

    # Offer owner should get a notification
    r = client.get("/notifications/me", headers={"Authorization": f"Bearer {token1}"})
    assert r.status_code == 200
    notifs = r.json()
    assert len(notifs) >= 1


def test_offer_matches_existing_request_creates_notifications():
    app = create_app()
    client = TestClient(app)
    token1, token2 = setup_users(client)

    now = datetime.utcnow()
    offer = {"start_at": (now + timedelta(hours=1)).isoformat(), "end_at": (now + timedelta(hours=4)).isoformat()}
    req = {"start_at": (now + timedelta(hours=2)).isoformat(), "end_at": (now + timedelta(hours=3)).isoformat()}

    r = client.post("/availability/requests", json=req, headers={"Authorization": f"Bearer {token2}"})
    assert r.status_code == 200

    r = client.post("/availability/offers", json=offer, headers={"Authorization": f"Bearer {token1}"})
    assert r.status_code == 200

    # Requester should get a notification
    r = client.get("/notifications/me", headers={"Authorization": f"Bearer {token2}"})
    assert r.status_code == 200
    notifs = r.json()
    assert len(notifs) >= 1
