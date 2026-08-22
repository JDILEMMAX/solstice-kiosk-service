import pytest
from fastapi.testclient import TestClient
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.main import app
from data.seed import seed_db
import backend.database as db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    seed_db()
    from backend.queue_manager import print_queue
    print_queue._queue = None
    yield

def test_first_time_checkin_enqueues_job():
    with TestClient(app) as client:
        response = client.post("/api/checkin", json={"qr_code": "QR-ALICE-101"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PENDING_PRINT"
        assert data["badge_printed"] == False
        assert data["attendee"]["status"] == "PENDING_PRINT"

def test_webhook_callback_promotes_status():
    with TestClient(app) as client:
        client.post("/api/checkin", json={"qr_code": "QR-ALICE-101"})
        
        attendee = db.get_attendee_by_qr("QR-ALICE-101")
        job_id = attendee["print_job_id"]
        
        webhook_payload = {
            "job_id": job_id,
            "qr_code": "QR-ALICE-101",
            "status": "completed",
            "printed_at": "2026-08-22T10:00:00"
        }
        webhook_res = client.post("/api/webhooks/printer", json=webhook_payload)
        assert webhook_res.status_code == 200
        assert webhook_res.json()["status"] == "success"
        
        final_attendee = db.get_attendee_by_qr("QR-ALICE-101")
        assert final_attendee["status"] == "CHECKED_IN"

def test_duplicate_scan_rejection():
    with TestClient(app) as client:
        response_bob = client.post("/api/checkin", json={"qr_code": "QR-BOB-202"})
        assert response_bob.status_code == 400
        
        client.post("/api/checkin", json={"qr_code": "QR-ALICE-101"})
        response_alice = client.post("/api/checkin", json={"qr_code": "QR-ALICE-101"})
        assert response_alice.status_code == 400
