# test_main.py
from fastapi.testclient import TestClient
from music_api import app

client = TestClient(app)

def test_signup_and_login():
    # 1️⃣ signup
    response = client.post("/signup", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200 or response.status_code == 400  # user may exist

    # 2️⃣ login
    response = client.post("/login", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

    # 3️⃣ get /me
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_create_artist():
    # signup/login to get token
    client.post("/signup", json={"username": "artistuser", "password": "pass123"})
    login = client.post("/login", data={"username": "artistuser", "password": "pass123"})
    token = login.json()["access_token"]

    # create artist with token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/artists", json={"name": "Test Artist"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Artist"

