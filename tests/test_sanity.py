from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_attendees():
    response = client.get("/api/attendees")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_single_attendee_not_found():
    response = client.get("/api/attendee/INVALID")
    assert response.status_code == 404
