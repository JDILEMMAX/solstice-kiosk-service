import pytest
from fastapi.testclient import TestClient
import os
import sys

# Add parent directory to path to allow absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.main import app
from data.seed import seed_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    seed_db()
    from backend.queue_manager import print_queue
    print_queue._queue = None
    yield

def test_first_time_checkin():
    response = client.post("/api/checkin", json={"qr_code": "QR-ALICE-101"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PENDING_PRINT"
    assert data["badge_printed"] == False
    assert data["attendee"]["status"] == "PENDING_PRINT"

def test_duplicate_scan_rejection():
    response = client.post("/api/checkin", json={"qr_code": "QR-BOB-202"})
    assert response.status_code == 400
    assert "Duplicate Scan Error" in response.json()["detail"]

def test_invalid_qr_code():
    response = client.post("/api/checkin", json={"qr_code": "QR-INVALID-999"})
    assert response.status_code == 404
