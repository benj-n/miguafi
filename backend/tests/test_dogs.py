from fastapi.testclient import TestClient
from app.main import create_app


def get_client():
    app = create_app()
    return TestClient(app)


def auth_headers(client: TestClient, email: str) -> dict[str, str]:
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "pass12345",
            "dog_name": None,
            "location_lat": None,
            "location_lng": None,
        },
    )
    r = client.post("/auth/login", data={"username": email, "password": "pass12345"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_list_update_delete_dog_and_photo(tmp_path):
    client = get_client()
    headers = auth_headers(client, "dogowner@example.com")

    # Create a dog
    r = client.post("/dogs/", json={"name": "BUDDY21"}, headers=headers)
    assert r.status_code == 200, r.text
    dog = r.json()
    dog_id = dog["id"]

    # List my dogs
    r = client.get("/dogs/me", headers=headers)
    assert r.status_code == 200
    items = r.json()
    assert any(d["id"] == dog_id for d in items)

    # Update name
    r = client.put(f"/dogs/{dog_id}", json={"name": "BUDDY22"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "BUDDY22"

    # Upload a photo (local storage mounted under /static/uploads)
    # Create a tiny bytes payload
    payload = b"\x89PNG\r\n\x1a\n" + b"0" * 32
    files = {"file": ("photo.png", payload, "image/png")}
    r = client.post(f"/dogs/{dog_id}/photo", files=files, headers=headers)
    assert r.status_code == 200, r.text
    photo_url = r.json()["photo_url"]
    assert photo_url is not None
    assert "/static/uploads/" in photo_url or photo_url.startswith("s3://") or photo_url.startswith("http")

    # Delete
    r = client.delete(f"/dogs/{dog_id}", headers=headers)
    assert r.status_code == 204


def test_coowner_and_permissions():
    client = get_client()
    # Owner A
    headers_a = auth_headers(client, "a@example.com")
    # Co-owner B
    headers_b = auth_headers(client, "b@example.com")

    # Create by A
    r = client.post("/dogs/", json={"name": "ROXY99"}, headers=headers_a)
    assert r.status_code == 200
    dog = r.json()
    dog_id = dog["id"]

    # Get B's user id
    me_b = client.get("/users/me", headers=headers_b).json()
    b_id = me_b["id"]

    # Add co-owner B
    r = client.post(f"/dogs/{dog_id}/coowners/{b_id}", headers=headers_a)
    assert r.status_code == 200

    # B sees the dog in list
    r = client.get("/dogs/me", headers=headers_b)
    assert any(d["id"] == dog_id for d in r.json())

    # B cannot update or delete (not primary owner by our rule - only owners can manage; here we set co-owner as owner = True)
    # Our API sets is_owner=True for co-owners as well; still should forbid non-owners? For strictness, only original owner can manage co-owners
    # But update/delete dog allowed for any owner; test ensures non-linked user cannot manage
    headers_c = auth_headers(client, "c@example.com")
    r = client.put(f"/dogs/{dog_id}", json={"name": "HACK00"}, headers=headers_c)
    assert r.status_code == 403
    r = client.delete(f"/dogs/{dog_id}", headers=headers_c)
    assert r.status_code == 403

    # Remove co-owner B
    r = client.delete(f"/dogs/{dog_id}/coowners/{b_id}", headers=headers_a)
    assert r.status_code == 200

    # B no longer sees the dog
    r = client.get("/dogs/me", headers=headers_b)
    assert all(d["id"] != dog_id for d in r.json())


def test_upload_photo_with_s3_mock(monkeypatch):
    # Patch storage.get_storage to return a fake that yields deterministic URL
    from app.services import storage as storage_mod

    class FakeS3(storage_mod.StorageService):
        def save(self, fileobj, filename, content_type=None) -> str:
            return "http://minio/miguafi/dogs/fake-key.png"

    monkeypatch.setattr(storage_mod, "get_storage", lambda: FakeS3())

    client = get_client()
    headers = auth_headers(client, "s3user@example.com")
    # Create dog
    r = client.post("/dogs/", json={"name": "S3DOG42"}, headers=headers)
    assert r.status_code == 200
    dog_id = r.json()["id"]

    payload = b"\x89PNG\r\n\x1a\n" + b"0" * 32
    files = {"file": ("photo.png", payload, "image/png")}
    r = client.post(f"/dogs/{dog_id}/photo", files=files, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["photo_url"] == "http://minio/miguafi/dogs/fake-key.png"
