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


def test_delete_offer_and_request_with_ownership():
    app = create_app()
    client = TestClient(app)
    t1 = reg_login(client, "owner@example.com")
    t2 = reg_login(client, "other@example.com")

    now = datetime.utcnow()
    offer = {"start_at": (now + timedelta(hours=1)).isoformat(), "end_at": (now + timedelta(hours=2)).isoformat()}
    req = {"start_at": (now + timedelta(hours=3)).isoformat(), "end_at": (now + timedelta(hours=4)).isoformat()}

    r = client.post("/availability/offers", json=offer, headers=auth_hdr(t1))
    assert r.status_code == 200, r.text
    offer_id = r.json()["id"]

    r = client.post("/availability/requests", json=req, headers=auth_hdr(t1))
    assert r.status_code == 200, r.text
    req_id = r.json()["id"]

    # Other user cannot delete
    r = client.delete(f"/availability/offers/{offer_id}", headers=auth_hdr(t2))
    assert r.status_code == 404
    r = client.delete(f"/availability/requests/{req_id}", headers=auth_hdr(t2))
    assert r.status_code == 404

    # Owner can delete
    r = client.delete(f"/availability/offers/{offer_id}", headers=auth_hdr(t1))
    assert r.status_code == 204
    r = client.delete(f"/availability/requests/{req_id}", headers=auth_hdr(t1))
    assert r.status_code == 204

    # Lists should be empty
    r = client.get("/availability/offers/mine", headers=auth_hdr(t1))
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    r = client.get("/availability/requests/mine", headers=auth_hdr(t1))
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0


def test_validation_invalid_and_overlapping_and_past():
    app = create_app()
    client = TestClient(app)
    t1 = reg_login(client, "val@example.com")

    now = datetime.utcnow()

    # invalid: end <= start
    bad = {"start_at": (now + timedelta(hours=2)).isoformat(), "end_at": (now + timedelta(hours=1)).isoformat()}
    r = client.post("/availability/offers", json=bad, headers=auth_hdr(t1))
    assert r.status_code == 400
    r = client.post("/availability/requests", json=bad, headers=auth_hdr(t1))
    assert r.status_code == 400

    # past: any part in past is rejected
    past = {"start_at": (now - timedelta(hours=2)).isoformat(), "end_at": (now - timedelta(hours=1)).isoformat()}
    r = client.post("/availability/offers", json=past, headers=auth_hdr(t1))
    assert r.status_code == 400
    r = client.post("/availability/requests", json=past, headers=auth_hdr(t1))
    assert r.status_code == 400

    # ok slot
    a = {"start_at": (now + timedelta(hours=1)).isoformat(), "end_at": (now + timedelta(hours=2)).isoformat()}
    r = client.post("/availability/offers", json=a, headers=auth_hdr(t1))
    assert r.status_code == 200
    # overlapping with 'a'
    a2 = {"start_at": (now + timedelta(hours=1, minutes=30)).isoformat(), "end_at": (now + timedelta(hours=2, minutes=30)).isoformat()}
    r = client.post("/availability/offers", json=a2, headers=auth_hdr(t1))
    assert r.status_code == 400

    # same for requests
    r = client.post("/availability/requests", json=a, headers=auth_hdr(t1))
    assert r.status_code == 200
    r = client.post("/availability/requests", json=a2, headers=auth_hdr(t1))
    assert r.status_code == 400
