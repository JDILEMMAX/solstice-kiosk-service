import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from backend.models import CheckInRequest, CheckInResponse, PrinterWebhookPayload
import backend.database as db
from backend.queue_manager import print_queue

@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(print_queue.worker())
    yield
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

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
async def checkin_attendee(request: CheckInRequest):
    attendee = db.get_attendee_by_qr(request.qr_code)
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
        
    if attendee["status"] in ("CHECKED_IN", "PENDING_PRINT"):
        raise HTTPException(
            status_code=400, 
            detail="Duplicate Scan Error: Attendee is already checked in or print job is currently in progress."
        )
        
    job_id = await print_queue.enqueue_job(request.qr_code, attendee["full_name"])
    db.update_attendee_status(request.qr_code, "PENDING_PRINT", job_id)
    
    updated_attendee = db.get_attendee_by_qr(request.qr_code)
    
    return CheckInResponse(
        status="PENDING_PRINT",
        message="Print job enqueued.",
        attendee=updated_attendee,
        badge_printed=False,
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/webhooks/printer")
def printer_webhook(payload: PrinterWebhookPayload):
    db.update_attendee_status(payload.qr_code, "CHECKED_IN", payload.job_id)
    return {"status": "success", "message": "Check-in finalized via printer webhook callback"}
