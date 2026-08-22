"""
DEPRECATION NOTICE:
This synchronous print driver was retired per the Day 4 pivot.
It is retained solely for architectural audit history.
"""
import time
import uuid

def print_badge_synchronous(attendee: dict) -> dict:
    """Simulates blocking HTTP calls to vendor printer API."""
    time.sleep(1.0)
    job_id = f"JOB-SYNC-{uuid.uuid4()}"
    return {"status": "success", "job_id": job_id}
