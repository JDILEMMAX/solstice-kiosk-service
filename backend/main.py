from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from backend.models import CheckInRequest, CheckInResponse
import backend.database as db
from backend.sync_printer_legacy import print_badge_synchronous

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/attendees")
def get_attendees():
    return db.get_all_attendees()

@app.get("/api/attendee/{qr_code}")
def get_attendee(qr_code: str):
    attendee = db.get_attendee_by_qr(qr_code)
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return attendee

@app.post("/api/checkin", response_model=CheckInResponse)
def checkin_attendee(request: CheckInRequest):
    attendee = db.get_attendee_by_qr(request.qr_code)
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
        
    if attendee["status"] == "CHECKED_IN":
        raise HTTPException(
            status_code=400, 
            detail="Duplicate Scan Error: Attendee has already checked in and badge was issued."
        )
        
    print_result = print_badge_synchronous(attendee)
    db.update_attendee_status(request.qr_code, "CHECKED_IN", print_result["job_id"])
    
    updated_attendee = db.get_attendee_by_qr(request.qr_code)
    
    return CheckInResponse(
        status="success",
        message="Checked in successfully.",
        attendee=updated_attendee,
        badge_printed=True,
        timestamp=datetime.now().isoformat()
    )
